

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import uuid
import logging
from collections import deque

from models import EventRecord, EventType, PersonDetection, PersonType

logger = logging.getLogger(__name__)


class EventStreamManager:
    """
    Manages event generation and streaming for real-time updates
    Converts detection results into actionable events
    """
    
    def __init__(self, max_event_buffer: int = 1000):
        """
        Initialize event stream manager
        
        Args:
            max_event_buffer: Maximum events to buffer for streaming
        """
        self.event_buffer = deque(maxlen=max_event_buffer)
        self.event_subscribers = []
        self.is_running = True
        
        logger.info("EventStreamManager initialized")
    
    
    async def create_events_from_results(
        self,
        results: Dict
    ) -> List[EventRecord]:
        """
        Generate events from video analysis results
        
        Args:
            results: Video processing results containing detections
            
        Returns:
            List of generated events
        """
        events = []
        detections = results.get('detections', [])
        
        logger.info(f"Generating events from {len(detections)} detections")
        
        for detection in detections:
            # Generate person detected event
            event = self._create_detection_event(
                detection,
                results.get('video_id', 'unknown')
            )
            events.append(event)
            
            
            self.event_buffer.append(event.dict())
            
            
            if detection.first_seen_frame == detection.last_seen_frame or \
               detection.total_frames_visible <= 2:
                entry_event = self._create_entry_event(detection, results.get('video_id'))
                events.append(entry_event)
                self.event_buffer.append(entry_event.dict())
            
            
            if detection.dwell_time_seconds > 30:
                dwell_event = self._create_dwell_event(detection, results.get('video_id'))
                events.append(dwell_event)
                self.event_buffer.append(dwell_event.dict())
        
        logger.info(f"Generated {len(events)} events")
        
        return events
    
    
    def _create_detection_event(
        self,
        detection: PersonDetection,
        video_id: str
    ) -> EventRecord:
        """
        Create person detected event
        
        Args:
            detection: PersonDetection object
            video_id: Video identifier
            
        Returns:
            EventRecord for person detection
        """
        return EventRecord(
            event_id=str(uuid.uuid4()),
            event_type=EventType.PERSON_DETECTED,
            timestamp=datetime.utcnow().isoformat(),
            store_id=video_id.split('_')[0] if '_' in video_id else 'unknown',
            camera_id=video_id.split('_')[1] if '_' in video_id and len(video_id.split('_')) > 1 else 'unknown',
            person_id=detection.person_id,
            person_type=detection.person_type,
            bbox=detection.bbox,
            metadata={
                'confidence': detection.confidence,
                'first_frame': detection.first_seen_frame,
                'last_frame': detection.last_seen_frame,
                'dwell_time': detection.dwell_time_seconds,
                'frames_visible': detection.total_frames_visible
            }
        )
    
    
    def _create_entry_event(
        self,
        detection: PersonDetection,
        video_id: str
    ) -> EventRecord:
        """
        Create person entered event
        
        Args:
            detection: PersonDetection object
            video_id: Video identifier
            
        Returns:
            EventRecord for person entry
        """
        return EventRecord(
            event_id=str(uuid.uuid4()),
            event_type=EventType.PERSON_ENTERED,
            timestamp=datetime.utcnow().isoformat(),
            store_id=video_id.split('_')[0] if '_' in video_id else 'unknown',
            camera_id=video_id.split('_')[1] if '_' in video_id and len(video_id.split('_')) > 1 else 'unknown',
            person_id=detection.person_id,
            person_type=detection.person_type,
            bbox=detection.bbox,
            metadata={
                'entry_frame': detection.first_seen_frame,
                'entry_position': detection.trajectory[0] if detection.trajectory else None
            }
        )
    
    
    def _create_exit_event(
        self,
        detection: PersonDetection,
        video_id: str
    ) -> EventRecord:
        """
        Create person exited event
        
        Args:
            detection: PersonDetection object
            video_id: Video identifier
            
        Returns:
            EventRecord for person exit
        """
        return EventRecord(
            event_id=str(uuid.uuid4()),
            event_type=EventType.PERSON_EXITED,
            timestamp=datetime.utcnow().isoformat(),
            store_id=video_id.split('_')[0] if '_' in video_id else 'unknown',
            camera_id=video_id.split('_')[1] if '_' in video_id and len(video_id.split('_')) > 1 else 'unknown',
            person_id=detection.person_id,
            person_type=detection.person_type,
            bbox=detection.bbox,
            metadata={
                'exit_frame': detection.last_seen_frame,
                'exit_position': detection.trajectory[-1] if detection.trajectory else None,
                'total_dwell_time': detection.dwell_time_seconds
            }
        )
    
    
    def _create_dwell_event(
        self,
        detection: PersonDetection,
        video_id: str
    ) -> EventRecord:
        """
        Create dwell time threshold event
        
        Args:
            detection: PersonDetection object
            video_id: Video identifier
            
        Returns:
            EventRecord for dwell time threshold
        """
        return EventRecord(
            event_id=str(uuid.uuid4()),
            event_type=EventType.DWELL_TIME_THRESHOLD,
            timestamp=datetime.utcnow().isoformat(),
            store_id=video_id.split('_')[0] if '_' in video_id else 'unknown',
            camera_id=video_id.split('_')[1] if '_' in video_id and len(video_id.split('_')) > 1 else 'unknown',
            person_id=detection.person_id,
            person_type=detection.person_type,
            bbox=detection.bbox,
            metadata={
                'dwell_time_seconds': detection.dwell_time_seconds,
                'threshold_seconds': 30,
                'alert_level': 'info' if detection.dwell_time_seconds < 60 else 'warning'
            }
        )
    
    
    def _create_movement_event(
        self,
        detection: PersonDetection,
        video_id: str,
        from_position: tuple,
        to_position: tuple
    ) -> EventRecord:
        """
        Create movement detected event
        
        Args:
            detection: PersonDetection object
            video_id: Video identifier
            from_position: Starting position (x, y)
            to_position: Ending position (x, y)
            
        Returns:
            EventRecord for movement
        """
        return EventRecord(
            event_id=str(uuid.uuid4()),
            event_type=EventType.MOVEMENT_DETECTED,
            timestamp=datetime.utcnow().isoformat(),
            store_id=video_id.split('_')[0] if '_' in video_id else 'unknown',
            camera_id=video_id.split('_')[1] if '_' in video_id and len(video_id.split('_')) > 1 else 'unknown',
            person_id=detection.person_id,
            person_type=detection.person_type,
            bbox=detection.bbox,
            metadata={
                'from_position': from_position,
                'to_position': to_position,
                'trajectory_length': len(detection.trajectory)
            }
        )
    
    
    async def get_next_event(self) -> Optional[Dict]:
        """
        Get next event from buffer for SSE streaming
        
        Returns:
            Event dictionary or None if buffer empty
        """
        if len(self.event_buffer) > 0:
            return self.event_buffer.popleft()
        
        return None
    
    
    async def stream_events(self):
        """
        Async generator for streaming events to subscribers
        
        Yields:
            Event dictionaries
        """
        while self.is_running:
            if len(self.event_buffer) > 0:
                event = self.event_buffer.popleft()
                yield event
            else:
                await asyncio.sleep(0.1)
    
    
    def add_subscriber(self, subscriber_id: str):
        """
        Add event subscriber
        
        Args:
            subscriber_id: Unique subscriber identifier
        """
        if subscriber_id not in self.event_subscribers:
            self.event_subscribers.append(subscriber_id)
            logger.info(f"Event subscriber added: {subscriber_id}")
    
    
    def remove_subscriber(self, subscriber_id: str):
        """
        Remove event subscriber
        
        Args:
            subscriber_id: Subscriber identifier to remove
        """
        if subscriber_id in self.event_subscribers:
            self.event_subscribers.remove(subscriber_id)
            logger.info(f"Event subscriber removed: {subscriber_id}")
    
    
    def get_event_count(self) -> int:
        """
        Get current number of buffered events
        
        Returns:
            Number of events in buffer
        """
        return len(self.event_buffer)
    
    
    def clear_buffer(self):
        """Clear all buffered events"""
        self.event_buffer.clear()
        logger.info("Event buffer cleared")
    
    
    async def shutdown(self):
        """Shutdown event stream manager"""
        self.is_running = False
        self.event_buffer.clear()
        self.event_subscribers.clear()
        logger.info("EventStreamManager shutdown complete")
