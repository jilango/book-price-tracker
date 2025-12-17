"""Rate limiting utilities for API calls."""

import time
from typing import Optional
from collections import defaultdict
from threading import Lock

from src.utils.logger import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """Simple rate limiter using token bucket algorithm."""
    
    def __init__(self, max_calls: int, time_window: int):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = defaultdict(list)
        self.lock = Lock()
        self.logger = logger
    
    def wait_if_needed(self, key: str = 'default') -> None:
        """
        Wait if rate limit would be exceeded.
        
        Args:
            key: Rate limit key (for different API endpoints)
        """
        with self.lock:
            now = time.time()
            calls = self.calls[key]
            
            # Remove old calls outside the time window
            calls[:] = [call_time for call_time in calls if now - call_time < self.time_window]
            
            # If we're at the limit, wait until the oldest call expires
            if len(calls) >= self.max_calls:
                oldest_call = min(calls)
                wait_time = self.time_window - (now - oldest_call) + 0.1  # Add small buffer
                if wait_time > 0:
                    self.logger.info(f"Rate limit reached for {key}, waiting {wait_time:.2f}s")
                    time.sleep(wait_time)
                    # Clean up again after waiting
                    now = time.time()
                    calls[:] = [call_time for call_time in calls if now - call_time < self.time_window]
            
            # Record this call
            calls.append(time.time())
    
    def can_proceed(self, key: str = 'default') -> bool:
        """
        Check if a call can proceed without waiting.
        
        Args:
            key: Rate limit key
            
        Returns:
            True if call can proceed, False otherwise
        """
        with self.lock:
            now = time.time()
            calls = self.calls[key]
            
            # Remove old calls
            calls[:] = [call_time for call_time in calls if now - call_time < self.time_window]
            
            return len(calls) < self.max_calls


class SimpleRateLimiter:
    """Simple rate limiter with fixed delay between calls."""
    
    def __init__(self, delay_seconds: float):
        """
        Initialize simple rate limiter.
        
        Args:
            delay_seconds: Delay between calls in seconds
        """
        self.delay_seconds = delay_seconds
        self.last_call_time = defaultdict(float)
        self.lock = Lock()
        self.logger = logger
    
    def wait_if_needed(self, key: str = 'default') -> None:
        """
        Wait if needed to respect rate limit.
        
        Args:
            key: Rate limit key
        """
        with self.lock:
            now = time.time()
            last_call = self.last_call_time[key]
            elapsed = now - last_call
            
            if elapsed < self.delay_seconds:
                wait_time = self.delay_seconds - elapsed
                self.logger.debug(f"Rate limiting {key}, waiting {wait_time:.2f}s")
                time.sleep(wait_time)
            
            self.last_call_time[key] = time.time()

