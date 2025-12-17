"""CSV parsing and validation."""

import re
import pandas as pd
from typing import Optional
from urllib.parse import urlparse

from src.utils.logger import get_logger

logger = get_logger(__name__)


class CSVParser:
    """Parser for Packt books CSV file."""
    
    REQUIRED_COLUMNS = ['ISBN', 'Title', 'Author', 'Packt_Price', 'Packt_URL']
    OPTIONAL_COLUMNS = ['Last_Updated']
    
    def __init__(self):
        """Initialize CSV parser."""
        self.logger = logger
    
    def parse(self, csv_path: str) -> Optional[pd.DataFrame]:
        """
        Parse CSV file and return validated DataFrame.
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            Validated DataFrame or None if parsing fails
        """
        try:
            df = pd.read_csv(csv_path)
            self.logger.info(f"Loaded CSV with {len(df)} rows")
            
            # Validate columns
            if not self._validate_columns(df):
                return None
            
            # Validate and clean data
            validated_df = self._validate_data(df)
            
            self.logger.info(f"Validated {len(validated_df)} rows")
            return validated_df
            
        except FileNotFoundError:
            self.logger.error(f"CSV file not found: {csv_path}")
            return None
        except pd.errors.EmptyDataError:
            self.logger.error(f"CSV file is empty: {csv_path}")
            return None
        except Exception as e:
            self.logger.error(f"Error parsing CSV: {e}")
            return None
    
    def _validate_columns(self, df: pd.DataFrame) -> bool:
        """Validate that required columns exist."""
        missing_columns = []
        for col in self.REQUIRED_COLUMNS:
            if col not in df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            self.logger.error(f"Missing required columns: {missing_columns}")
            return False
        
        return True
    
    def _validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean data in DataFrame."""
        validated_rows = []
        
        for idx, row in df.iterrows():
            try:
                validated_row = self._validate_row(row)
                if validated_row:
                    validated_rows.append(validated_row)
            except Exception as e:
                self.logger.warning(f"Skipping row {idx + 1}: {e}")
                continue
        
        if not validated_rows:
            self.logger.warning("No valid rows found after validation")
            return pd.DataFrame()
        
        return pd.DataFrame(validated_rows)
    
    def _validate_row(self, row: pd.Series) -> Optional[dict]:
        """Validate a single row of data."""
        # Validate ISBN
        isbn = str(row['ISBN']).strip()
        if not self._is_valid_isbn(isbn):
            raise ValueError(f"Invalid ISBN: {isbn}")
        
        # Validate title
        title = str(row['Title']).strip() if pd.notna(row['Title']) else None
        if not title:
            raise ValueError("Title is required")
        
        # Validate author
        author = str(row['Author']).strip() if pd.notna(row['Author']) else None
        
        # Validate price
        try:
            price = float(row['Packt_Price'])
            if price < 0:
                raise ValueError(f"Price must be positive: {price}")
        except (ValueError, TypeError):
            raise ValueError(f"Invalid price: {row['Packt_Price']}")
        
        # Validate URL
        url = str(row['Packt_URL']).strip() if pd.notna(row['Packt_URL']) else None
        if url and not self._is_valid_url(url):
            raise ValueError(f"Invalid URL: {url}")
        
        # Optional: Last_Updated
        last_updated = None
        if 'Last_Updated' in row and pd.notna(row['Last_Updated']):
            last_updated = str(row['Last_Updated']).strip()
        
        return {
            'ISBN': isbn,
            'Title': title,
            'Author': author,
            'Packt_Price': price,
            'Packt_URL': url,
            'Last_Updated': last_updated
        }
    
    def _is_valid_isbn(self, isbn: str) -> bool:
        """Validate ISBN format (10 or 13 digits)."""
        # Remove hyphens and spaces
        isbn_clean = re.sub(r'[-\s]', '', isbn)
        # Check if it's 10 or 13 digits
        return bool(re.match(r'^\d{10}$|^\d{13}$', isbn_clean))
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

