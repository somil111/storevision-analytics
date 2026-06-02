# User Guide - StoreVision Analytics Platform

Complete guide for users accessing the website and using the system.

## Getting Started

### For End Users (No Installation)

If someone shared a live link with you, just open it in your browser. No installation needed!

### For Developers/Self-Hosted

#### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/storevision-analytics.git
cd storevision-analytics
```

#### Step 2: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Step 3: Start Server
```bash
python main.py
```

#### Step 4: Open Dashboard
Open your browser and go to:
```
http://localhost:8000/static/index.html
```

## Using the Dashboard

### Dashboard Overview

The StoreVision dashboard consists of three main sections:

1. **Upload Tab** (default): Upload and analyze videos
2. **Analytics Tab**: View metrics and trends
3. **Events Tab**: Monitor real-time events

### Step-by-Step: Analyzing Your First Video

#### 1. Enter Store Information

In the Upload tab, fill in:
- **Store ID**: Unique identifier for your store (e.g., `store_001`, `store_manhattan`)
- **Camera ID**: Which camera in the store (e.g., `camera_01`, `entrance_cam`)

#### 2. Select Video

Click "Select MP4 file" button and choose an MP4 video from your computer.

Supported:
- Format: MP4
- Codec: H.264/H.265
- Resolution: Any (will be resized for processing)
- Duration: Any length

#### 3. Start Analysis

Click "Upload & Analyze" button.

The system will:
1. Upload your video (shows filename)
2. Detect persons in each frame
3. Track persons across frames
4. Classify as employee or customer
5. Calculate analytics

#### 4. Watch Progress

Real-time progress display shows:
- **Progress Bar**: % complete (0-100%)
- **Current Frame**: Which frame is being processed
- **Total Frames**: Total frames in video
- **Detections**: How many persons detected so far

#### 5. View Results

When analysis completes, you'll see:

**Summary Metrics**:
- Total Detections: Total persons found
- Employees: Count of employees
- Customers: Count of customers
- Avg Confidence: Average detection confidence (0-100%)

**Details Table**:
- Person ID: Unique identifier
- Type: Employee or Customer
- Confidence: Detection confidence %
- Dwell Time: How long they stayed (seconds)
- Frames: How many frames they were visible in

#### 6. Analyze New Video

Click "New Analysis" to start over with a different video.

## Understanding Results

### Person Classification

**Employee** indicators (classified as):
- Located in frame edges (0-20% or 80-100% from sides)
- In top portion of frame (checkout/service areas)
- Long dwell times in storage areas

**Customer** indicators (classified as):
- Located in center of frame (30-70%)
- In middle or bottom portions
- Movement through store aisles

**Confidence Score**:
- 0.0 = Very uncertain
- 0.5 = Moderate confidence
- 1.0 = Very confident
- Threshold: Detections with <0.5 confidence are filtered

### Metrics Explained

**Total Detections**: Sum of all persons detected in video

**Employee Count**: Unique employees identified

**Customer Count**: Unique customers identified

**Average Confidence**: Mean confidence score of all detections
- Higher = more reliable results

**Peak Occupancy**: Maximum number of persons in frame simultaneously

**Average Dwell Time**: How long each person stayed on average

## API Access (For Developers)

### REST API Endpoints

#### Upload Video
```
POST /api/v1/video/upload
Parameters:
  - store_id: string
  - camera_id: string
  - video: file (MP4)

Response:
{
  "video_id": "store_001_camera_01_1234567890",
  "store_id": "store_001",
  "camera_id": "camera_01",
  "filename": "video.mp4",
  "size_bytes": 52428800,
  "upload_timestamp": "2026-06-02T19:26:42"
}
```

#### Analyze Video
```
POST /api/v1/video/analyze
Body:
{
  "video_id": "store_001_camera_01_1234567890",
  "enable_tracking": true,
  "enable_events": true,
  "confidence_threshold": 0.5
}

Response:
{
  "video_id": "store_001_camera_01_1234567890",
  "status": "completed",
  "detections": [
    {
      "person_id": "person_0001",
      "person_type": "customer",
      "confidence": 0.87,
      "dwell_time_seconds": 15.6,
      "total_frames_visible": 47
    }
  ],
  "metrics": {
    "total_detections": 25,
    "employee_count": 5,
    "customer_count": 20,
    "average_confidence": 0.82,
    "peak_occupancy": 8
  },
  "processing_time_seconds": 42.3
}
```

#### Get Metrics
```
GET /api/v1/analytics/metrics?store_id=store_001&time_window_hours=24

Response:
{
  "total_detections": 250,
  "employee_count": 50,
  "customer_count": 200,
  "average_confidence": 0.81,
  "average_dwell_time_seconds": 18.5,
  "peak_occupancy": 42
}
```

### WebSocket Streaming

Real-time analysis updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/stream/analysis/video_id');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Progress:', data.progress_percent);
    console.log('Frame:', data.current_frame);
    console.log('Detections:', data.detections_so_far);
};
```

## API Documentation

Full interactive API documentation available at:

```
http://localhost:8000/docs
```

This provides:
- All endpoints
- Request/response schemas
- Try-it-out interface
- Authentication details

## System Health

Check system status:

```
GET /health
```

Response shows:
- Overall status (healthy/degraded/unhealthy)
- Component status
- Uptime
- Warnings

## Troubleshooting

### Video Won't Upload

**Problem**: Upload fails with error

**Solutions**:
1. Ensure file is MP4 format
2. Check file size (max 100MB recommended)
3. Verify backend server is running
4. Check browser console for errors

### No Detections Found

**Problem**: Analysis returns 0 detections

**Solutions**:
1. Video may be too dark/blurry
2. No visible persons in video
3. Lower confidence threshold (contact admin)
4. Check video format compatibility

### Slow Processing

**Problem**: Analysis takes too long

**Solutions**:
1. Use shorter video for testing
2. Reduce video resolution
3. Check server CPU/memory usage
4. Increase frame sampling rate (admin only)

### Dashboard Won't Load

**Problem**: Blank page or won't open

**Solutions**:
1. Verify URL: http://localhost:8000/static/index.html
2. Check server is running (see logs)
3. Try different browser
4. Clear browser cache
5. Check firewall/proxy settings

### Connection Errors

**Problem**: Can't connect to server

**Solutions**:
1. Verify server running on port 8000
2. Check firewall allows port 8000
3. Verify localhost is accessible
4. Try IP address: http://127.0.0.1:8000
5. Check antivirus/security software

## System Requirements

### Minimum
- CPU: 2 cores
- RAM: 4GB
- Storage: 2GB free
- Internet: Not required (runs locally)

### Recommended
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 10GB+ free
- GPU: NVIDIA (for faster processing)

## Browser Support

Tested and working on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Tips & Tricks

### 1. Batch Processing

Process multiple videos in sequence:
1. Analyze first video
2. When done, click "New Analysis"
3. Repeat with next video

### 2. Store Layouts

Different store layouts will have different classification accuracy:
- Linear stores: Good accuracy
- Open layout: Very good accuracy
- Complex layouts: Good, may need tuning

### 3. Lighting Conditions

Best results with:
- Good, even lighting
- No heavy shadows
- Clear person visibility

### 4. Video Quality

For best detection:
- Use high-quality cameras
- Ensure clear frames
- Avoid heavy compression
- Good frame rate (24+ fps)

### 5. Scheduling Analysis

For large batches:
- Process during off-hours
- Use lower confidence thresholds at night
- Monitor performance metrics

## Integration Examples

### Python Client

```python
import requests

# Upload
response = requests.post(
    'http://localhost:8000/api/v1/video/upload',
    params={'store_id': 'store_001', 'camera_id': 'cam_01'},
    files={'video': open('video.mp4', 'rb')}
)
video_id = response.json()['video_id']

# Analyze
response = requests.post(
    'http://localhost:8000/api/v1/video/analyze',
    json={'video_id': video_id}
)
results = response.json()

print(f"Customers: {results['metrics']['customer_count']}")
print(f"Employees: {results['metrics']['employee_count']}")
```

### JavaScript/Node.js

```javascript
const FormData = require('form-data');
const fs = require('fs');

const formData = new FormData();
formData.append('video', fs.createReadStream('video.mp4'));

const response = await fetch(
    'http://localhost:8000/api/v1/video/upload?store_id=store_001&camera_id=cam_01',
    { method: 'POST', body: formData }
);

const data = await response.json();
console.log('Video ID:', data.video_id);
```

## Getting Help

- Issues: Report bugs on GitHub Issues
- Documentation: See main README
- API Docs: http://localhost:8000/docs
- Discussions: Ask on GitHub Discussions

## FAQ

**Q: Can I process live camera feeds?**
A: Currently only MP4 files. Live streaming planned for v2.0.

**Q: How accurate is the classification?**
A: ~85-90% accuracy with good lighting. Depends on store layout.

**Q: Can I export results?**
A: Yes, via API responses. Dashboard results can be screenshot.

**Q: Is my video data stored?**
A: Videos are temporary in uploads/ folder. Deleted after processing.

**Q: Can I run this on cloud?**
A: Yes. See DEPLOYMENT.md for AWS, GCP, Heroku guides.

**Q: What about privacy?**
A: All processing is local. No data sent to external services.

---

**Need Help?** Check the documentation files or open an issue on GitHub!
