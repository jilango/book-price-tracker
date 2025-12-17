"""CSV to database synchronization."""

import hashlib
from typing import Dict, Tuple
import pandas as pd

from src.csv_processor.csv_watcher import CSVWatcher
from src.csv_processor.csv_parser import CSVParser
from src.storage.database import db
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CSVSync:
    """Synchronize CSV data to database."""
    
    def __init__(self, csv_path: str):
        """Initialize CSV sync."""
        self.csv_path = csv_path
        self.watcher = CSVWatcher(csv_path)
        self.parser = CSVParser()
        self.logger = logger
    
    def sync(self) -> Tuple[bool, Dict[str, int]]:
        """
        Synchronize CSV file to database.
        
        Returns:
            Tuple of (success, stats_dict) where stats_dict contains:
            - rows_processed: Total rows processed
            - rows_inserted: New books inserted
            - rows_updated: Existing books updated
        """
        # Check if CSV has changed
        if not self.watcher.has_changed():
            self.logger.info("CSV file unchanged, skipping sync")
            return True, {'rows_processed': 0, 'rows_inserted': 0, 'rows_updated': 0}
        
        # Parse CSV
        df = self.parser.parse(self.csv_path)
        if df is None or df.empty:
            self.logger.error("Failed to parse CSV or CSV is empty")
            return False, {'rows_processed': 0, 'rows_inserted': 0, 'rows_updated': 0}
        
        # Sync to database
        stats = self._sync_to_database(df)
        
        # Log sync operation
        file_hash = self.watcher.get_file_hash()
        filename = self.watcher.csv_path.name
        db.create_sync_log(
            filename=filename,
            last_processed_hash=file_hash or '',
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
        """Sync DataFrame to database."""
        stats = {
            'rows_processed': 0,
            'rows_inserted': 0,
            'rows_updated': 0
        }
        
        for _, row in df.iterrows():
            try:
                stats['rows_processed'] += 1
                isbn = row['ISBN']
                
                # Calculate row hash for change detection
                row_hash = self._calculate_row_hash(row)
                
                # Check if book exists
                existing_book = db.get_book_by_isbn(isbn)
                
                if existing_book is None:
                    # Insert new book
                    new_book = db.create_book(
                        isbn=isbn,
                        title=row['Title'],
                        author=row['Author'],
                        packt_price=row['Packt_Price'],
                        packt_url=row['Packt_URL'],
                        csv_row_hash=row_hash
                    )
                    stats['rows_inserted'] += 1
                    self.logger.debug(f"Inserted new book: {isbn}")
                    
                    # Add price history
                    db.add_price_history(
                        book_id=new_book.id,
                        source='packt',
                        price=row['Packt_Price']
                    )
                else:
                    # Access attributes while book is still attached to session
                    existing_price = existing_book.packt_price
                    existing_hash = existing_book.csv_row_hash
                    
                    # Check if price changed
                    price_changed = existing_price != row['Packt_Price']
                    hash_changed = existing_hash != row_hash
                    
                    if price_changed or hash_changed:
                        # Update book
                        update_data = {
                            'title': row['Title'],
                            'author': row['Author'],
                            'packt_price': row['Packt_Price'],
                            'packt_url': row['Packt_URL'],
                            'csv_row_hash': row_hash
                        }
                        db.update_book(existing_book.id, **update_data)
                        stats['rows_updated'] += 1
                        self.logger.debug(f"Updated book: {isbn}")
                        
                        # Add price history if price changed
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
                
            except Exception as e:
                self.logger.error(f"Error syncing row for ISBN {row.get('ISBN', 'unknown')}: {e}")
                continue
        
        return stats
    
    def _calculate_row_hash(self, row: pd.Series) -> str:
        """Calculate hash for a CSV row (ISBN + Price + Title)."""
        hash_string = f"{row['ISBN']}|{row['Packt_Price']}|{row['Title']}"
        return hashlib.sha256(hash_string.encode()).hexdigest()

