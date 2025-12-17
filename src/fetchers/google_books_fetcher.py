"""Google Books API client."""

import requests
from typing import Optional, Dict, Any
from time import sleep

from src.utils.logger import get_logger
from src.utils.rate_limiter import SimpleRateLimiter

logger = get_logger(__name__)


class GoogleBooksFetcher:
    """Fetcher for Google Books API."""
    
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"
    
    def __init__(self):
        """Initialize Google Books fetcher."""
        self.logger = logger
        # Google Books API: 1000 requests/day free tier
        # Use simple rate limiter with 1 second delay to be safe
        self.rate_limiter = SimpleRateLimiter(delay_seconds=1.0)
    
    def fetch_by_isbn(self, isbn: str) -> Optional[Dict[str, Any]]:
        """
        Fetch book metadata by ISBN.
        
        Args:
            isbn: Book ISBN (10 or 13 digits)
            
        Returns:
            Dictionary with book metadata or None if not found/error
        """
        self.rate_limiter.wait_if_needed('google_books')
        
        try:
            # Clean ISBN (remove hyphens and spaces)
            clean_isbn = isbn.replace('-', '').replace(' ', '')
            query = f"isbn:{clean_isbn}"
            
            params = {
                'q': query,
                'maxResults': 1
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('totalItems', 0) == 0:
                self.logger.debug(f"No results found for ISBN: {isbn}")
                return None
            
            # Extract book information
            item = data['items'][0]
            volume_info = item.get('volumeInfo', {})
            
            book_data = {
                'title': volume_info.get('title'),
                'authors': volume_info.get('authors', []),
                'published_date': volume_info.get('publishedDate'),
                'description': volume_info.get('description'),
                'publisher': volume_info.get('publisher'),
                'page_count': volume_info.get('pageCount'),
                'categories': volume_info.get('categories', []),
                'language': volume_info.get('language'),
                'preview_link': volume_info.get('previewLink'),
                'info_link': volume_info.get('infoLink'),
                'canonical_isbn': self._extract_isbn(volume_info.get('industryIdentifiers', []))
            }
            
            self.logger.debug(f"Fetched metadata for ISBN {isbn}: {book_data.get('title')}")
            return book_data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching from Google Books API for ISBN {isbn}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching from Google Books API: {e}")
            return None
    
    def _extract_isbn(self, identifiers: list) -> Optional[str]:
        """Extract ISBN from industry identifiers."""
        for identifier in identifiers:
            if identifier.get('type') in ['ISBN_13', 'ISBN_10']:
                return identifier.get('identifier')
        return None
    
    def validate_book(self, isbn: str, title: str = None) -> bool:
        """
        Validate that a book exists in Google Books.
        
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
            # Simple substring matching (can be improved)
            if provided_title not in fetched_title and fetched_title not in provided_title:
                self.logger.warning(
                    f"Title mismatch for ISBN {isbn}: "
                    f"provided '{title}' vs fetched '{book_data.get('title')}'"
                )
        
        return True

