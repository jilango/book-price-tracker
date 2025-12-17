"""Main orchestrator for Book Price Drop Watcher."""

import signal
import sys
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.config import config
from src.storage.database import db
from src.csv_processor.csv_sync import CSVSync
from src.fetchers.google_books_fetcher import GoogleBooksFetcher
from src.fetchers.open_library_fetcher import OpenLibraryFetcher
from src.comparators.price_comparator import PriceComparator
from src.notifications.console_notifier import ConsoleNotifier
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BookPriceWatcher:
    """Main orchestrator for the price watching pipeline."""
    
    def __init__(self):
        """Initialize the price watcher."""
        self.logger = logger
        self.config = config
        self.scheduler = BlockingScheduler()
        self.csv_sync = CSVSync(config.csv_file_path)
        self.google_books_fetcher = GoogleBooksFetcher()
        self.open_library_fetcher = OpenLibraryFetcher()
        self.price_comparator = PriceComparator()
        self.notifier = ConsoleNotifier()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info("Received shutdown signal, stopping scheduler...")
        self.scheduler.shutdown()
        sys.exit(0)
    
    def setup_jobs(self):
        """Setup scheduled jobs."""
        # CSV sync job
        csv_trigger = IntervalTrigger(
            minutes=self.config.csv_check_interval_minutes
        )
        self.scheduler.add_job(
            self.csv_sync_job,
            trigger=csv_trigger,
            id='csv_sync',
            name='CSV Sync Job',
            replace_existing=True
        )
        self.logger.info(
            f"CSV sync job scheduled to run every {self.config.csv_check_interval_minutes} minutes"
        )
        
        # Price check job
        price_trigger = IntervalTrigger(
            hours=self.config.price_check_interval_hours
        )
        self.scheduler.add_job(
            self.price_check_job,
            trigger=price_trigger,
            id='price_check',
            name='Price Check Job',
            replace_existing=True
        )
        self.logger.info(
            f"Price check job scheduled to run every {self.config.price_check_interval_hours} hours"
        )
    
    def csv_sync_job(self):
        """Job to sync CSV file to database."""
        self.logger.info("Starting CSV sync job")
        try:
            success, stats = self.csv_sync.sync()
            if success:
                self.logger.info(
                    f"CSV sync completed: {stats['rows_inserted']} inserted, "
                    f"{stats['rows_updated']} updated"
                )
            else:
                self.logger.error("CSV sync failed")
        except Exception as e:
            self.logger.error(f"Error in CSV sync job: {e}", exc_info=True)
    
    def price_check_job(self):
        """Job to check prices and send notifications."""
        self.logger.info("Starting price check job")
        try:
            books = db.get_all_books()
            self.logger.info(f"Checking prices for {len(books)} books")
            
            for book in books:
                try:
                    self._check_book_prices(book)
                except Exception as e:
                    self.logger.error(
                        f"Error checking prices for book {book.isbn}: {e}",
                        exc_info=True
                    )
                    continue
            
            self.logger.info("Price check job completed")
        except Exception as e:
            self.logger.error(f"Error in price check job: {e}", exc_info=True)
    
    def _check_book_prices(self, book):
        """Check prices for a single book."""
        self.logger.debug(f"Checking prices for book: {book.isbn} - {book.title}")
        
        # Note: Google Books and Open Library APIs don't provide prices
        # This is a placeholder for when price sources become available
        # For now, we validate book metadata
        
        # Validate with Google Books
        if 'google_books' in self.config.third_party_sources:
            try:
                metadata = self.google_books_fetcher.fetch_by_isbn(book.isbn)
                if metadata:
                    self.logger.debug(
                        f"Validated {book.isbn} with Google Books: {metadata.get('title')}"
                    )
            except Exception as e:
                self.logger.warning(f"Error validating with Google Books: {e}")
        
        # Validate with Open Library
        if 'open_library' in self.config.third_party_sources:
            try:
                metadata = self.open_library_fetcher.fetch_by_isbn(book.isbn)
                if metadata:
                    self.logger.debug(
                        f"Validated {book.isbn} with Open Library: {metadata.get('title')}"
                    )
            except Exception as e:
                self.logger.warning(f"Error validating with Open Library: {e}")
        
        # TODO: When price sources become available, fetch prices and compare:
        # third_party_price = fetch_price_from_source(book.isbn)
        # alert_data = self.price_comparator.compare_prices(book, third_party_price, 'source')
        # if alert_data and self.price_comparator.should_notify(alert_data):
        #     self.notifier.send_alert(alert_data)
    
    def run(self):
        """Run the scheduler."""
        self.logger.info("Starting Book Price Drop Watcher")
        self.logger.info(f"Database: {self.config.db_path}")
        self.logger.info(f"CSV file: {self.config.csv_file_path}")
        
        # Run initial CSV sync
        self.logger.info("Running initial CSV sync...")
        self.csv_sync_job()
        
        # Setup and start scheduler
        self.setup_jobs()
        self.logger.info("Scheduler started, waiting for jobs...")
        
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            self.logger.info("Scheduler stopped")


def main():
    """Main entry point."""
    watcher = BookPriceWatcher()
    watcher.run()


if __name__ == '__main__':
    main()

