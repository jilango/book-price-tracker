"""Console notification service."""

from typing import Dict, Any

from src.storage.database import db
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ConsoleNotifier:
    """Console-based notification service."""
    
    def __init__(self):
        """Initialize console notifier."""
        self.logger = logger
    
    def send_alert(self, alert_data: Dict[str, Any]) -> bool:
        """
        Send alert notification to console.
        
        Args:
            alert_data: Alert data dictionary from price comparator
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            # Format alert message
            message = self._format_alert_message(alert_data)
            
            # Log as structured JSON
            self.logger.info(
                "PRICE DROP ALERT",
                extra={
                    'alert_type': 'price_drop',
                    'book_isbn': alert_data.get('book_isbn'),
                    'book_title': alert_data.get('book_title'),
                    'packt_price': alert_data.get('packt_price'),
                    'third_party_price': alert_data.get('third_party_price'),
                    'third_party_source': alert_data.get('third_party_source'),
                    'difference': alert_data.get('difference'),
                    'percentage_diff': alert_data.get('percentage_diff'),
                    'threshold_type': alert_data.get('threshold_type'),
                    'threshold_value': alert_data.get('threshold_value')
                }
            )
            
            # Also print formatted message to console
            print("\n" + "=" * 80)
            print("PRICE DROP ALERT")
            print("=" * 80)
            print(message)
            print("=" * 80 + "\n")
            
            # Create alert record in database
            alert = db.create_alert(
                book_id=alert_data['book_id'],
                threshold_type=alert_data['threshold_type'],
                threshold_value=alert_data['threshold_value'],
                packt_price=alert_data['packt_price'],
                third_party_price=alert_data['third_party_price'],
                third_party_source=alert_data['third_party_source'],
                status='sent'
            )
            
            self.logger.info(f"Alert created in database with ID: {alert.id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending alert: {e}")
            # Try to create alert with failed status
            try:
                db.create_alert(
                    book_id=alert_data.get('book_id'),
                    threshold_type=alert_data.get('threshold_type', 'unknown'),
                    threshold_value=alert_data.get('threshold_value', 0),
                    packt_price=alert_data.get('packt_price', 0),
                    third_party_price=alert_data.get('third_party_price', 0),
                    third_party_source=alert_data.get('third_party_source', 'unknown'),
                    status='failed'
                )
            except Exception:
                pass
            return False
    
    def _format_alert_message(self, alert_data: Dict[str, Any]) -> str:
        """Format alert message for console output."""
        lines = [
            f"Book: {alert_data.get('book_title', 'Unknown')}",
            f"ISBN: {alert_data.get('book_isbn', 'Unknown')}",
            f"",
            f"Packt Price: ${alert_data.get('packt_price', 0):.2f}",
            f"{alert_data.get('third_party_source', 'Third-Party')} Price: ${alert_data.get('third_party_price', 0):.2f}",
            f"",
            f"Savings: ${alert_data.get('difference', 0):.2f} ({alert_data.get('percentage_diff', 0):.2f}%)",
            f"",
            f"Threshold: {alert_data.get('threshold_type', 'unknown')} ({alert_data.get('threshold_value', 0)})"
        ]
        return "\n".join(lines)

