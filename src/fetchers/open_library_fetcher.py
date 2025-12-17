"""Open Library API client."""

import requests
from typing import Optional, Dict, Any

from src.utils.logger import get_logger
from src.utils.rate_limiter import SimpleRateLimiter

logger = get_logger(__name__)


class OpenLibraryFetcher:
    """Fetcher for Open Library API."""
    
    BASE_URL = "https://openlibrary.org/api/books"
    
    def __init__(self):
        """Initialize Open Library fetcher."""
        self.logger = logger
        # Open Library is more permissive, but use rate limiting anyway
        self.rate_limiter = SimpleRateLimiter(delay_seconds=0.5)
    
    def fetch_by_isbn(self, isbn: str) -> Optional[Dict[str, Any]]:
        """
        Fetch book metadata by ISBN.
        
        Args:
            isbn: Book ISBN (10 or 13 digits)
            
        Returns:
            Dictionary with book metadata or None if not found/error
        """
        self.rate_limiter.wait_if_needed('open_library')
        
        try:
            # Clean ISBN
            clean_isbn = isbn.replace('-', '').replace(' ', '')
            
            # Open Library uses ISBN: prefix
            bibkey = f"ISBN:{clean_isbn}"
            
            params = {
                'bibkeys': bibkey,
                'format': 'json',
                'jscmd': 'data'
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Open Library returns data with ISBN as key
            book_key = f"ISBN:{clean_isbn}"
            if book_key not in data:
                self.logger.debug(f"No results found for ISBN: {isbn}")
                return None
            
            book_info = data[book_key]
            
            # Extract book information
            book_data = {
                'title': book_info.get('title'),
                'authors': [author.get('name') for author in book_info.get('authors', [])],
                'publish_date': book_info.get('publish_date'),
                'publishers': [pub.get('name') for pub in book_info.get('publishers', [])],
                'number_of_pages': book_info.get('number_of_pages'),
                'subjects': [sub.get('name') for sub in book_info.get('subjects', [])],
                'url': book_info.get('url'),
                'cover_url': book_info.get('cover', {}).get('large') if book_info.get('cover') else None
            }
            
            self.logger.debug(f"Fetched metadata for ISBN {isbn}: {book_data.get('title')}")
            return book_data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching from Open Library API for ISBN {isbn}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching from Open Library API: {e}")
            return None
    
    def validate_book(self, isbn: str, title: str = None) -> bool:
        """
        Validate that a book exists in Open Library.
        
        Args:
            isbn: Book ISBN
            title: Optional title to cross-validate
            
        Returns:
            True if book exists, False otherwise
        """
        book_data = self.fetch_by_isbn(isbn)
        if book_data is None:
            return False
        
        # If title provided, do basic matching
        if title:
            fetched_title = book_data.get('title', '').lower()
            provided_title = title.lower()
            # Simple substring matching
            if provided_title not in fetched_title and fetched_title not in provided_title:
                self.logger.warning(
                    f"Title mismatch for ISBN {isbn}: "
                    f"provided '{title}' vs fetched '{book_data.get('title')}'"
                )
        
        return True

