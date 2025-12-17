"""CSV file change detection."""

import hashlib
import os
from pathlib import Path
from typing import Optional

from src.storage.database import db
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CSVWatcher:
    """Monitor CSV file for changes using hash comparison."""
    
    def __init__(self, csv_path: str):
        """Initialize CSV watcher."""
        self.csv_path = Path(csv_path)
        self.logger = logger
    
    def has_changed(self) -> bool:
        """
        Check if CSV file has changed since last sync.
        
        Returns:
            True if file has changed, False otherwise
        """
        if not self.csv_path.exists():
            self.logger.warning(f"CSV file does not exist: {self.csv_path}")
            return False
        
        # Calculate current file hash
        current_hash = self._calculate_file_hash()
        if current_hash is None:
            return False
        
        # Get last processed hash from database
        filename = self.csv_path.name
        last_sync = db.get_latest_sync_log(filename)
        
        if last_sync is None:
            # First time processing this file
            self.logger.info(f"First time processing CSV file: {filename}")
            return True
        
        # Access hash attribute while session is still open (it's already accessed in get_latest_sync_log)
        # But we need to get it as a string to avoid session issues
        last_hash = last_sync.last_processed_hash if last_sync else None
        
        # Compare hashes
        if current_hash != last_hash:
            self.logger.info(f"CSV file changed: {filename}")
            return True
        
        self.logger.debug(f"CSV file unchanged: {filename}")
        return False
    
    def _calculate_file_hash(self) -> Optional[str]:
        """Calculate SHA256 hash of file content."""
        try:
            sha256_hash = hashlib.sha256()
            with open(self.csv_path, 'rb') as f:
                # Read file in chunks to handle large files
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating file hash: {e}")
            return None
    
    def get_file_hash(self) -> Optional[str]:
        """Get current file hash."""
        return self._calculate_file_hash()
    
    def get_file_mtime(self) -> Optional[float]:
        """Get file modification time."""
        try:
            return os.path.getmtime(self.csv_path)
        except Exception as e:
            self.logger.error(f"Error getting file mtime: {e}")
            return None

