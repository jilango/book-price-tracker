"""Price comparison logic."""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from src.storage.database import db
from src.storage.models import Book
from src.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PriceComparator:
    """Compare prices and check thresholds."""
    
    def __init__(self):
        """Initialize price comparator."""
        self.logger = logger
        self.threshold_percentage = config.threshold_percentage
        self.threshold_absolute = config.threshold_absolute
        self.cooldown_hours = config.notification_cooldown_hours
    
    def compare_prices(self, book: Book, third_party_price: float,
                      third_party_source: str) -> Optional[Dict[str, Any]]:
        """
        Compare Packt price with third-party price.
        
        Args:
            book: Book object from database
            third_party_price: Third-party price
            third_party_source: Source of third-party price
            
        Returns:
            Alert dictionary if threshold met, None otherwise
        """
        if book.packt_price is None:
            self.logger.warning(f"Book {book.isbn} has no Packt price")
            return None
        
        if third_party_price is None or third_party_price <= 0:
            self.logger.warning(f"Invalid third-party price: {third_party_price}")
            return None
        
        # Check if third-party price is cheaper
        if third_party_price >= book.packt_price:
            self.logger.debug(
                f"Third-party price ({third_party_price}) not cheaper than Packt ({book.packt_price})"
            )
            return None
        
        # Calculate difference
        difference = book.packt_price - third_party_price
        percentage_diff = (difference / book.packt_price) * 100
        
        self.logger.info(
            f"Price comparison for {book.isbn}: Packt=${book.packt_price}, "
            f"{third_party_source}=${third_party_price}, "
            f"diff=${difference:.2f} ({percentage_diff:.2f}%)"
        )
        
        # Check thresholds
        threshold_met = (
            percentage_diff >= self.threshold_percentage or
            difference >= self.threshold_absolute
        )
        
        if not threshold_met:
            self.logger.debug(f"Threshold not met for {book.isbn}")
            return None
        
        # Check cooldown period
        if self._is_in_cooldown(book.id):
            self.logger.info(
                f"Book {book.isbn} is in cooldown period, skipping notification"
            )
            return None
        
        # Create alert data
        alert_data = {
            'book_id': book.id,
            'book_isbn': book.isbn,
            'book_title': book.title,
            'threshold_type': 'percentage' if percentage_diff >= self.threshold_percentage else 'absolute',
            'threshold_value': self.threshold_percentage if percentage_diff >= self.threshold_percentage else self.threshold_absolute,
            'packt_price': book.packt_price,
            'third_party_price': third_party_price,
            'third_party_source': third_party_source,
            'difference': difference,
            'percentage_diff': percentage_diff
        }
        
        return alert_data
    
    def _is_in_cooldown(self, book_id: int) -> bool:
        """
        Check if book is in notification cooldown period.
        
        Args:
            book_id: Book ID
            
        Returns:
            True if in cooldown, False otherwise
        """
        recent_alerts = db.get_recent_alerts(book_id, self.cooldown_hours)
        return len(recent_alerts) > 0
    
    def should_notify(self, alert_data: Dict[str, Any]) -> bool:
        """
        Determine if notification should be sent.
        
        Args:
            alert_data: Alert data dictionary
            
        Returns:
            True if should notify, False otherwise
        """
        if alert_data is None:
            return False
        
        # Check cooldown again (in case it changed)
        if self._is_in_cooldown(alert_data['book_id']):
            return False
        
        return True

