# StoreVision Project Structure

## Directory Layout

```
storevision-analytics/
│
├── backend/                          # FastAPI backend server
│   ├── main.py                      # Main API server with all endpoints
│   ├── models.py                    # Pydantic data models and schemas
│   ├── video_processor.py           # Person detection, tracking, classification
│   ├── event_stream.py              # Event generation and streaming
│   ├── analytics_engine.py          # Metrics calculation and analysis
│   ├── requirements.txt             # Python dependencies
│   └── uploads/                     # Temporary video storage
│
├── frontend/                         # Web dashboard (HTML/CSS/JS)
│   ├── index.html                   # Dashboard interface
│   ├── styles.css                   # Professional styling
│   └── app.js                       # WebSocket and API integration
│
├── .github/                          # GitHub configuration
│   └── workflows/
│       └── python-app.yml          # CI/CD pipeline
│
├── README.md                         # Main documentation
├── QUICKSTART.md                     # Quick setup guide
├── SYSTEM_OVERVIEW.md               # Architecture and design
├── DEPLOYMENT.md                     # Deployment instructions
├── CONTRIBUTING.md                  # Contribution guidelines
├── LICENSE                           # MIT License
├── .gitignore                        # Git ignore rules
├── Dockerfile                        # Docker container definition
├── docker-compose.yml               # Multi-container orchestration
└── START_SERVER.bat                 # Windows batch launcher

```

## Component Details

### Backend Structure

#### main.py (263 lines)
Core FastAPI application with:
- Async request handling
- CORS configuration
- WebSocket streaming
- RESTful endpoints
- Static file serving
- Health checks

Key Endpoints:
- POST /api/v1/video/upload
- POST /api/v1/video/analyze
- WebSocket /api/v1/stream/analysis/{video_id}
- GET /api/v1/analytics/metrics
- GET /api/v1/events/stream

#### models.py (212 lines)
Type-safe data validation using Pydantic:
- PersonDetection: Detection results
- EventRecord: Event data
- DetectionMetrics: Aggregated statistics
- AnalysisResponse: Complete results
- SystemHealth: Health status

#### video_processor.py (468 lines)
Computer vision processing pipeline:
- Person detection using HOG descriptor
- Multi-object tracking with centroid matching
- Employee/customer classification
- Trajectory mapping
- Dwell time analysis

Key Methods:
- process_video(): Complete video analysis
- process_video_streaming(): Real-time updates
- _detect_persons_in_frame(): Frame-level detection
- _classify_person(): Classification logic
- _track_person(): Cross-frame tracking

#### event_stream.py (297 lines)
Real-time event management:
- Event generation from detections
- Event buffering (circular queue)
- SSE streaming support
- Subscriber management

Event Types:
- PERSON_DETECTED
- PERSON_ENTERED
- PERSON_EXITED
- DWELL_TIME_THRESHOLD
- MOVEMENT_DETECTED

#### analytics_engine.py (330 lines)
Analytics and insights generation:
- Metrics calculation
- Historical data tracking
- Trend analysis
- Store comparison
- Time-windowed aggregation

Metrics Provided:
- Total detections by type
- Average confidence
- Peak occupancy
- Dwell time statistics
- Entry/exit counts

### Frontend Structure

#### index.html
Dashboard interface with:
- Navigation tabs (Upload, Analytics, Events)
- File upload form
- Real-time progress indicator
- Results display
- Metrics cards
- Detection table

#### styles.css (200+ lines)
Professional dark-themed styling:
- Color scheme: Dark background, green accents
- Responsive layout
- Smooth animations
- Professional typography
- No emojis

#### app.js (337 lines)
Frontend logic:
- WebSocket connection management
- REST API integration
- Real-time progress updates
- Form validation
- Results rendering
- Health monitoring

## Development Workflow

### Adding Features

1. Define data model in models.py
2. Add API endpoint in main.py
3. Implement logic in processor/engine
4. Update frontend in app.js
5. Test locally
6. Create pull request

### Testing

- Unit tests in backend/tests/
- Integration tests for API
- Frontend testing with browser
- Manual video processing tests

### Deployment

1. Push to GitHub
2. CI/CD runs tests (GitHub Actions)
3. Build Docker image
4. Deploy to cloud platform
5. Monitor performance

## File Descriptions

### .gitignore
Python and project-specific rules:
- __pycache__, .pyc files
- Virtual environments
- IDE settings
- Uploaded videos
- Environment files
- Build artifacts

### Dockerfile
Multi-stage container build:
- Python 3.9-slim base
- System dependencies for OpenCV
- Python packages installation
- Exposed port 8000
- Production-ready entry point

### docker-compose.yml
Container orchestration:
- Service definition
- Port mapping (8000:8000)
- Volume mounting for uploads
- Restart policy
- Environment configuration

### START_SERVER.bat
Windows convenience script:
- Sets up environment
- Displays server URL
- Launches main.py
- Shows documentation links

## Dependencies

### Backend (requirements.txt)
- fastapi (0.109.0): Web framework
- uvicorn (0.27.0): ASGI server
- pydantic (2.5.3): Data validation
- opencv-python (4.9.0.80): Computer vision
- numpy (1.26.3): Numerical computing
- python-multipart (0.0.6): File uploads
- websockets (12.0): WebSocket support
- aiofiles (23.2.1): Async file operations

### Frontend
- Vanilla JavaScript (no frameworks)
- HTML5 API
- CSS3

## Configuration

### Environment Variables

Create `backend/.env`:
```
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO
UPLOAD_DIR=./uploads
MAX_VIDEO_SIZE=104857600
```

### Detection Parameters

In `video_processor.py`:
- min_confidence: 0.5
- win_stride: (8, 8)
- scale: 1.05
- frame_sampling: every 5th frame

## Git Workflow

### Branch Strategy
- main: Production releases
- develop: Development branch
- feature/*: Feature branches
- bugfix/*: Bug fix branches

### Commit Messages
```
[FEATURE] Add GPU support
[BUGFIX] Fix tracking issue on occlusion
[DOCS] Update deployment guide
[TEST] Add video processor tests
```

## Continuous Integration

GitHub Actions (python-app.yml):
- Python 3.9 environment
- Dependency installation
- Linting with flake8
- Testing with pytest
- Runs on: push, pull_request

## Performance Metrics

- Processing: ~2-5 FPS (CPU)
- Memory: ~50-100MB base
- Event buffer: Max 1000 events
- Video storage: Temporary in uploads/

## Support Resources

- README.md: Overview and usage
- QUICKSTART.md: 30-second setup
- SYSTEM_OVERVIEW.md: Architecture details
- DEPLOYMENT.md: Production deployment
- CONTRIBUTING.md: Development guidelines
