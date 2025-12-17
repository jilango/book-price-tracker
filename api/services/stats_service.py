"""Statistics calculation service."""

from typing import List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy import func, and_, or_
from src.storage.models import Book, Alert, PriceHistory
from src.storage.database import db
from api.models import (
    DashboardStatsResponse, PriceTrendDataPoint, ComparisonStatsResponse,
    PriceDistributionResponse, PriceBucket, DataQualityResponse, RecentActivityResponse,
    ActivityDataPoint, BookResponse
)


class StatsService:
    """Service for statistics calculations."""
    
    @staticmethod
    def get_dashboard_stats() -> DashboardStatsResponse:
        """Get dashboard summary statistics."""
        with db.get_session() as session:
            # Total books
            total_books = session.query(func.count(Book.id)).scalar()
            
            # Active alerts (within cooldown period)
            from src.config import config
            cooldown_hours = config.notification_cooldown_hours
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=cooldown_hours)
            
            active_alerts = session.query(func.count(Alert.id)).filter(
                Alert.notified_at >= cutoff_time,
                Alert.status == 'sent'
            ).scalar()
            
            # Books with alerts
            books_with_alerts = session.query(func.count(func.distinct(Alert.book_id))).filter(
                Alert.notified_at >= cutoff_time,
                Alert.status == 'sent'
            ).scalar()
            
            # Average price difference from active alerts
            avg_diff_result = session.query(
                func.avg(Alert.packt_price - Alert.third_party_price)
            ).filter(
                Alert.notified_at >= cutoff_time,
                Alert.status == 'sent'
            ).scalar()
            
            # Total savings opportunity
            total_savings = session.query(
                func.sum(Alert.packt_price - Alert.third_party_price)
            ).filter(
                Alert.notified_at >= cutoff_time,
                Alert.status == 'sent'
            ).scalar()
            
            # New catalog overview metrics
            prices = session.query(Book.packt_price).filter(Book.packt_price.isnot(None)).all()
            prices_list = [p[0] for p in prices if p[0] is not None]
            
            total_catalog_value = sum(prices_list) if prices_list else None
            min_price = min(prices_list) if prices_list else None
            max_price = max(prices_list) if prices_list else None
            average_price = sum(prices_list) / len(prices_list) if prices_list else None
            
            # Data quality metrics
            books_missing_authors = session.query(func.count(Book.id)).filter(
                or_(Book.author.is_(None), Book.author == '')
            ).scalar()
            
            books_missing_urls = session.query(func.count(Book.id)).filter(
                or_(Book.packt_url.is_(None), Book.packt_url == '')
            ).scalar()
            
            # Books without price history
            books_with_history = session.query(func.count(func.distinct(PriceHistory.book_id))).scalar()
            books_without_price_history = total_books - books_with_history if total_books > 0 else 0
            
            # Data completeness percentage
            # Complete = has title, author, price, url
            complete_books = session.query(func.count(Book.id)).filter(
                Book.title.isnot(None),
                Book.title != '',
                Book.packt_price.isnot(None),
                Book.packt_url.isnot(None),
                Book.packt_url != ''
            ).scalar()
            data_completeness = (complete_books / total_books * 100) if total_books > 0 else 0.0
            
            return DashboardStatsResponse(
                total_books=total_books or 0,
                active_alerts=active_alerts or 0,
                average_price_difference=float(avg_diff_result) if avg_diff_result else None,
                total_savings_opportunity=float(total_savings) if total_savings else None,
                books_with_alerts=books_with_alerts or 0,
                total_catalog_value=float(total_catalog_value) if total_catalog_value else None,
                min_price=float(min_price) if min_price else None,
                max_price=float(max_price) if max_price else None,
                average_price=float(average_price) if average_price else None,
                books_missing_authors=books_missing_authors or 0,
                books_missing_urls=books_missing_urls or 0,
                books_without_price_history=books_without_price_history,
                data_completeness_percentage=round(data_completeness, 2)
            )
    
    @staticmethod
    def get_price_trends(
        days: int = 30,
        book_id: Optional[int] = None
    ) -> List[PriceTrendDataPoint]:
        """Get price trends data for charts."""
        date_from = datetime.now(timezone.utc) - timedelta(days=days)
        
        with db.get_session() as session:
            query = session.query(PriceHistory).filter(
                PriceHistory.timestamp >= date_from
            )
            
            if book_id:
                query = query.filter(PriceHistory.book_id == book_id)
            
            # Group by date and source
            price_history = query.order_by(PriceHistory.timestamp.asc()).all()
            
            # Aggregate by date
            trends_dict = {}
            packt_prices_by_date = {}  # Track all packt prices to average them
            for ph in price_history:
                date_key = ph.timestamp.date().isoformat()
                if date_key not in trends_dict:
                    trends_dict[date_key] = {
                        'packt_price': None,
                        'third_party_price': None
                    }
                    packt_prices_by_date[date_key] = []
                
                if ph.source == 'packt':
                    packt_prices_by_date[date_key].append(ph.price)
                    # Use average of all packt prices for this date
                    trends_dict[date_key]['packt_price'] = sum(packt_prices_by_date[date_key]) / len(packt_prices_by_date[date_key])
                else:
                    if trends_dict[date_key]['third_party_price'] is None:
                        trends_dict[date_key]['third_party_price'] = ph.price
                    else:
                        # Take minimum third-party price
                        trends_dict[date_key]['third_party_price'] = min(
                            trends_dict[date_key]['third_party_price'],
                            ph.price
                        )
            
            # Convert to list of data points
            trends = []
            for date_str, prices in sorted(trends_dict.items()):
                diff = None
                if prices['packt_price'] and prices['third_party_price']:
                    diff = prices['packt_price'] - prices['third_party_price']
                
                trends.append(PriceTrendDataPoint(
                    date=date_str,
                    packt_price=prices['packt_price'],
                    third_party_price=prices['third_party_price'],
                    difference=diff
                ))
            
            return trends
    
    @staticmethod
    def get_comparison_stats() -> ComparisonStatsResponse:
        """Get price comparison statistics."""
        with db.get_session() as session:
            # Get all alerts
            alerts = session.query(Alert).filter(Alert.status == 'sent').all()
            
            total_comparisons = len(alerts)
            packt_cheaper = 0
            third_party_cheaper = 0
            total_diff = 0.0
            
            for alert in alerts:
                diff = alert.packt_price - alert.third_party_price
                if diff > 0:
                    third_party_cheaper += 1
                    total_diff += diff
                elif diff < 0:
                    packt_cheaper += 1
            
            avg_diff = total_diff / third_party_cheaper if third_party_cheaper > 0 else None
            
            return ComparisonStatsResponse(
                total_comparisons=total_comparisons,
                packt_cheaper=packt_cheaper,
                third_party_cheaper=third_party_cheaper,
                average_difference=float(avg_diff) if avg_diff else None
            )
    
    @staticmethod
    def get_price_distribution() -> PriceDistributionResponse:
        """Get price distribution by buckets."""
        price_buckets = [
            (0, 5, "$0-5"),
            (5, 10, "$5-10"),
            (10, 15, "$10-15"),
            (15, 20, "$15-20"),
            (20, 25, "$20-25"),
            (25, 30, "$25-30"),
            (30, float('inf'), "$30+")
        ]
        
        with db.get_session() as session:
            total_books = session.query(func.count(Book.id)).scalar()
            books = session.query(Book).filter(Book.packt_price.isnot(None)).all()
            
            buckets = []
            for min_price, max_price, label in price_buckets:
                count = 0
                for book in books:
                    if book.packt_price is not None:
                        if min_price <= book.packt_price < max_price:
                            count += 1
                
                percentage = (count / total_books * 100) if total_books > 0 else 0.0
                buckets.append(PriceBucket(
                    range=label,
                    count=count,
                    percentage=round(percentage, 2)
                ))
            
            return PriceDistributionResponse(
                buckets=buckets,
                total_books=total_books or 0
            )
    
    @staticmethod
    def get_data_quality() -> DataQualityResponse:
        """Get detailed data quality metrics."""
        with db.get_session() as session:
            total_books = session.query(func.count(Book.id)).scalar()
            
            # Missing authors
            books_missing_authors = session.query(func.count(Book.id)).filter(
                or_(Book.author.is_(None), Book.author == '')
            ).scalar()
            
            # Missing URLs
            books_missing_urls = session.query(func.count(Book.id)).filter(
                or_(Book.packt_url.is_(None), Book.packt_url == '')
            ).scalar()
            
            # Missing prices
            books_missing_prices = session.query(func.count(Book.id)).filter(
                Book.packt_price.is_(None)
            ).scalar()
            
            # Without price history
            books_with_history = session.query(func.count(func.distinct(PriceHistory.book_id))).scalar()
            books_without_price_history = total_books - books_with_history if total_books > 0 else 0
            
            # Stale books (not updated in 90+ days)
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)
            books_stale = session.query(func.count(Book.id)).filter(
                or_(
                    Book.last_updated.is_(None),
                    Book.last_updated < cutoff_date
                )
            ).scalar()
            
            # Data completeness
            complete_books = session.query(func.count(Book.id)).filter(
                Book.title.isnot(None),
                Book.title != '',
                Book.packt_price.isnot(None),
                Book.packt_url.isnot(None),
                Book.packt_url != ''
            ).scalar()
            data_completeness = (complete_books / total_books * 100) if total_books > 0 else 0.0
            
            # Books needing attention
            books_needing_attention = session.query(Book).filter(
                or_(
                    or_(Book.author.is_(None), Book.author == ''),
                    or_(Book.packt_url.is_(None), Book.packt_url == ''),
                    Book.packt_price.is_(None)
                )
            ).limit(20).all()
            
            # Convert to response models
            attention_books = []
            for book in books_needing_attention:
                book_dict = {
                    'id': book.id,
                    'isbn': book.isbn,
                    'title': book.title,
                    'author': book.author,
                    'packt_price': book.packt_price,
                    'packt_url': book.packt_url,
                    'last_updated': book.last_updated.isoformat() if book.last_updated else None,
                    'created_at': book.created_at.isoformat() if book.created_at else None,
                }
                attention_books.append(BookResponse(**book_dict))
            
            return DataQualityResponse(
                total_books=total_books or 0,
                books_missing_authors=books_missing_authors or 0,
                books_missing_urls=books_missing_urls or 0,
                books_missing_prices=books_missing_prices or 0,
                books_without_price_history=books_without_price_history,
                books_stale=books_stale or 0,
                data_completeness_percentage=round(data_completeness, 2),
                books_needing_attention=attention_books
            )
    
    @staticmethod
    def get_recent_activity(days: int = 30) -> RecentActivityResponse:
        """Get recent activity timeline."""
        date_from = datetime.now(timezone.utc) - timedelta(days=days)
        
        with db.get_session() as session:
            # Get books created/updated in the period
            books_created = session.query(Book).filter(
                Book.created_at >= date_from
            ).all()
            
            books_updated = session.query(Book).filter(
                Book.last_updated >= date_from,
                Book.last_updated != Book.created_at  # Exclude books that were just created
            ).all()
            
            # Get CSV sync history
            from src.storage.models import CSVSyncLog
            sync_logs = session.query(CSVSyncLog).filter(
                CSVSyncLog.last_processed_time >= date_from
            ).order_by(CSVSyncLog.last_processed_time.asc()).all()
            
            # Group by date
            activity_dict = {}
            
            # Process book creations
            for book in books_created:
                date_key = book.created_at.date().isoformat() if book.created_at else None
                if date_key:
                    if date_key not in activity_dict:
                        activity_dict[date_key] = {'books_added': 0, 'books_updated': 0}
                    activity_dict[date_key]['books_added'] += 1
            
            # Process book updates
            for book in books_updated:
                date_key = book.last_updated.date().isoformat() if book.last_updated else None
                if date_key:
                    if date_key not in activity_dict:
                        activity_dict[date_key] = {'books_added': 0, 'books_updated': 0}
                    activity_dict[date_key]['books_updated'] += 1
            
            # Process sync logs
            for sync_log in sync_logs:
                date_key = sync_log.last_processed_time.date().isoformat()
                if date_key not in activity_dict:
                    activity_dict[date_key] = {'books_added': 0, 'books_updated': 0}
                # Syncs can add both new and updated books
                activity_dict[date_key]['books_added'] += sync_log.rows_inserted
                activity_dict[date_key]['books_updated'] += sync_log.rows_updated
            
            # Convert to list
            activity = []
            for date_str in sorted(activity_dict.keys()):
                data = activity_dict[date_str]
                activity.append(ActivityDataPoint(
                    date=date_str,
                    books_added=data['books_added'],
                    books_updated=data['books_updated'],
                    total_changes=data['books_added'] + data['books_updated']
                ))
            
            return RecentActivityResponse(
                activity=activity,
                date_from=date_from.date().isoformat(),
                date_to=datetime.now(timezone.utc).date().isoformat()
            )

