# StoreVision Analytics Platform - Quick Start Guide

## 30-Second Setup

### Step 1: Install Dependencies
```bash
cd storevision_platform\backend
pip install -r requirements.txt
```

### Step 2: Start Server
Double-click `START_SERVER.bat` or run:
```bash
cd storevision_platform
START_SERVER.bat
```

### Step 3: Open Dashboard
Open in your browser:
```
http://localhost:8000/static/index.html
```

## First Analysis

1. Enter Store ID: `store_001`
2. Enter Camera ID: `camera_01`
3. Select any MP4 video file
4. Click "Upload & Analyze"
5. Watch real-time processing
6. View detection results

## System Requirements

- Python 3.8+
- 4GB RAM minimum
- MP4 video files
- Windows/Linux/Mac

## What Happens During Analysis

1. **Upload**: Video is uploaded to server
2. **Detection**: HOG descriptor finds persons in frames
3. **Tracking**: System tracks persons across frames
4. **Classification**: Classifies as employee or customer based on position
5. **Events**: Generates entry, exit, and dwell time events
6. **Metrics**: Calculates statistics and insights

## Key Features

### Real-time Processing
- WebSocket streaming for live updates
- Progress indicator with frame counts
- Detection counter

### Detection Results
- Person ID and type (employee/customer)
- Confidence scores
- Dwell time per person
- Frame visibility counts

### Analytics
- Total detections
- Employee vs customer counts
- Average confidence
- Peak occupancy

## Classification Logic

**Employees** are detected in:
- Frame edges (0-20% or 80-100%)
- Top sections (checkout counters)
- Long dwell times in back areas

**Customers** are detected in:
- Central areas (30-70%)
- Middle and bottom sections
- Movement through aisles

## API Testing

### Using cURL

Upload video:
```bash
curl -X POST "http://localhost:8000/api/v1/video/upload?store_id=store_001&camera_id=camera_01" \
  -F "video=@path/to/video.mp4"
```

Get metrics:
```bash
curl "http://localhost:8000/api/v1/analytics/metrics?time_window_hours=24"
```

### Using Python

```python
import requests

# Upload video
with open('video.mp4', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/video/upload',
        params={'store_id': 'store_001', 'camera_id': 'camera_01'},
        files={'video': f}
    )

video_id = response.json()['video_id']

# Analyze video
response = requests.post(
    'http://localhost:8000/api/v1/video/analyze',
    json={'video_id': video_id}
)

results = response.json()
print(f"Detected {len(results['detections'])} persons")
```

## Troubleshooting

### Server Won't Start
- Check Python is installed: `python --version`
- Install dependencies: `pip install -r backend/requirements.txt`
- Check port 8000 is available

### No Detections Found
- Ensure video has visible persons
- Check video quality (not too dark/blurry)
- Lower confidence threshold in code

### Slow Processing
- Use shorter videos for testing
- Reduce video resolution
- Increase frame sampling rate

## Performance Tips

**For faster processing**:
- Edit `video_processor.py`, line 88: Change `frame_number % 5` to `frame_number % 10` (process every 10th frame)
- Reduce video resolution to 720p or lower
- Use videos under 2 minutes for testing

**For better accuracy**:
- Use high-quality footage with good lighting
- Ensure persons are clearly visible
- Avoid heavily occluded scenes

## Next Steps

1. Review full documentation in `README.md`
2. Explore API docs at http://localhost:8000/docs
3. Customize classification logic in `video_processor.py`
4. Add custom events in `event_stream.py`
5. Extend analytics in `analytics_engine.py`

## Support

For detailed information, see the main README.md file.

---

**Ready to analyze?** Just run `START_SERVER.bat` and open http://localhost:8000/static/index.html
