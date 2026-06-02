

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Literal, Any
from datetime import datetime
from enum import Enum


class PersonType(str, Enum):
    """Person classification types"""
    EMPLOYEE = "employee"
    CUSTOMER = "customer"
    UNKNOWN = "unknown"


class EventType(str, Enum):
    """Event types for streaming"""
    PERSON_DETECTED = "person_detected"
    PERSON_ENTERED = "person_entered"
    PERSON_EXITED = "person_exited"
    ZONE_OCCUPIED = "zone_occupied"
    ZONE_VACANT = "zone_vacant"
    DWELL_TIME_THRESHOLD = "dwell_time_threshold"
    MOVEMENT_DETECTED = "movement_detected"


class VideoUploadResponse(BaseModel):
    """Response model for video upload"""
    video_id: str
    store_id: str
    camera_id: str
    filename: str
    size_bytes: int
    upload_timestamp: str


class AnalysisRequest(BaseModel):
    """Request model for video analysis"""
    video_id: str
    enable_tracking: bool = True
    enable_events: bool = True
    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0)


class BoundingBox(BaseModel):
    """Bounding box coordinates"""
    x: float
    y: float
    width: float
    height: float
    
    @field_validator('x', 'y', 'width', 'height')
    @classmethod
    def validate_positive(cls, v):
        if v < 0:
            raise ValueError("Coordinates must be positive")
        return v


class PersonDetection(BaseModel):
    """Person detection result"""
    person_id: str
    person_type: PersonType
    confidence: float = Field(..., ge=0.0, le=1.0)
    bbox: BoundingBox
    first_seen_frame: int
    last_seen_frame: int
    total_frames_visible: int
    dwell_time_seconds: float
    trajectory: List[tuple[float, float]]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EventRecord(BaseModel):
    """Event record for streaming and storage"""
    event_id: str
    event_type: EventType
    timestamp: str
    store_id: str
    camera_id: str
    person_id: Optional[str] = None
    person_type: Optional[PersonType] = None
    zone_id: Optional[str] = None
    bbox: Optional[BoundingBox] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DetectionMetrics(BaseModel):
    """Aggregated detection metrics"""
    total_detections: int
    employee_count: int
    customer_count: int
    unknown_count: int
    average_confidence: float
    average_dwell_time_seconds: float
    peak_occupancy: int
    total_entries: int
    total_exits: int
    time_window_start: str
    time_window_end: str


class AnalysisResponse(BaseModel):
    """Complete analysis response"""
    video_id: str
    status: Literal["completed", "failed", "partial"]
    detections: List[PersonDetection]
    events: List[EventRecord]
    metrics: DetectionMetrics
    processing_time_seconds: float
    warnings: List[str] = Field(default_factory=list)


class SystemHealth(BaseModel):
    """System health status"""
    status: Literal["healthy", "degraded", "unhealthy"]
    timestamp: str
    components: Dict[str, str]
    uptime_seconds: float
    warnings: List[str] = Field(default_factory=list)


class StreamingUpdate(BaseModel):
    """Real-time streaming update"""
    video_id: str
    progress_percent: float
    current_frame: int
    total_frames: int
    detections_so_far: int
    latest_detection: Optional[PersonDetection] = None
    latest_event: Optional[EventRecord] = None


class ZoneDefinition(BaseModel):
    """Store zone definition"""
    zone_id: str
    zone_name: str
    polygon_coords: List[tuple[float, float]]
    zone_type: Literal["entrance", "checkout", "product", "aisle", "storage"]
    
    @field_validator('polygon_coords')
    @classmethod
    def validate_polygon(cls, v):
        if len(v) < 3:
            raise ValueError("Polygon must have at least 3 vertices")
        return v


class StoreConfiguration(BaseModel):
    """Complete store configuration"""
    store_id: str
    store_name: str
    cameras: List[Dict[str, str]]
    zones: List[ZoneDefinition]
    operating_hours: Dict[str, str]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TrackingState(BaseModel):
    """Person tracking state"""
    person_id: str
    current_bbox: BoundingBox
    current_zone: Optional[str] = None
    velocity: tuple[float, float]
    is_stationary: bool
    frames_stationary: int
    last_update_frame: int


class AnomalyDetection(BaseModel):
    """Anomaly detection result"""
    anomaly_id: str
    anomaly_type: Literal["unusual_movement", "prolonged_dwell", "restricted_area", "crowd_formation"]
    severity: Literal["low", "medium", "high", "critical"]
    timestamp: str
    person_id: Optional[str] = None
    zone_id: Optional[str] = None
    description: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class PerformanceMetrics(BaseModel):
    """System performance metrics"""
    frames_per_second: float
    detection_latency_ms: float
    tracking_accuracy: float
    memory_usage_mb: float
    cpu_usage_percent: float
    gpu_usage_percent: Optional[float] = None
