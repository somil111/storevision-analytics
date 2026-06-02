

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
import statistics

from models import DetectionMetrics, PersonDetection, PersonType

logger = logging.getLogger(__name__)


class AnalyticsEngine:
   
    
    def __init__(self):
        """Initialize analytics engine"""
        self.metrics_cache = {}
        self.historical_data = []
        
        logger.info("AnalyticsEngine initialized")
    
    
    async def calculate_metrics(self, results: Dict) -> DetectionMetrics:
        """
        Calculate comprehensive metrics from video analysis results
        
        Args:
            results: Video processing results containing detections
            
        Returns:
            DetectionMetrics object with aggregated statistics
        """
        detections = results.get('detections', [])
        
        logger.info(f"Calculating metrics from {len(detections)} detections")
        
        if len(detections) == 0:
            return DetectionMetrics(
                total_detections=0,
                employee_count=0,
                customer_count=0,
                unknown_count=0,
                average_confidence=0.0,
                average_dwell_time_seconds=0.0,
                peak_occupancy=0,
                total_entries=0,
                total_exits=0,
                time_window_start=datetime.utcnow().isoformat(),
                time_window_end=datetime.utcnow().isoformat()
            )
        
        
        employee_count = sum(
            1 for d in detections
            if d.person_type == PersonType.EMPLOYEE
        )
        customer_count = sum(
            1 for d in detections
            if d.person_type == PersonType.CUSTOMER
        )
        unknown_count = sum(
            1 for d in detections
            if d.person_type == PersonType.UNKNOWN
        )
        
    
        avg_confidence = statistics.mean(
            d.confidence for d in detections
        ) if detections else 0.0
        
        
        avg_dwell_time = statistics.mean(
            d.dwell_time_seconds for d in detections
        ) if detections else 0.0
        
        
        peak_occupancy = self._calculate_peak_occupancy(detections)
        
        
        total_entries = len(detections)  
        total_exits = len(detections)    
        
        
        fps = results.get('fps', 30)
        total_frames = results.get('total_frames', 0)
        
        video_duration = total_frames / fps if fps > 0 else 0
        
        time_start = datetime.utcnow() - timedelta(seconds=video_duration)
        time_end = datetime.utcnow()
        
        metrics = DetectionMetrics(
            total_detections=len(detections),
            employee_count=employee_count,
            customer_count=customer_count,
            unknown_count=unknown_count,
            average_confidence=round(avg_confidence, 3),
            average_dwell_time_seconds=round(avg_dwell_time, 2),
            peak_occupancy=peak_occupancy,
            total_entries=total_entries,
            total_exits=total_exits,
            time_window_start=time_start.isoformat(),
            time_window_end=time_end.isoformat()
        )
        
    
        video_id = results.get('video_id', 'unknown')
        self.metrics_cache[video_id] = metrics
        
        
        self.historical_data.append({
            'timestamp': datetime.utcnow(),
            'video_id': video_id,
            'metrics': metrics
        })
        
        logger.info(
            f"Metrics calculated - Total: {metrics.total_detections}, "
            f"Employees: {employee_count}, Customers: {customer_count}"
        )
        
        return metrics
    
    
    def _calculate_peak_occupancy(self, detections: List[PersonDetection]) -> int:
        """
        Calculate peak occupancy from detection data
        
        Args:
            detections: List of PersonDetection objects
            
        Returns:
            Maximum number of concurrent persons
        """
        if not detections:
            return 0
        
        occupancy_timeline = {}
        
        for detection in detections:
            for frame in range(detection.first_seen_frame, detection.last_seen_frame + 1):
                if frame not in occupancy_timeline:
                    occupancy_timeline[frame] = 0
                occupancy_timeline[frame] += 1
        
        
        peak = max(occupancy_timeline.values()) if occupancy_timeline else 0
        
        return peak
    
    
    async def get_aggregated_metrics(
        self,
        store_id: Optional[str] = None,
        time_window_hours: int = 24
    ) -> DetectionMetrics:
        """
        Get aggregated metrics across multiple analyses
        
        Args:
            store_id: Optional store filter
            time_window_hours: Time window for aggregation
            
        Returns:
            Aggregated DetectionMetrics
        """
        logger.info(
            f"Aggregating metrics - Store: {store_id}, "
            f"Window: {time_window_hours}h"
        )
        
        
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        filtered_data = [
            entry for entry in self.historical_data
            if entry['timestamp'] >= cutoff_time
        ]
        
        
        if store_id:
            filtered_data = [
                entry for entry in filtered_data
                if entry['video_id'].startswith(store_id)
            ]
        
        if not filtered_data:
            
            return DetectionMetrics(
                total_detections=0,
                employee_count=0,
                customer_count=0,
                unknown_count=0,
                average_confidence=0.0,
                average_dwell_time_seconds=0.0,
                peak_occupancy=0,
                total_entries=0,
                total_exits=0,
                time_window_start=cutoff_time.isoformat(),
                time_window_end=datetime.utcnow().isoformat()
            )
        
        
        total_detections = sum(
            entry['metrics'].total_detections
            for entry in filtered_data
        )
        
        employee_count = sum(
            entry['metrics'].employee_count
            for entry in filtered_data
        )
        
        customer_count = sum(
            entry['metrics'].customer_count
            for entry in filtered_data
        )
        
        unknown_count = sum(
            entry['metrics'].unknown_count
            for entry in filtered_data
        )
        
        
        avg_confidence = statistics.mean(
            entry['metrics'].average_confidence
            for entry in filtered_data
        )
        
        
        avg_dwell_time = statistics.mean(
            entry['metrics'].average_dwell_time_seconds
            for entry in filtered_data
        )
        
        
        peak_occupancy = max(
            entry['metrics'].peak_occupancy
            for entry in filtered_data
        )
        
        
        total_entries = sum(
            entry['metrics'].total_entries
            for entry in filtered_data
        )
        
        total_exits = sum(
            entry['metrics'].total_exits
            for entry in filtered_data
        )
        
        return DetectionMetrics(
            total_detections=total_detections,
            employee_count=employee_count,
            customer_count=customer_count,
            unknown_count=unknown_count,
            average_confidence=round(avg_confidence, 3),
            average_dwell_time_seconds=round(avg_dwell_time, 2),
            peak_occupancy=peak_occupancy,
            total_entries=total_entries,
            total_exits=total_exits,
            time_window_start=cutoff_time.isoformat(),
            time_window_end=datetime.utcnow().isoformat()
        )
    
    
    def get_trend_analysis(
        self,
        metric_name: str,
        time_window_hours: int = 24
    ) -> Dict:
        """
        Analyze trends for specific metric
        
        Args:
            metric_name: Name of metric to analyze
            time_window_hours: Time window for trend analysis
            
        Returns:
            Trend analysis results
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        filtered_data = [
            entry for entry in self.historical_data
            if entry['timestamp'] >= cutoff_time
        ]
        
        if not filtered_data:
            return {
                'metric': metric_name,
                'trend': 'insufficient_data',
                'data_points': 0
            }
        
        
        values = []
        timestamps = []
        
        for entry in filtered_data:
            metrics = entry['metrics']
            
            if hasattr(metrics, metric_name):
                values.append(getattr(metrics, metric_name))
                timestamps.append(entry['timestamp'])
        
        if len(values) < 2:
            return {
                'metric': metric_name,
                'trend': 'insufficient_data',
                'data_points': len(values)
            }
        
    
        avg_first_half = statistics.mean(values[:len(values)//2])
        avg_second_half = statistics.mean(values[len(values)//2:])
        
        trend = 'increasing' if avg_second_half > avg_first_half else 'decreasing'
        
        return {
            'metric': metric_name,
            'trend': trend,
            'data_points': len(values),
            'min_value': min(values),
            'max_value': max(values),
            'avg_value': statistics.mean(values),
            'current_value': values[-1],
            'time_window_start': timestamps[0].isoformat(),
            'time_window_end': timestamps[-1].isoformat()
        }
    
    
    def get_comparison(
        self,
        store_id_1: str,
        store_id_2: str,
        time_window_hours: int = 24
    ) -> Dict:
        """
        Compare metrics between two stores
        
        Args:
            store_id_1: First store ID
            store_id_2: Second store ID
            time_window_hours: Time window for comparison
            
        Returns:
            Comparison results
        """
        metrics_1 = self.get_aggregated_metrics(store_id_1, time_window_hours)
        metrics_2 = self.get_aggregated_metrics(store_id_2, time_window_hours)
        
        return {
            'store_1': {
                'store_id': store_id_1,
                'metrics': metrics_1
            },
            'store_2': {
                'store_id': store_id_2,
                'metrics': metrics_2
            },
            'comparison': {
                'detection_difference': metrics_1.total_detections - metrics_2.total_detections,
                'employee_difference': metrics_1.employee_count - metrics_2.employee_count,
                'customer_difference': metrics_1.customer_count - metrics_2.customer_count
            }
        }
    
    
    def clear_cache(self):
        """Clear metrics cache"""
        self.metrics_cache.clear()
        logger.info("Metrics cache cleared")
    
    
    def clear_historical_data(self):
        """Clear historical data"""
        self.historical_data.clear()
        logger.info("Historical data cleared")
