

import cv2
import numpy as np
from typing import Dict, List, AsyncGenerator, Tuple
import asyncio
import time
import logging
from datetime import datetime
import uuid

from models import PersonDetection, PersonType, BoundingBox

logger = logging.getLogger(__name__)


class VideoProcessor:
    """
    Core video processing engine for person detection and tracking
    Uses OpenCV HOG descriptor for person detection
    """
    
    def __init__(self):
        """Initialize video processor with detection model"""
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        
        
        self.min_confidence = 0.5
        self.hit_threshold = 0.0
        self.win_stride = (8, 8)
        self.padding = (8, 8)
        self.scale = 1.05
        
        
        self.tracked_persons = {}
        self.next_person_id = 1
        
        logger.info("VideoProcessor initialized")
    
    
    async def process_video(self, video_path: str, video_id: str) -> Dict:
        """
        Process complete video file and return detection results
        
        Args:
            video_path: Path to video file
            video_id: Unique video identifier
            
        Returns:
            Dictionary containing detections and metadata
        """
        logger.info(f"Starting video analysis: {video_path}")
        
        start_time = time.time()
        
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
        
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        logger.info(f"Video properties - Frames: {total_frames}, FPS: {fps}")
        
        
        self.tracked_persons = {}
        self.next_person_id = 1
        
        frame_number = 0
        detections_per_frame = []
        
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            frame_number += 1
            
            
            if frame_number % 5 != 0:
                continue
            
            
            frame_detections = self._detect_persons_in_frame(
                frame,
                frame_number,
                fps
            )
            
            detections_per_frame.append({
                'frame': frame_number,
                'detections': frame_detections
            })
            
            
            if frame_number % 50 == 0:
                await asyncio.sleep(0.01)
                logger.debug(f"Processed frame {frame_number}/{total_frames}")
        
        cap.release()
        
        
        person_detections = self._aggregate_person_tracks(
            detections_per_frame,
            fps
        )
        
        processing_time = time.time() - start_time
        
        logger.info(
            f"Video analysis complete - {len(person_detections)} persons detected "
            f"in {processing_time:.2f}s"
        )
        
        return {
            'video_id': video_id,
            'total_frames': total_frames,
            'fps': fps,
            'detections': person_detections,
            'processing_time': processing_time
        }
    
    
    async def process_video_streaming(
        self,
        video_path: str
    ) -> AsyncGenerator[Dict, None]:
        """
        Process video with real-time streaming updates
        
        Args:
            video_path: Path to video file
            
        Yields:
            Progress updates and detection results
        """
        logger.info(f"Starting streaming analysis: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            yield {
                'status': 'error',
                'message': 'Cannot open video file'
            }
            return
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
    
        self.tracked_persons = {}
        self.next_person_id = 1
        
        frame_number = 0
        all_detections = []
        
        yield {
            'status': 'processing',
            'progress_percent': 0,
            'current_frame': 0,
            'total_frames': total_frames,
            'detections_so_far': 0
        }
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            frame_number += 1
            
            
            if frame_number % 5 == 0:
                detections = self._detect_persons_in_frame(frame, frame_number, fps)
                all_detections.extend(detections)
                
                
                progress = (frame_number / total_frames) * 100
                
                yield {
                    'status': 'processing',
                    'progress_percent': progress,
                    'current_frame': frame_number,
                    'total_frames': total_frames,
                    'detections_so_far': len(self.tracked_persons)
                }
            
            
            if frame_number % 20 == 0:
                await asyncio.sleep(0.01)
        
        cap.release()
        
        
        person_tracks = self._aggregate_person_tracks(
            [{'frame': i, 'detections': all_detections} for i in range(total_frames)],
            fps
        )
        
        yield {
            'status': 'completed',
            'results': {
                'detections': person_tracks,
                'total_frames': total_frames,
                'fps': fps
            }
        }
    
    
    def _detect_persons_in_frame(
        self,
        frame: np.ndarray,
        frame_number: int,
        fps: int
    ) -> List[Dict]:
        """
        Detect persons in a single frame
        
        Args:
            frame: Video frame
            frame_number: Frame index
            fps: Video FPS
            
        Returns:
            List of detections in frame
        """
    
        height, width = frame.shape[:2]
        scale_factor = 1.0
        
        if width > 1280:
            scale_factor = 1280.0 / width
            new_width = 1280
            new_height = int(height * scale_factor)
            frame = cv2.resize(frame, (new_width, new_height))
        
        
        try:
            boxes, weights = self.hog.detectMultiScale(
                frame,
                winStride=self.win_stride,
                padding=self.padding,
                scale=self.scale,
                hitThreshold=self.hit_threshold
            )
        except Exception as e:
            logger.warning(f"Detection failed on frame {frame_number}: {e}")
            return []
        
        detections = []
        
        for (x, y, w, h), weight in zip(boxes, weights):
            confidence = float(weight[0]) if isinstance(weight, np.ndarray) else float(weight)
            
            
            if confidence < self.min_confidence:
                continue
            
            
            if scale_factor != 1.0:
                x = int(x / scale_factor)
                y = int(y / scale_factor)
                w = int(w / scale_factor)
                h = int(h / scale_factor)
            
            
            person_type = self._classify_person(
                x, y, w, h,
                width, height,
                frame_number
            )
            
            
            person_id = self._track_person(x, y, w, h, frame_number)
            
            detections.append({
                'person_id': person_id,
                'person_type': person_type,
                'confidence': min(confidence, 1.0),
                'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                'frame': frame_number,
                'timestamp': frame_number / fps
            })
        
        return detections
    
    
    def _classify_person(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        frame_width: int,
        frame_height: int,
        frame_number: int
    ) -> PersonType:
        """
        Classify detected person as employee or customer
        
        Uses heuristics based on:
        - Position in frame (employees often in specific zones)
        - Appearance duration (employees stay longer)
        - Movement patterns (employees have different behavior)
        
        Args:
            x, y, w, h: Bounding box coordinates
            frame_width, frame_height: Frame dimensions
            frame_number: Current frame number
            
        Returns:
            PersonType classification
        """
        
        center_x = x + w / 2
        center_y = y + h / 2
        
        
        norm_x = center_x / frame_width
        norm_y = center_y / frame_height
        
        
        
        if norm_x < 0.2 or norm_x > 0.8 or norm_y < 0.2 or norm_y > 0.8:
            
            return PersonType.EMPLOYEE
        
        
        elif 0.3 < norm_x < 0.7 and 0.3 < norm_y < 0.7:
            return PersonType.CUSTOMER
        
        
        
        elif norm_y < 0.3:
            return PersonType.EMPLOYEE
        
        
        else:
            return PersonType.CUSTOMER
    
    
    def _track_person(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        frame_number: int
    ) -> str:
        """
        Track person across frames using simple centroid tracking
        
        Args:
            x, y, w, h: Bounding box coordinates
            frame_number: Current frame number
            
        Returns:
            Person ID
        """
        center_x = x + w / 2
        center_y = y + h / 2
        
        
        min_distance = float('inf')
        matched_id = None
        
        for person_id, track_data in self.tracked_persons.items():
            last_center = track_data['last_center']
            last_frame = track_data['last_frame']
            
    
            if frame_number - last_frame > 10:
                continue
            
            distance = np.sqrt(
                (center_x - last_center[0])**2 +
                (center_y - last_center[1])**2
            )
            
            if distance < min_distance and distance < 100:
                min_distance = distance
                matched_id = person_id
        
        
        if matched_id:
            self.tracked_persons[matched_id]['last_center'] = (center_x, center_y)
            self.tracked_persons[matched_id]['last_frame'] = frame_number
            self.tracked_persons[matched_id]['frames'].append(frame_number)
            self.tracked_persons[matched_id]['trajectory'].append((center_x, center_y))
            return matched_id
        else:
            
            new_id = f"person_{self.next_person_id:04d}"
            self.next_person_id += 1
            
            self.tracked_persons[new_id] = {
                'last_center': (center_x, center_y),
                'last_frame': frame_number,
                'first_frame': frame_number,
                'frames': [frame_number],
                'trajectory': [(center_x, center_y)]
            }
            
            return new_id
    
    
    def _aggregate_person_tracks(
        self,
        detections_per_frame: List[Dict],
        fps: int
    ) -> List[PersonDetection]:
        """
        Aggregate frame-level detections into person tracks
        
        Args:
            detections_per_frame: All detections per frame
            fps: Video FPS
            
        Returns:
            List of PersonDetection objects
        """
        person_tracks = {}
        
        
        for frame_data in detections_per_frame:
            for detection in frame_data['detections']:
                person_id = detection['person_id']
                
                if person_id not in person_tracks:
                    person_tracks[person_id] = []
                
                person_tracks[person_id].append(detection)
        
        
        results = []
        
        for person_id, detections in person_tracks.items():
            if len(detections) == 0:
                continue
            
        
            detections.sort(key=lambda d: d['frame'])
            
            first_detection = detections[0]
            last_detection = detections[-1]
            
            
            avg_confidence = sum(d['confidence'] for d in detections) / len(detections)
            
            
            person_types = [d['person_type'] for d in detections]
            person_type = max(set(person_types), key=person_types.count)
            
        
            dwell_time = (last_detection['frame'] - first_detection['frame']) / fps
            
            
            trajectory = [
                (d['bbox']['x'] + d['bbox']['width']/2,
                 d['bbox']['y'] + d['bbox']['height']/2)
                for d in detections
            ]
            
            
            bbox = BoundingBox(**last_detection['bbox'])
            
            results.append(PersonDetection(
                person_id=person_id,
                person_type=person_type,
                confidence=avg_confidence,
                bbox=bbox,
                first_seen_frame=first_detection['frame'],
                last_seen_frame=last_detection['frame'],
                total_frames_visible=len(detections),
                dwell_time_seconds=dwell_time,
                trajectory=trajectory,
                metadata={
                    'first_timestamp': first_detection['timestamp'],
                    'last_timestamp': last_detection['timestamp']
                }
            ))
        
        return results
