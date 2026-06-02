

const API_BASE_URL = 'http://localhost:8000';
let currentVideoId = null;
let analysisWebSocket = null;


document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeFileInput();
    initializeUploadForm();
    checkSystemHealth();
    
    
    setInterval(checkSystemHealth, 30000);
});


function initializeNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    const views = document.querySelectorAll('.view');
    
    navButtons.forEach(button => {
        button.addEventListener('click', function() {
            const viewName = this.dataset.view;
            
            // Update active button
            navButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Update active view
            views.forEach(view => view.classList.remove('active'));
            document.getElementById(`${viewName}View`).classList.add('active');
        });
    });
}


function initializeFileInput() {
    const fileInput = document.getElementById('videoFile');
    const fileDisplay = document.getElementById('fileDisplay');
    const uploadBtn = document.getElementById('uploadBtn');
    
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        
        if (file) {
            const fileText = fileDisplay.querySelector('.file-text');
            fileText.textContent = file.name;
            
            // Enable upload button if all fields are filled
            validateForm();
        }
    });
    
    
    document.getElementById('storeId').addEventListener('input', validateForm);
    document.getElementById('cameraId').addEventListener('input', validateForm);
}


function validateForm() {
    const storeId = document.getElementById('storeId').value.trim();
    const cameraId = document.getElementById('cameraId').value.trim();
    const fileInput = document.getElementById('videoFile');
    const uploadBtn = document.getElementById('uploadBtn');
    
    const isValid = storeId && cameraId && fileInput.files.length > 0;
    uploadBtn.disabled = !isValid;
}


function initializeUploadForm() {
    const uploadBtn = document.getElementById('uploadBtn');
    uploadBtn.addEventListener('click', handleUpload);
    
    const newAnalysisBtn = document.getElementById('newAnalysisBtn');
    newAnalysisBtn.addEventListener('click', resetForm);
}


async function handleUpload() {
    const storeId = document.getElementById('storeId').value.trim();
    const cameraId = document.getElementById('cameraId').value.trim();
    const fileInput = document.getElementById('videoFile');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a video file');
        return;
    }
    
    try {
        
        document.querySelector('.upload-form').style.display = 'none';
        document.getElementById('processingStatus').style.display = 'block';
        
        
        const formData = new FormData();
        formData.append('video', file);
        
        const uploadResponse = await fetch(
            `${API_BASE_URL}/api/v1/video/upload?store_id=${storeId}&camera_id=${cameraId}`,
            {
                method: 'POST',
                body: formData
            }
        );
        
        if (!uploadResponse.ok) {
            throw new Error('Upload failed');
        }
        
        const uploadData = await uploadResponse.json();
        currentVideoId = uploadData.video_id;
        
        console.log('Video uploaded:', uploadData);
        
        
        await startWebSocketAnalysis(currentVideoId);
        
    } catch (error) {
        console.error('Error:', error);
        alert('Upload failed: ' + error.message);
        resetForm();
    }
}


async function startWebSocketAnalysis(videoId) {
    const wsUrl = `ws://localhost:8000/api/v1/stream/analysis/${videoId}`;
    
    analysisWebSocket = new WebSocket(wsUrl);
    
    analysisWebSocket.onopen = function() {
        console.log('WebSocket connected');
    };
    
    analysisWebSocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        if (data.error) {
            console.error('Analysis error:', data.error);
            alert('Analysis failed: ' + data.error);
            analysisWebSocket.close();
            resetForm();
            return;
        }
        
        if (data.status === 'processing') {
            updateProgress(data);
        } else if (data.status === 'completed') {
            displayResults(data.results);
            analysisWebSocket.close();
        }
    };
    
    analysisWebSocket.onerror = function(error) {
        console.error('WebSocket error:', error);
        
        analyzeVideoFallback(videoId);
    };
    
    analysisWebSocket.onclose = function() {
        console.log('WebSocket closed');
    };
}


async function analyzeVideoFallback(videoId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/video/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                video_id: videoId,
                enable_tracking: true,
                enable_events: true
            })
        });
        
        if (!response.ok) {
            throw new Error('Analysis failed');
        }
        
        const data = await response.json();
        displayResults(data);
        
    } catch (error) {
        console.error('Analysis error:', error);
        alert('Analysis failed: ' + error.message);
        resetForm();
    }
}


function updateProgress(data) {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const currentFrame = document.getElementById('currentFrame');
    const totalFrames = document.getElementById('totalFrames');
    const detectionCount = document.getElementById('detectionCount');
    
    const progress = data.progress_percent || 0;
    
    progressFill.style.width = `${progress}%`;
    progressText.textContent = `${Math.round(progress)}%`;
    currentFrame.textContent = data.current_frame || 0;
    totalFrames.textContent = data.total_frames || 0;
    detectionCount.textContent = data.detections_so_far || 0;
}


function displayResults(results) {
    
    document.getElementById('processingStatus').style.display = 'none';
    
   
    const resultsContainer = document.getElementById('resultsContainer');
    resultsContainer.style.display = 'block';
    
   
    const detections = results.detections || [];
    const employeeCount = detections.filter(d => d.person_type === 'employee').length;
    const customerCount = detections.filter(d => d.person_type === 'customer').length;
    const avgConfidence = detections.length > 0
        ? detections.reduce((sum, d) => sum + d.confidence, 0) / detections.length
        : 0;
    
    document.getElementById('totalDetections').textContent = detections.length;
    document.getElementById('employeeCount').textContent = employeeCount;
    document.getElementById('customerCount').textContent = customerCount;
    document.getElementById('avgConfidence').textContent = `${Math.round(avgConfidence * 100)}%`;
    
    
    const tableBody = document.getElementById('detectionsTableBody');
    tableBody.innerHTML = '';
    
    detections.forEach(detection => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${detection.person_id}</td>
            <td>${capitalizeFirst(detection.person_type)}</td>
            <td>${Math.round(detection.confidence * 100)}%</td>
            <td>${detection.dwell_time_seconds.toFixed(1)}s</td>
            <td>${detection.total_frames_visible}</td>
        `;
        tableBody.appendChild(row);
    });
}


function resetForm() {
    
    document.getElementById('resultsContainer').style.display = 'none';
    document.getElementById('processingStatus').style.display = 'none';
    
    
    document.querySelector('.upload-form').style.display = 'block';
    
    
    document.getElementById('storeId').value = '';
    document.getElementById('cameraId').value = '';
    document.getElementById('videoFile').value = '';
    document.querySelector('.file-text').textContent = 'Select MP4 file';
    document.getElementById('uploadBtn').disabled = true;
    
    
    document.getElementById('progressFill').style.width = '0%';
    document.getElementById('progressText').textContent = '0%';
    
    
    if (analysisWebSocket) {
        analysisWebSocket.close();
        analysisWebSocket = null;
    }
    
    currentVideoId = null;
}


async function checkSystemHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        const statusIndicator = document.getElementById('systemStatus');
        const apiStatus = document.getElementById('apiStatus');
        
        if (data.status === 'healthy') {
            statusIndicator.textContent = 'Operational';
            statusIndicator.style.backgroundColor = 'var(--success-color)';
            apiStatus.textContent = 'API: Connected';
        } else {
            statusIndicator.textContent = 'Degraded';
            statusIndicator.style.backgroundColor = 'var(--warning-color)';
            apiStatus.textContent = 'API: Degraded';
        }
    } catch (error) {
        const statusIndicator = document.getElementById('systemStatus');
        const apiStatus = document.getElementById('apiStatus');
        
        statusIndicator.textContent = 'Offline';
        statusIndicator.style.backgroundColor = 'var(--error-color)';
        apiStatus.textContent = 'API: Disconnected';
    }
}


function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}
