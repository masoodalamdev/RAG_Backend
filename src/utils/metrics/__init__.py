import time
from typing import Dict, List
from collections import defaultdict
import threading


class MetricsCollector:
    """
    A simple metrics collector for tracking response times and other performance metrics.
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._response_times: Dict[str, List[float]] = defaultdict(list)
        self._request_counts: Dict[str, int] = defaultdict(int)
        self._error_counts: Dict[str, int] = defaultdict(int)
    
    def record_response_time(self, endpoint: str, response_time: float):
        """
        Record the response time for a specific endpoint.
        
        Args:
            endpoint: The API endpoint (e.g., "/chat", "/health")
            response_time: The response time in seconds
        """
        with self._lock:
            self._response_times[endpoint].append(response_time)
            # Keep only the last 1000 measurements to prevent memory issues
            if len(self._response_times[endpoint]) > 1000:
                self._response_times[endpoint] = self._response_times[endpoint][-1000:]
    
    def record_request(self, endpoint: str):
        """
        Record that a request was made to an endpoint.
        
        Args:
            endpoint: The API endpoint (e.g., "/chat", "/health")
        """
        with self._lock:
            self._request_counts[endpoint] += 1
    
    def record_error(self, endpoint: str):
        """
        Record that an error occurred for an endpoint.
        
        Args:
            endpoint: The API endpoint (e.g., "/chat", "/health")
        """
        with self._lock:
            self._error_counts[endpoint] += 1
    
    def get_average_response_time(self, endpoint: str) -> float:
        """
        Get the average response time for an endpoint.
        
        Args:
            endpoint: The API endpoint (e.g., "/chat", "/health")
            
        Returns:
            Average response time in seconds, or 0.0 if no data
        """
        with self._lock:
            times = self._response_times[endpoint]
            if not times:
                return 0.0
            return sum(times) / len(times)
    
    def get_p95_response_time(self, endpoint: str) -> float:
        """
        Get the 95th percentile response time for an endpoint.
        
        Args:
            endpoint: The API endpoint (e.g., "/chat", "/health")
            
        Returns:
            95th percentile response time in seconds, or 0.0 if no data
        """
        with self._lock:
            times = sorted(self._response_times[endpoint])
            if not times:
                return 0.0
            
            index = int(0.95 * len(times))
            if index >= len(times):
                index = len(times) - 1
                
            return times[index]
    
    def get_request_count(self, endpoint: str) -> int:
        """
        Get the total number of requests for an endpoint.
        
        Args:
            endpoint: The API endpoint (e.g., "/chat", "/health")
            
        Returns:
            Total request count
        """
        with self._lock:
            return self._request_counts[endpoint]
    
    def get_error_count(self, endpoint: str) -> int:
        """
        Get the total number of errors for an endpoint.
        
        Args:
            endpoint: The API endpoint (e.g., "/chat", "/health")
            
        Returns:
            Total error count
        """
        with self._lock:
            return self._error_counts[endpoint]
    
    def get_error_rate(self, endpoint: str) -> float:
        """
        Get the error rate for an endpoint.
        
        Args:
            endpoint: The API endpoint (e.g., "/chat", "/health")
            
        Returns:
            Error rate as a decimal (e.g., 0.05 for 5% error rate), or 0.0 if no requests
        """
        with self._lock:
            total_requests = self._request_counts[endpoint]
            if total_requests == 0:
                return 0.0
            return self._error_counts[endpoint] / total_requests


# Global metrics collector instance
metrics_collector = MetricsCollector()


def time_and_record(endpoint: str):
    """
    Decorator to time a function and record the response time.
    
    Args:
        endpoint: The API endpoint to associate with the timing
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                # Record successful request
                metrics_collector.record_request(endpoint)
                return result
            except Exception:
                # Record error
                metrics_collector.record_error(endpoint)
                raise
            finally:
                # Always record response time
                response_time = time.time() - start_time
                metrics_collector.record_response_time(endpoint, response_time)
        return wrapper
    return decorator