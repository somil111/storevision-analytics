from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, StreamingResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import logging
from pathlib import Path
from typing import List, Dict, Any
import json
import asyncio
from datetime import datetime

from video_processor import VideoProcessor
from event_stream import EventStreamManager
from analytics_engine import AnalyticsEngine
from models import (
    VideoUploadResponse,
    AnalysisRequest,
    AnalysisResponse,
    EventRecord,
    SystemHealth,
    DetectionMetrics
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

video_processor = None
event_manager = None
analytics_engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup system resources"""
    global video_processor, event_manager, analytics_engine
    
    logger.info("Initializing StoreVision Analytics Platform")
    
    video_processor = VideoProcessor()
    event_manager = EventStreamManager()
    analytics_engine = AnalyticsEngine()
    
    logger.info("System initialization complete")
    
    yield
    
    logger.info("Shutting down StoreVision Platform")
    await event_manager.shutdown()


app = FastAPI(
    title="StoreVision Analytics Platform",
    description="Production-grade CCTV intelligence system with real-time analytics",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Robust frontend path resolution
frontend_path = Path(__file__).parent.parent / "frontend"
if not frontend_path.exists():
    frontend_path = Path(__file__).parent / ".." / "frontend"

# Only mount if the directory actually exists
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    logger.info(f"Serving frontend from: {frontend_path.resolve()}")
else:
    logger.warning(f"Frontend directory not found at: {frontend_path.resolve()}")


# Root endpoint - clean redirect
@app.get("/")
async def root():
    """Redirect to dashboard"""
    return RedirectResponse(url="/static/index.html")


@app.get("/health", response_model=SystemHealth)
async def health_check():
    """System health check endpoint"""
    return SystemHealth(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        components={
            "video_processor": "operational",
            "event_stream": "operational",
            "analytics_engine": "operational"
        },
        uptime_seconds=0
    )


@app.post("/api/v1/video/upload", response_model=VideoUploadResponse)
async def upload_video(
    store_id: str,
    camera_id: str,
    video: UploadFile = File(...)
):
    """
    Upload CCTV video for processing

    Args:
        store_id: Unique store identifier
        camera_id: Camera identifier
        video: Video file (MP4 format)

    Returns:
        Upload confirmation with video_id
    """
    logger.info(f"Receiving video upload - Store: {store_id}, Camera: {camera_id}")

    # Case-insensitive extension check
    if not video.filename.lower().endswith('.mp4'):
        raise HTTPException(
            status_code=400,
            detail="Only MP4 format supported"
        )

    try:
        video_id = f"{store_id}_{camera_id}_{datetime.utcnow().timestamp()}"
        video_path = UPLOAD_DIR / f"{video_id}.mp4"

        with open(video_path, "wb") as buffer:
            content = await video.read()
            buffer.write(content)

        logger.info(f"Video saved: {video_id}")

        return VideoUploadResponse(
            video_id=video_id,
            store_id=store_id,
            camera_id=camera_id,
            filename=video.filename,
            size_bytes=len(content),
            upload_timestamp=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


@app.post("/api/v1/video/analyze", response_model=AnalysisResponse)
async def analyze_video(request: AnalysisRequest):
    """
    Analyze uploaded video for person detection and classification

    Args:
        request: Analysis request with video_id

    Returns:
        Complete analysis results
    """
    logger.info(f"Starting analysis for video: {request.video_id}")

    video_path = UPLOAD_DIR / f"{request.video_id}.mp4"

    if not video_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Video not found"
        )

    try:
        results = await video_processor.process_video(
            str(video_path),
            request.video_id
        )

        events = await event_manager.create_events_from_results(results)
        metrics = await analytics_engine.calculate_metrics(results)

        logger.info(f"Analysis complete: {len(results['detections'])} detections")

        return AnalysisResponse(
            video_id=request.video_id,
            status="completed",
            detections=results['detections'],
            events=events,
            metrics=metrics,
            processing_time_seconds=results['processing_time']
        )

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.websocket("/api/v1/stream/analysis/{video_id}")
async def stream_analysis(websocket: WebSocket, video_id: str):
    """Real-time video analysis streaming via WebSocket"""
    await websocket.accept()
    logger.info(f"WebSocket connection established for video: {video_id}")

    video_path = UPLOAD_DIR / f"{video_id}.mp4"

    if not video_path.exists():
        await websocket.send_json({"error": "Video not found"})
        await websocket.close()
        return

    try:
        async for update in video_processor.process_video_streaming(str(video_path)):
            await websocket.send_json(update)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {video_id}")
    except Exception as e:
        logger.error(f"Streaming error: {str(e)}")
        try:
            await websocket.send_json({"error": str(e)})
        except Exception:
            pass  # Socket may already be closed
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


@app.get("/api/v1/analytics/metrics", response_model=DetectionMetrics)
async def get_metrics(
    store_id: str = None,
    time_window_hours: int = 24
):
    """Get aggregated analytics metrics"""
    metrics = await analytics_engine.get_aggregated_metrics(
        store_id=store_id,
        time_window_hours=time_window_hours
    )
    return metrics


@app.get("/api/v1/events/stream")
async def stream_events():
    """Server-Sent Events stream for real-time event updates"""
    async def event_generator():
        try:
            while True:
                event = await event_manager.get_next_event()
                if event:
                    yield f"data: {json.dumps(event)}\n\n"
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            logger.info("Event stream cancelled")
        except Exception as e:
            logger.error(f"Event stream error: {str(e)}")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@app.delete("/api/v1/video/{video_id}")
async def delete_video(video_id: str):
    """Delete uploaded video"""
    video_path = UPLOAD_DIR / f"{video_id}.mp4"

    if not video_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Video not found"
        )

    try:
        video_path.unlink()
        logger.info(f"Video deleted: {video_id}")
        return {"status": "deleted", "video_id": video_id}
    except Exception as e:
        logger.error(f"Delete failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Delete failed: {str(e)}"
        )


if __name__ == "__main__":
    logger.info("Starting StoreVision Analytics Platform")
    logger.info("Dashboard available at: http://localhost:8000/static/index.html")
    logger.info("API documentation: http://localhost:8000/docs")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )