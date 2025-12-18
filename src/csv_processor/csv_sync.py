"""
CSV to database synchronization.

This module handles the core synchronization logic between CSV files and the database.
It implements change detection using file hashing to avoid unnecessary processing,
and row-level hashing to detect which specific books have been updated.

Key features:
- Hash-based change detection (file and row level)
- Upsert logic (insert new books, update existing ones)
- Price history tracking for price changes
- Transaction-safe database operations
- Comprehensive error handling and logging
"""

import hashlib
from typing import Dict, Tuple
import pandas as pd

from src.csv_processor.csv_watcher import CSVWatcher
from src.csv_processor.csv_parser import CSVParser
from src.storage.database import db
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CSVSync:
    """
    Synchronize CSV data to database.
    
    This class orchestrates the entire CSV-to-database sync process:
    1. Monitors CSV file for changes (via CSVWatcher)
    2. Parses and validates CSV data (via CSVParser)
    3. Performs upsert operations (insert new, update existing)
    4. Tracks price changes and maintains price history
    5. Logs all sync operations for audit trail
    """
    
    def __init__(self, csv_path: str):
        """
        Initialize CSV sync with file path.
        
        Args:
            csv_path: Path to the CSV file to monitor and sync
        """
        self.csv_path = csv_path
        self.watcher = CSVWatcher(csv_path)  # Monitors file for changes
        self.parser = CSVParser()  # Validates and parses CSV structure
        self.logger = logger
    
    def sync(self) -> Tuple[bool, Dict[str, int]]:
        """
        Synchronize CSV file to database.
        
        This is the main entry point for CSV synchronization. It:
        1. Checks if the CSV file has changed (using file hash)
        2. Parses the CSV into a DataFrame
        3. Syncs each row to the database (insert/update)
        4. Creates a sync log entry for audit purposes
        
        Returns:
            Tuple of (success, stats_dict) where stats_dict contains:
            - rows_processed: Total rows processed (including errors)
            - rows_inserted: New books inserted into database
            - rows_updated: Existing books updated in database
            
        Note:
            Returns early if CSV hasn't changed, avoiding unnecessary DB operations.
        """
        # Step 1: Check if CSV has changed using file hash comparison
        # This optimization prevents processing unchanged files
        if not self.watcher.has_changed():
            self.logger.info("CSV file unchanged, skipping sync")
            return True, {'rows_processed': 0, 'rows_inserted': 0, 'rows_updated': 0}
        
        # Step 2: Parse CSV file into pandas DataFrame
        # Parser validates structure, data types, and required columns
        df = self.parser.parse(self.csv_path)
        if df is None or df.empty:
            self.logger.error("Failed to parse CSV or CSV is empty")
            return False, {'rows_processed': 0, 'rows_inserted': 0, 'rows_updated': 0}
        
        # Step 3: Sync DataFrame rows to database
        # This performs the actual insert/update operations
        stats = self._sync_to_database(df)
        
        # Step 4: Create sync log entry for audit trail
        # This records when sync happened, what was processed, and file hash
        file_hash = self.watcher.get_file_hash()
        filename = self.watcher.csv_path.name
        db.create_sync_log(
            filename=filename,
            last_processed_hash=file_hash or '',  # Store hash to detect next change
            rows_processed=stats['rows_processed'],
            rows_inserted=stats['rows_inserted'],
            rows_updated=stats['rows_updated']
        )
        
        self.logger.info(
            f"CSV sync completed: {stats['rows_inserted']} inserted, "
            f"{stats['rows_updated']} updated, {stats['rows_processed']} total"
        )
        
        return True, stats
    
    def _sync_to_database(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Sync DataFrame rows to database using upsert logic.
        
        This method processes each row in the DataFrame and either:
        - Inserts a new book if ISBN doesn't exist
        - Updates existing book if ISBN exists and data has changed
        
        Change detection uses row-level hashing (ISBN + Price + Title) to determine
        if an update is needed, avoiding unnecessary database writes.
        
        Args:
            df: Pandas DataFrame containing book data from CSV
            
        Returns:
            Dictionary with sync statistics:
            - rows_processed: Total rows attempted (including failures)
            - rows_inserted: New books created
            - rows_updated: Existing books modified
            
        Important:
            SQLAlchemy session management: We access ORM object attributes
            (existing_price, existing_hash) immediately after fetching the book,
            while it's still attached to the session. This prevents DetachedInstanceError
            that would occur if we tried to access attributes after the session closes.
        """
        stats = {
            'rows_processed': 0,
            'rows_inserted': 0,
            'rows_updated': 0
        }
        
        # Process each row in the CSV
        for _, row in df.iterrows():
            try:
                stats['rows_processed'] += 1
                isbn = row['ISBN']  # ISBN is the unique identifier
                
                # Calculate row hash for change detection
                # Hash includes ISBN, Price, and Title to detect any meaningful changes
                row_hash = self._calculate_row_hash(row)
                
                # Check if book already exists in database
                existing_book = db.get_book_by_isbn(isbn)
                
                if existing_book is None:
                    # Case 1: New book - insert into database
                    new_book = db.create_book(
                        isbn=isbn,
                        title=row['Title'],
                        author=row['Author'],
                        packt_price=row['Packt_Price'],
                        packt_url=row['Packt_URL'],
                        csv_row_hash=row_hash  # Store hash for future change detection
                    )
                    stats['rows_inserted'] += 1
                    self.logger.debug(f"Inserted new book: {isbn}")
                    
                    # Create initial price history entry for new book
                    # This ensures we have a baseline price record
                    db.add_price_history(
                        book_id=new_book.id,
                        source='packt',
                        price=row['Packt_Price']
                    )
                else:
                    # Case 2: Existing book - check if update is needed
                    
                    # CRITICAL: Access ORM attributes while object is still attached to session
                    # If we wait until after db.update_book() or session closes, we'll get
                    # DetachedInstanceError when trying to access these attributes.
                    # This is a common SQLAlchemy pitfall - always access attributes before
                    # the session context ends or object becomes detached.
                    existing_price = existing_book.packt_price
                    existing_hash = existing_book.csv_row_hash
                    
                    # Determine if update is needed by comparing:
                    # 1. Price change (triggers price history entry)
                    # 2. Hash change (indicates any field changed: price, title, etc.)
                    price_changed = existing_price != row['Packt_Price']
                    hash_changed = existing_hash != row_hash
                    
                    if price_changed or hash_changed:
                        # Update book with new data from CSV
                        update_data = {
                            'title': row['Title'],
                            'author': row['Author'],
                            'packt_price': row['Packt_Price'],
                            'packt_url': row['Packt_URL'],
                            'csv_row_hash': row_hash  # Update hash to reflect current state
                        }
                        db.update_book(existing_book.id, **update_data)
                        stats['rows_updated'] += 1
                        self.logger.debug(f"Updated book: {isbn}")
                        
                        # Track price changes in price history table
                        # This enables price trend analysis and alert generation
                        if price_changed:
                            db.add_price_history(
                                book_id=existing_book.id,
                                source='packt',
                                price=row['Packt_Price']
                            )
                            self.logger.info(
                                f"Price changed for {isbn}: "
                                f"{existing_price} -> {row['Packt_Price']}"
                            )
                    # If neither price nor hash changed, skip update (no-op)
                
            except Exception as e:
                # Log error but continue processing remaining rows
                # This ensures one bad row doesn't stop the entire sync
                self.logger.error(f"Error syncing row for ISBN {row.get('ISBN', 'unknown')}: {e}")
                continue
        
        return stats
    
    def _calculate_row_hash(self, row: pd.Series) -> str:
        """
        Calculate SHA256 hash for a CSV row to detect changes.
        
        The hash is computed from a combination of key fields that indicate
        meaningful changes to the book record:
        - ISBN: Unique identifier (shouldn't change, but included for safety)
        - Packt_Price: Price changes are critical for price tracking
        - Title: Title changes indicate book metadata updates
        
        Args:
            row: Pandas Series representing one CSV row
            
        Returns:
            Hexadecimal SHA256 hash string (64 characters)
            
        Note:
            Using pipe (|) as delimiter to avoid collisions if field values
            contain common characters. SHA256 ensures cryptographic uniqueness.
            
        Example:
            ISBN=123, Price=29.99, Title="Python Guide" 
            -> hash("123|29.99|Python Guide")
        """
        # Combine key fields with pipe delimiter to create unique hash input
        hash_string = f"{row['ISBN']}|{row['Packt_Price']}|{row['Title']}"
        # Generate SHA256 hash and return as hexadecimal string
        return hashlib.sha256(hash_string.encode()).hexdigest()

