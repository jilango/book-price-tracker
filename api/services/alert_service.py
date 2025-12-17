"""Business logic for alert operations."""

from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import and_
from src.storage.models import Alert
from src.storage.database import db


class AlertService:
    """Service for alert-related operations."""
    
    @staticmethod
    def get_alerts(
        status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[Alert], int]:
        """
        Get alerts with filtering and pagination.
        
        Returns:
            Tuple of (alerts list, total count)
        """
        with db.get_session() as session:
            query = session.query(Alert)
            
            # Status filter
            if status:
                query = query.filter(Alert.status == status)
            
            # Date range filter
            if date_from:
                query = query.filter(Alert.notified_at >= date_from)
            if date_to:
                query = query.filter(Alert.notified_at <= date_to)
            
            # Get total count
            total = query.count()
            
            # Order by notified_at descending
            query = query.order_by(Alert.notified_at.desc())
            
            # Pagination
            offset = (page - 1) * limit
            alerts = query.offset(offset).limit(limit).all()
            
            return alerts, total
    
    @staticmethod
    def get_active_alerts(
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[Alert], int]:
        """Get active alerts (recent, not acknowledged)."""
        from src.config import config
        
        cooldown_hours = config.notification_cooldown_hours
        cutoff_time = datetime.utcnow() - timedelta(hours=cooldown_hours)
        
        with db.get_session() as session:
            query = session.query(Alert).filter(
                Alert.notified_at >= cutoff_time,
                Alert.status == 'sent'
            )
            
            total = query.count()
            query = query.order_by(Alert.notified_at.desc())
            
            offset = (page - 1) * limit
            alerts = query.offset(offset).limit(limit).all()
            
            return alerts, total
    
    @staticmethod
    def get_alert_by_id(alert_id: int) -> Optional[Alert]:
        """Get alert by ID."""
        with db.get_session() as session:
            return session.query(Alert).filter(Alert.id == alert_id).first()
    
    @staticmethod
    def acknowledge_alert(alert_id: int) -> Optional[Alert]:
        """Acknowledge an alert."""
        return db.update_alert_status(alert_id, 'acknowledged')

