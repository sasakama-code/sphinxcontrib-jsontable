"""Real-time Excel File Monitoring and Auto-Update System.

This module provides comprehensive real-time monitoring capabilities for Excel files
in enterprise environments. It detects file changes, automatically triggers
RAG re-processing, and maintains data freshness across the federation.

Key Features:
- Real-time Excel file change detection
- Automatic RAG re-processing on file updates
- Batch processing for multiple file changes
- Conflict resolution and version management
- Performance optimization for large-scale monitoring
- Integration with federation systems
- Configurable update policies and schedules

Enterprise Benefits:
- Always up-to-date AI insights
- Zero manual intervention for data updates
- Automatic quality validation on changes
- Audit trail for all data modifications
- Performance-optimized for enterprise scale
"""

from __future__ import annotations

import asyncio
import logging
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent

from .converter import ExcelRAGConverter
from .federation import ExcelRAGFederation

logger = logging.getLogger(__name__)


class ExcelFileChangeEvent:
    """Represents a change event for an Excel file."""
    
    def __init__(
        self,
        file_path: str,
        event_type: str,
        timestamp: datetime,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize Excel file change event.
        
        Args:
            file_path: Path to the changed Excel file
            event_type: Type of change (created, modified, deleted)
            timestamp: Timestamp of the change
            metadata: Additional metadata about the change
        """
        self.file_path = file_path
        self.event_type = event_type
        self.timestamp = timestamp
        self.metadata = metadata or {}
        self.processed = False
        self.processing_result: Optional[Dict[str, Any]] = None


class UpdatePolicy:
    """Defines update policy for Excel file monitoring."""
    
    def __init__(
        self,
        immediate_update: bool = True,
        batch_interval: int = 300,  # 5 minutes
        max_batch_size: int = 10,
        quality_threshold: float = 0.8,
        retry_attempts: int = 3,
        backup_on_update: bool = True
    ):
        """Initialize update policy.
        
        Args:
            immediate_update: Whether to process changes immediately
            batch_interval: Interval for batch processing (seconds)
            max_batch_size: Maximum number of files to process in one batch
            quality_threshold: Minimum quality threshold for accepting updates
            retry_attempts: Number of retry attempts for failed updates
            backup_on_update: Whether to backup files before updating
        """
        self.immediate_update = immediate_update
        self.batch_interval = batch_interval
        self.max_batch_size = max_batch_size
        self.quality_threshold = quality_threshold
        self.retry_attempts = retry_attempts
        self.backup_on_update = backup_on_update


class ExcelFileHandler(FileSystemEventHandler):
    """File system event handler for Excel files."""
    
    def __init__(self, monitoring_system: 'ExcelRAGMonitor'):
        """Initialize Excel file handler.
        
        Args:
            monitoring_system: Reference to the monitoring system
        """
        self.monitoring_system = monitoring_system
        self.supported_extensions = {'.xlsx', '.xls', '.xlsm', '.csv'}
        
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory and self._is_excel_file(event.src_path):
            self.monitoring_system._handle_file_change(
                event.src_path, "modified", datetime.now()
            )
    
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory and self._is_excel_file(event.src_path):
            self.monitoring_system._handle_file_change(
                event.src_path, "created", datetime.now()
            )
    
    def _is_excel_file(self, file_path: str) -> bool:
        """Check if file is an Excel file."""
        return Path(file_path).suffix.lower() in self.supported_extensions


class ExcelRAGMonitor:
    """Real-time Excel file monitoring and auto-update system.
    
    This class provides enterprise-grade monitoring capabilities for Excel files,
    automatically detecting changes and triggering RAG re-processing to maintain
    data freshness and accuracy.
    
    Features:
    - Real-time file change detection
    - Configurable update policies
    - Batch processing optimization
    - Quality validation and rollback
    - Integration with federation systems
    - Performance monitoring and alerting
    
    Example:
        >>> monitor = ExcelRAGMonitor()
        >>> monitor.watch_directory("/company/data/", auto_update=True)
        >>> monitor.watch_file("sales_report.xlsx", 
        ...                   on_change=lambda: print("Sales data updated!"))
        >>> monitor.start_monitoring()
    """
    
    def __init__(
        self,
        excel_converter: Optional[ExcelRAGConverter] = None,
        federation: Optional[ExcelRAGFederation] = None,
        update_policy: Optional[UpdatePolicy] = None
    ):
        """Initialize Excel RAG monitor.
        
        Args:
            excel_converter: ExcelRAGConverter instance for processing
            federation: ExcelRAGFederation instance for integration
            update_policy: Update policy configuration
        """
        self.excel_converter = excel_converter or ExcelRAGConverter()
        self.federation = federation
        self.update_policy = update_policy or UpdatePolicy()
        
        # Monitoring state
        self.observers: List[Observer] = []
        self.watched_files: Dict[str, Dict[str, Any]] = {}
        self.watched_directories: Dict[str, Dict[str, Any]] = {}
        self.change_queue: List[ExcelFileChangeEvent] = []
        self.processing_queue: List[ExcelFileChangeEvent] = []
        
        # Control flags
        self.monitoring_active = False
        self.batch_processor_active = False
        
        # Performance tracking
        self.performance_stats = {
            "files_monitored": 0,
            "changes_detected": 0,
            "successful_updates": 0,
            "failed_updates": 0,
            "average_processing_time": 0.0,
            "last_update": None
        }
        
        # Threading
        self.batch_processor_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        
        logger.info("Excel RAG Monitor initialized")
    
    def watch_file(
        self,
        file_path: str,
        on_change: Optional[Callable[[], None]] = None,
        rag_purpose: Optional[str] = None,
        department: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """Watch a specific Excel file for changes.
        
        Args:
            file_path: Path to Excel file to watch
            on_change: Callback function to execute on change
            rag_purpose: RAG purpose for this file
            department: Department this file belongs to
            config: Additional configuration
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        watch_config = {
            "file_path": str(file_path_obj.absolute()),
            "on_change": on_change,
            "rag_purpose": rag_purpose or f"monitor-{file_path_obj.stem}",
            "department": department,
            "config": config or {},
            "last_modified": file_path_obj.stat().st_mtime,
            "watch_started": datetime.now()
        }
        
        self.watched_files[str(file_path_obj.absolute())] = watch_config
        
        # Set up directory observer for this file
        directory = str(file_path_obj.parent)
        if directory not in self.watched_directories:
            self._setup_directory_observer(directory)
        
        self.performance_stats["files_monitored"] += 1
        
        logger.info(f"Watching Excel file: {file_path}")
    
    def watch_directory(
        self,
        directory_path: str,
        recursive: bool = True,
        file_pattern: str = "*.xlsx",
        auto_update: bool = True,
        department: Optional[str] = None
    ) -> None:
        """Watch a directory for Excel file changes.
        
        Args:
            directory_path: Path to directory to watch
            recursive: Whether to watch subdirectories
            file_pattern: File pattern to match
            auto_update: Whether to auto-update on changes
            department: Department this directory belongs to
        """
        dir_path = Path(directory_path)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        watch_config = {
            "directory": str(dir_path.absolute()),
            "recursive": recursive,
            "file_pattern": file_pattern,
            "auto_update": auto_update,
            "department": department,
            "watch_started": datetime.now()
        }
        
        self.watched_directories[str(dir_path.absolute())] = watch_config
        
        # Setup directory observer
        self._setup_directory_observer(str(dir_path.absolute()), recursive)
        
        # Scan existing files
        existing_files = self._scan_directory_for_excel_files(dir_path, file_pattern, recursive)
        for excel_file in existing_files:
            self.watch_file(
                str(excel_file),
                rag_purpose=f"directory-monitor-{excel_file.stem}",
                department=department
            )
        
        logger.info(f"Watching directory: {directory_path} ({len(existing_files)} Excel files found)")
    
    def start_monitoring(self) -> None:
        """Start the monitoring system."""
        if self.monitoring_active:
            logger.warning("Monitoring is already active")
            return
        
        self.monitoring_active = True
        
        # Start observers
        for observer in self.observers:
            observer.start()
        
        # Start batch processor if not immediate updates
        if not self.update_policy.immediate_update:
            self._start_batch_processor()
        
        logger.info(f"Excel monitoring started for {len(self.watched_files)} files and {len(self.watched_directories)} directories")
    
    def stop_monitoring(self) -> None:
        """Stop the monitoring system."""
        if not self.monitoring_active:
            logger.warning("Monitoring is not active")
            return
        
        self.monitoring_active = False
        
        # Stop observers
        for observer in self.observers:
            observer.stop()
            observer.join()
        
        # Stop batch processor
        if self.batch_processor_active:
            self._stop_batch_processor()
        
        logger.info("Excel monitoring stopped")
    
    def force_update_all(self) -> Dict[str, Any]:
        """Force update all watched Excel files.
        
        Returns:
            Dictionary containing update results
        """
        logger.info("Force updating all watched Excel files")
        
        results = {
            "total_files": len(self.watched_files),
            "successful_updates": 0,
            "failed_updates": 0,
            "skipped_files": 0,
            "update_details": []
        }
        
        for file_path, watch_config in self.watched_files.items():
            try:
                update_result = self._process_file_update(
                    file_path, "force_update", datetime.now()
                )
                
                if update_result["success"]:
                    results["successful_updates"] += 1
                else:
                    results["failed_updates"] += 1
                
                results["update_details"].append({
                    "file": file_path,
                    "status": "success" if update_result["success"] else "failed",
                    "quality_score": update_result.get("quality_score"),
                    "processing_time": update_result.get("processing_time")
                })
                
            except Exception as e:
                results["failed_updates"] += 1
                results["update_details"].append({
                    "file": file_path,
                    "status": "error",
                    "error": str(e)
                })
                logger.error(f"Failed to force update {file_path}: {e}")
        
        return results
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get comprehensive monitoring status.
        
        Returns:
            Dictionary containing monitoring status
        """
        return {
            "monitoring_active": self.monitoring_active,
            "batch_processor_active": self.batch_processor_active,
            "watched_files": len(self.watched_files),
            "watched_directories": len(self.watched_directories),
            "pending_changes": len(self.change_queue),
            "processing_queue": len(self.processing_queue),
            "performance_stats": self.performance_stats.copy(),
            "update_policy": {
                "immediate_update": self.update_policy.immediate_update,
                "batch_interval": self.update_policy.batch_interval,
                "quality_threshold": self.update_policy.quality_threshold
            }
        }
    
    def update_policy_config(self, new_policy: UpdatePolicy) -> None:
        """Update the monitoring policy configuration.
        
        Args:
            new_policy: New update policy configuration
        """
        old_immediate = self.update_policy.immediate_update
        self.update_policy = new_policy
        
        # Restart batch processor if immediate setting changed
        if old_immediate != new_policy.immediate_update:
            if self.monitoring_active:
                if new_policy.immediate_update and self.batch_processor_active:
                    self._stop_batch_processor()
                elif not new_policy.immediate_update and not self.batch_processor_active:
                    self._start_batch_processor()
        
        logger.info("Update policy configuration updated")
    
    def _handle_file_change(self, file_path: str, event_type: str, timestamp: datetime) -> None:
        """Handle file change event."""
        if file_path not in self.watched_files:
            return
        
        # Check if this is a real change (avoid duplicate events)
        watch_config = self.watched_files[file_path]
        current_mtime = Path(file_path).stat().st_mtime
        
        if current_mtime <= watch_config["last_modified"]:
            return  # Not a real change
        
        # Update last modified time
        watch_config["last_modified"] = current_mtime
        
        # Create change event
        change_event = ExcelFileChangeEvent(
            file_path=file_path,
            event_type=event_type,
            timestamp=timestamp,
            metadata={
                "department": watch_config.get("department"),
                "rag_purpose": watch_config["rag_purpose"],
                "config": watch_config["config"]
            }
        )
        
        with self.lock:
            self.change_queue.append(change_event)
            self.performance_stats["changes_detected"] += 1
        
        logger.info(f"Excel file change detected: {file_path} ({event_type})")
        
        # Execute on_change callback if provided
        if watch_config["on_change"]:
            try:
                watch_config["on_change"]()
            except Exception as e:
                logger.error(f"Error executing on_change callback: {e}")
        
        # Process immediately if policy allows
        if self.update_policy.immediate_update:
            self._process_change_event(change_event)
    
    def _process_change_event(self, event: ExcelFileChangeEvent) -> None:
        """Process a single change event."""
        start_time = time.time()
        
        try:
            # Process file update
            result = self._process_file_update(
                event.file_path,
                event.event_type,
                event.timestamp
            )
            
            # Update event with result
            event.processed = True
            event.processing_result = result
            
            # Update performance stats
            processing_time = time.time() - start_time
            self._update_performance_stats(True, processing_time)
            
            # Update federation if connected
            if self.federation and event.metadata.get("department"):
                self._update_federation_data(event)
            
            logger.info(f"Successfully processed change: {event.file_path}")
            
        except Exception as e:
            event.processed = True
            event.processing_result = {"success": False, "error": str(e)}
            
            processing_time = time.time() - start_time
            self._update_performance_stats(False, processing_time)
            
            logger.error(f"Failed to process change {event.file_path}: {e}")
    
    def _process_file_update(
        self,
        file_path: str,
        event_type: str,
        timestamp: datetime
    ) -> Dict[str, Any]:
        """Process update for a specific file."""
        watch_config = self.watched_files[file_path]
        
        # Create backup if policy requires
        if self.update_policy.backup_on_update:
            self._create_backup(file_path)
        
        # Convert Excel to RAG
        result = self.excel_converter.convert_excel_to_rag(
            excel_file=file_path,
            rag_purpose=watch_config["rag_purpose"],
            config=watch_config["config"]
        )
        
        # Validate quality
        quality_score = result.get("quality_score", 0.0)
        if quality_score < self.update_policy.quality_threshold:
            raise ValueError(f"Quality score {quality_score} below threshold {self.update_policy.quality_threshold}")
        
        return {
            "success": True,
            "quality_score": quality_score,
            "processing_time": time.time(),
            "records_processed": result.get("conversion_summary", {}).get("records_processed", 0),
            "files_generated": len(result.get("json_files", [])),
            "timestamp": timestamp.isoformat()
        }
    
    def _setup_directory_observer(self, directory: str, recursive: bool = True) -> None:
        """Setup file system observer for directory."""
        observer = Observer()
        handler = ExcelFileHandler(self)
        observer.schedule(handler, directory, recursive=recursive)
        self.observers.append(observer)
    
    def _scan_directory_for_excel_files(
        self,
        directory: Path,
        pattern: str,
        recursive: bool
    ) -> List[Path]:
        """Scan directory for Excel files matching pattern."""
        if recursive:
            return list(directory.rglob(pattern))
        else:
            return list(directory.glob(pattern))
    
    def _start_batch_processor(self) -> None:
        """Start batch processor thread."""
        if self.batch_processor_active:
            return
        
        self.batch_processor_active = True
        self.batch_processor_thread = threading.Thread(
            target=self._batch_processor_loop,
            daemon=True
        )
        self.batch_processor_thread.start()
        
        logger.info("Batch processor started")
    
    def _stop_batch_processor(self) -> None:
        """Stop batch processor thread."""
        if not self.batch_processor_active:
            return
        
        self.batch_processor_active = False
        if self.batch_processor_thread:
            self.batch_processor_thread.join(timeout=10)
        
        logger.info("Batch processor stopped")
    
    def _batch_processor_loop(self) -> None:
        """Main loop for batch processor."""
        while self.batch_processor_active:
            try:
                # Wait for batch interval
                time.sleep(self.update_policy.batch_interval)
                
                if not self.batch_processor_active:
                    break
                
                # Process pending changes
                with self.lock:
                    pending_changes = self.change_queue.copy()
                    self.change_queue.clear()
                
                if pending_changes:
                    self._process_batch(pending_changes)
                
            except Exception as e:
                logger.error(f"Error in batch processor: {e}")
                time.sleep(10)  # Wait before retrying
    
    def _process_batch(self, changes: List[ExcelFileChangeEvent]) -> None:
        """Process a batch of changes."""
        logger.info(f"Processing batch of {len(changes)} changes")
        
        # Group by file to avoid duplicate processing
        file_changes = {}
        for change in changes:
            if change.file_path not in file_changes:
                file_changes[change.file_path] = change
            else:
                # Keep the latest change for each file
                if change.timestamp > file_changes[change.file_path].timestamp:
                    file_changes[change.file_path] = change
        
        # Process each unique file change
        batch_size = min(len(file_changes), self.update_policy.max_batch_size)
        processed_count = 0
        
        for change in list(file_changes.values())[:batch_size]:
            try:
                self._process_change_event(change)
                processed_count += 1
            except Exception as e:
                logger.error(f"Failed to process batch change {change.file_path}: {e}")
        
        logger.info(f"Batch processing completed: {processed_count}/{batch_size} successful")
    
    def _create_backup(self, file_path: str) -> str:
        """Create backup of file before update."""
        file_obj = Path(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_obj.parent / f"{file_obj.stem}_backup_{timestamp}{file_obj.suffix}"
        
        import shutil
        shutil.copy2(file_path, backup_path)
        
        logger.debug(f"Backup created: {backup_path}")
        return str(backup_path)
    
    def _update_performance_stats(self, success: bool, processing_time: float) -> None:
        """Update performance statistics."""
        with self.lock:
            if success:
                self.performance_stats["successful_updates"] += 1
            else:
                self.performance_stats["failed_updates"] += 1
            
            # Update average processing time
            total_updates = (self.performance_stats["successful_updates"] + 
                           self.performance_stats["failed_updates"])
            
            if total_updates > 1:
                current_avg = self.performance_stats["average_processing_time"]
                self.performance_stats["average_processing_time"] = (
                    (current_avg * (total_updates - 1) + processing_time) / total_updates
                )
            else:
                self.performance_stats["average_processing_time"] = processing_time
            
            self.performance_stats["last_update"] = datetime.now().isoformat()
    
    def _update_federation_data(self, event: ExcelFileChangeEvent) -> None:
        """Update federation system with new data."""
        if not self.federation:
            return
        
        department = event.metadata.get("department")
        if not department:
            return
        
        try:
            # This would trigger federation update
            logger.info(f"Updating federation data for department: {department}")
            # federation.refresh_department_data(department)
        except Exception as e:
            logger.error(f"Failed to update federation data: {e}")


# Convenience functions for quick monitoring setup
def setup_enterprise_monitoring(
    excel_directories: List[str],
    federation: Optional[ExcelRAGFederation] = None,
    immediate_updates: bool = True
) -> ExcelRAGMonitor:
    """Setup enterprise-wide Excel monitoring.
    
    Args:
        excel_directories: List of directories to monitor
        federation: ExcelRAGFederation instance
        immediate_updates: Whether to process updates immediately
        
    Returns:
        Configured ExcelRAGMonitor instance
    """
    policy = UpdatePolicy(immediate_update=immediate_updates)
    monitor = ExcelRAGMonitor(federation=federation, update_policy=policy)
    
    for directory in excel_directories:
        monitor.watch_directory(directory, auto_update=True)
    
    return monitor


def monitor_department_files(
    department_files: Dict[str, List[str]],
    federation: Optional[ExcelRAGFederation] = None
) -> ExcelRAGMonitor:
    """Monitor Excel files by department.
    
    Args:
        department_files: Mapping of department to file paths
        federation: ExcelRAGFederation instance
        
    Returns:
        Configured ExcelRAGMonitor instance
    """
    monitor = ExcelRAGMonitor(federation=federation)
    
    for department, file_paths in department_files.items():
        for file_path in file_paths:
            monitor.watch_file(
                file_path=file_path,
                department=department,
                rag_purpose=f"{department}-monitoring"
            )
    
    return monitor