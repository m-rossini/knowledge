#!/usr/bin/env python3
"""
Prometheus metrics for the knowledge archival system.
Centralizes metric creation and management.
"""

import logging
import prometheus_client
from prometheus_client import Counter, Gauge, Histogram, Summary
from typing import Dict, Optional, List, Union, Any


class MetricsManager:
    """
    Manages Prometheus metrics for the knowledge archival system.
    Centralizes metric creation and management following project standards.
    """
    
    def __init__(self, metrics_port: int = 9090):
        """
        Initialize the MetricsManager.
        
        Args:
            metrics_port: Port to expose Prometheus metrics
        """
        self.logger = logging.getLogger(__name__)
        self.metrics_port = metrics_port
        self.metrics: Dict[str, Any] = {}
        
        # Start Prometheus HTTP server
        try:
            prometheus_client.start_http_server(self.metrics_port)
            self.logger.info(">> MetricsManager::__init__ Prometheus metrics server started on port %d", 
                           self.metrics_port)
        except Exception as e:
            self.logger.error(">>>> MetricsManager::__init__ Failed to start Prometheus server: %s", str(e))
        
        # Initialize standard metrics
        self._initialize_standard_metrics()
    
    def _initialize_standard_metrics(self) -> None:
        """Initialize standard metrics used throughout the application."""
        # Wikipedia metrics
        self.create_counter('wikipedia_check_count', 
                          'Number of times Wikipedia update was checked')
        self.create_counter('wikipedia_download_count', 
                          'Number of Wikipedia downloads')
        self.create_gauge('wikipedia_last_download_size_bytes', 
                        'Size of last Wikipedia download in bytes')
        self.create_gauge('wikipedia_last_download_time_seconds', 
                        'Time taken for last Wikipedia download in seconds')
        self.create_counter('wikipedia_download_failures', 
                          'Number of Wikipedia download failures')
        
        # Backup metrics
        self.create_counter('backup_count', 
                          'Number of backups performed')
        self.create_gauge('backup_last_size_bytes', 
                        'Size of last backup in bytes')
        self.create_gauge('backup_last_time_seconds', 
                        'Time taken for last backup in seconds')
        self.create_counter('backup_failures', 
                          'Number of backup failures')
    
    def create_counter(self, name: str, description: str, 
                     labels: Optional[List[str]] = None) -> Counter:
        """
        Create and register a Prometheus Counter.
        
        Args:
            name: Metric name
            description: Metric description
            labels: Optional list of label names
            
        Returns:
            The created Counter
        """
        if name in self.metrics:
            self.logger.debug("> MetricsManager::create_counter Returning existing metric: %s", name)
            return self.metrics[name]
        
        self.logger.debug("> MetricsManager::create_counter Creating new counter: %s", name)
        counter = Counter(name, description, labels or [])
        self.metrics[name] = counter
        return counter
    
    def create_gauge(self, name: str, description: str, 
                   labels: Optional[List[str]] = None) -> Gauge:
        """
        Create and register a Prometheus Gauge.
        
        Args:
            name: Metric name
            description: Metric description
            labels: Optional list of label names
            
        Returns:
            The created Gauge
        """
        if name in self.metrics:
            self.logger.debug("> MetricsManager::create_gauge Returning existing metric: %s", name)
            return self.metrics[name]
        
        self.logger.debug("> MetricsManager::create_gauge Creating new gauge: %s", name)
        gauge = Gauge(name, description, labels or [])
        self.metrics[name] = gauge
        return gauge
    
    def create_histogram(self, name: str, description: str, 
                       labels: Optional[List[str]] = None, 
                       buckets: Optional[List[float]] = None) -> Histogram:
        """
        Create and register a Prometheus Histogram.
        
        Args:
            name: Metric name
            description: Metric description
            labels: Optional list of label names
            buckets: Optional list of bucket boundaries
            
        Returns:
            The created Histogram
        """
        if name in self.metrics:
            self.logger.debug("> MetricsManager::create_histogram Returning existing metric: %s", name)
            return self.metrics[name]
        
        self.logger.debug("> MetricsManager::create_histogram Creating new histogram: %s", name)
        histogram = Histogram(name, description, labels or [], buckets)
        self.metrics[name] = histogram
        return histogram
    
    def get_metric(self, name: str) -> Optional[Union[Counter, Gauge, Histogram, Summary]]:
        """
        Get a registered metric by name.
        
        Args:
            name: Name of the metric to retrieve
            
        Returns:
            The metric object or None if not found
        """
        metric = self.metrics.get(name)
        if metric is None:
            self.logger.warning(">>> MetricsManager::get_metric Metric not found: %s", name)
        return metric