# StoreVision Analytics Platform

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.9.0-red.svg)](https://opencv.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Production-grade CCTV intelligence system with real-time analytics for retail environments.

## Overview

StoreVision is an end-to-end store intelligence system that processes CCTV footage to detect, track, and classify persons (employees vs customers) in real-time. Built for engineers who solve real-world AI and system design problems at scale.

Visit the live dashboard: http://localhost:8000/static/index.html (after starting server)

## Architecture

### Core Components

- **Video Processor**: Person detection using OpenCV HOG descriptor, multi-object tracking, and classification
- **Event Stream Manager**: Real-time event generation and streaming via WebSockets and SSE
- **Analytics Engine**: Metrics calculation, trend analysis, and actionable insights
- **FastAPI Backend**: Production-ready REST API with async processing
- **Real-time Dashboard**: WebSocket-powered frontend for live monitoring

### Tech Stack

- **Backend**: Python 3.8+, FastAPI, Uvicorn
- **Computer Vision**: OpenCV, NumPy
- **Data Validation**: Pydantic
- **Frontend**: Vanilla JavaScript, WebSocket API
- **Deployment**: Docker-ready, localhost-based

## Features

### Detection & Tracking Pipeline
- Person detection using HOG descriptor
- Multi-object tracking across frames
- Employee vs customer classification
- Trajectory mapping and dwell time analysis

### Real-time Intelligence APIs
- Video upload and processing
- WebSocket streaming for live updates
- Server-Sent Events (SSE) for event streaming
- RESTful analytics endpoints

### Event Schema
- Person detected/entered/exited events
- Zone occupancy events
- Dwell time threshold alerts
- Movement detection events

### Production Readiness
- Async processing for scalability
- Comprehensive error handling
- Health check endpoints
- Structured logging
- Request validation with Pydantic

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)
- Git (for cloning repository)

### Quick Start

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/storevision-analytics.git
cd storevision-analytics
```

2. **Create virtual environment**:
```bash
python -m venv venv
```

3. **Activate virtual environment**:

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

4. **Install dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

5. **Start the server**:
```bash
python main.py
```

6. **Open browser**:
```
http://localhost:8000/static/index.html
```

### Docker Deployment

Build and run with Docker:

```bash
docker-compose up --build
```

Then access: http://localhost:8000/static/index.html

### Using the Batch Script (Windows)

```bash
START_SERVER.bat
```

## Usage

### Starting the Server

1. **From the backend directory**:
```bash
python main.py
```

2. **Access the platform**:
- Dashboard: http://localhost:8000/static/index.html
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Using the Dashboard

1. Open http://localhost:8000/static/index.html in your browser
2. Enter Store ID (e.g., "store_001")
3. Enter Camera ID (e.g., "camera_01")
4. Select MP4 video file
5. Click "Upload & Analyze"
6. View real-time processing progress
7. Review detection results and metrics

### API Endpoints

#### Upload Video
```bash
POST /api/v1/video/upload
Content-Type: multipart/form-data

Parameters:
- store_id: string
- camera_id: string
- video: file (MP4)
```

#### Analyze Video
```bash
POST /api/v1/video/analyze
Content-Type: application/json

Body:
{
  "video_id": "store_001_camera_01_timestamp",
  "enable_tracking": true,
  "enable_events": true,
  "confidence_threshold": 0.5
}
```

#### Get Metrics
```bash
GET /api/v1/analytics/metrics?store_id=store_001&time_window_hours=24
```

#### WebSocket Streaming
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/stream/analysis/{video_id}');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Progress:', data.progress_percent);
};
```

## System Design

### Person Classification Logic

The system classifies persons as employees or customers using spatial heuristics:

1. **Edge Zone Detection**: Persons in frame edges (0-20% or 80-100%) are likely employees
2. **Central Zone Detection**: Persons in center (30-70%) are likely customers
3. **Top Zone Analysis**: Top frame positions indicate checkout/service counters (employees)
4. **Behavior Analysis**: Dwell time and movement patterns provide additional signals

### Tracking Algorithm

Simple centroid-based tracking:
- Tracks person centers across frames
- Matches detections within 100-pixel radius
- Handles temporary occlusions (up to 10 frames)
- Generates unique IDs for each person

### Performance Optimization

- Frame sampling (every 5th frame) for efficiency
- Async processing for scalability
- Frame resizing for faster detection
- Event buffering with circular queue

## Data Models

### PersonDetection
```python
{
    "person_id": "person_0001",
    "person_type": "customer",  # employee, customer, unknown
    "confidence": 0.87,
    "bbox": {"x": 100, "y": 200, "width": 50, "height": 120},
    "first_seen_frame": 10,
    "last_seen_frame": 245,
    "total_frames_visible": 47,
    "dwell_time_seconds": 15.6,
    "trajectory": [(x1, y1), (x2, y2), ...]
}
```

### EventRecord
```python
{
    "event_id": "uuid",
    "event_type": "person_detected",
    "timestamp": "2024-01-15T10:30:00",
    "store_id": "store_001",
    "camera_id": "camera_01",
    "person_id": "person_0001",
    "person_type": "customer",
    "metadata": {...}
}
```

### DetectionMetrics
```python
{
    "total_detections": 25,
    "employee_count": 5,
    "customer_count": 20,
    "average_confidence": 0.82,
    "average_dwell_time_seconds": 23.4,
    "peak_occupancy": 8,
    "total_entries": 25,
    "total_exits": 23
}
```

## Configuration

### Detection Parameters
Adjust in `video_processor.py`:

```python
self.min_confidence = 0.5          # Minimum detection confidence
self.win_stride = (8, 8)           # HOG window stride
self.scale = 1.05                  # Detection scale factor
```

### Classification Thresholds
Modify in `_classify_person()` method:

```python
# Edge zone threshold (0-20% or 80-100% = employee)
if norm_x < 0.2 or norm_x > 0.8:
    return PersonType.EMPLOYEE
```

## Troubleshooting

### Video Upload Fails
- Ensure file is MP4 format
- Check file size (max 100MB recommended)
- Verify backend server is running

### Detection Quality Issues
- Increase `min_confidence` threshold
- Adjust `scale` parameter for different person sizes
- Ensure adequate lighting in footage

### Performance Concerns
- Increase frame sampling rate (process every 10th frame)
- Reduce input video resolution
- Enable hardware acceleration if available

## Development

### Project Structure
```
storevision_platform/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── models.py               # Pydantic data models
│   ├── video_processor.py      # Detection & tracking
│   ├── event_stream.py         # Event management
│   ├── analytics_engine.py     # Metrics calculation
│   └── requirements.txt        # Dependencies
├── frontend/
│   ├── index.html              # Dashboard UI
│   ├── styles.css              # Styling
│   └── app.js                  # Frontend logic
└── README.md                   # Documentation
```

### Adding New Features

1. **New Event Type**: Add to `EventType` enum in `models.py`
2. **Custom Metrics**: Extend `DetectionMetrics` in `models.py`
3. **Enhanced Classification**: Modify `_classify_person()` in `video_processor.py`
4. **New Endpoints**: Add routes in `main.py`

## Production Deployment

### Environment Variables
```bash
export STOREVISION_HOST=0.0.0.0
export STOREVISION_PORT=8000
export STOREVISION_LOG_LEVEL=info
export STOREVISION_MAX_UPLOAD_SIZE=100000000
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Monitoring
- Health endpoint: `/health`
- Metrics endpoint: `/api/v1/analytics/metrics`
- Logs: Standard output with timestamp and level

## License

Proprietary - Built for production use in retail intelligence systems

## Support

For issues, questions, or feature requests, contact the development team.

---

**StoreVision Analytics Platform** - Built by engineers, for engineers solving real-world AI challenges at scale.
