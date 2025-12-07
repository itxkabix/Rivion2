import React, { useEffect, useRef, useState } from 'react';
import * as faceapi from 'face-api.js';
import '../styles/FaceCapture.css';

const FaceCaptureComponent = ({ onCapture }) => {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const displayCanvasRef = useRef(null);
    const [faceDetected, setFaceDetected] = useState(false);
    const [facesCount, setFacesCount] = useState(0);
    const [modelsLoaded, setModelsLoaded] = useState(false);
    const [isStreaming, setIsStreaming] = useState(false);
    const [faceQuality, setFaceQuality] = useState('');
    const detectionIntervalRef = useRef(null);

    // Load face-api models
    useEffect(() => {
        const loadModels = async () => {
            try {
                const MODEL_URL = 'https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model/';

                await Promise.all([
                    faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
                    faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL),
                    faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL),
                    faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL),
                    faceapi.nets.ageGenderNet.loadFromUri(MODEL_URL),
                ]);

                setModelsLoaded(true);
                console.log('✅ All face detection models loaded');
            } catch (error) {
                console.error('❌ Error loading models:', error);
                alert('Failed to load face detection models. Please refresh the page.');
            }
        };

        loadModels();
    }, []);

    // Start camera stream
    useEffect(() => {
        if (!modelsLoaded) return;

        const startCamera = async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: {
                        width: { ideal: 640 },
                        height: { ideal: 480 },
                        facingMode: 'user'
                    },
                });

                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                    videoRef.current.onloadedmetadata = () => {
                        videoRef.current.play();
                        setIsStreaming(true);
                    };
                }
            } catch (error) {
                console.error('❌ Camera access error:', error);
                alert('Please allow camera access to use this app.');
            }
        };

        startCamera();

        return () => {
            if (videoRef.current && videoRef.current.srcObject) {
                videoRef.current.srcObject.getTracks().forEach(track => track.stop());
                setIsStreaming(false);
            }
        };
    }, [modelsLoaded]);

    // Real-time face detection with visualization
    useEffect(() => {
        if (!modelsLoaded || !isStreaming) return;

        const detectFaces = async () => {
            if (!videoRef.current || !displayCanvasRef.current) return;

            try {
                const video = videoRef.current;
                const canvas = displayCanvasRef.current;

                // Detect faces with all features
                const detections = await faceapi
                    .detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
                    .withFaceLandmarks()
                    .withFaceExpressions()
                    .withAgeAndGender();

                // Set canvas dimensions
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;

                // Clear canvas
                const ctx = canvas.getContext('2d');
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                // Draw all detections
                if (detections.length > 0) {
                    // Draw boxes and landmarks
                    faceapi.draw.drawDetections(canvas, detections);
                    faceapi.draw.drawFaceLandmarks(canvas, detections);

                    // Draw expressions
                    const displaySize = { width: video.videoWidth, height: video.videoHeight };
                    const resizedDetections = faceapi.resizeResults(detections, displaySize);

                    resizedDetections.forEach((detection, index) => {
                        const { age, gender, genderProbability } = detection;
                        const expressions = detection.expressions;

                        // Get dominant expression
                        const dominantExpression = Object.entries(expressions).sort(
                            ([, a], [, b]) => b - a
                        )[0];

                        // Determine face quality
                        const box = detection.detection.box;
                        const faceArea = box.width * box.height;
                        const videoArea = canvas.width * canvas.height;
                        const facePercentage = (faceArea / videoArea) * 100;

                        if (facePercentage > 15 && facePercentage < 80) {
                            setFaceQuality('✅ Good positioning');
                        } else if (facePercentage <= 15) {
                            setFaceQuality('📏 Move closer to camera');
                        } else {
                            setFaceQuality('📏 Move back from camera');
                        }
                    });
                }

                // Update detection state
                setFacesCount(detections.length);
                setFaceDetected(detections.length > 0);

            } catch (error) {
                console.error('Detection error:', error);
            }
        };

        // Run detection every 100ms (10 FPS for performance)
        detectionIntervalRef.current = setInterval(detectFaces, 100);

        return () => {
            if (detectionIntervalRef.current) {
                clearInterval(detectionIntervalRef.current);
            }
        };
    }, [modelsLoaded, isStreaming]);

    // Capture image
    const handleCapture = async () => {
        if (!faceDetected) {
            alert('⚠️ Please face the camera. No face detected!');
            return;
        }

        if (!videoRef.current) return;

        try {
            const video = videoRef.current;
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);

            // Convert to base64
            const base64Image = canvas.toDataURL('image/jpeg', 0.95);

            console.log('✅ Face captured successfully');
            onCapture(base64Image);
        } catch (error) {
            console.error('Capture error:', error);
            alert('Failed to capture image');
        }
    };

    return (
        <div className="face-capture-container">
            <div className="capture-section">
                <h2>📸 Step 1: Capture Your Face</h2>

                {!modelsLoaded ? (
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Loading face detection models...</p>
                        <p className="loading-subtitle">This may take 30-60 seconds on first load</p>
                    </div>
                ) : (
                    <>
                        <div className="camera-wrapper">
                            <div className="camera-container">
                                <video
                                    ref={videoRef}
                                    autoPlay
                                    playsInline
                                    muted
                                    className="video-stream"
                                />
                                <canvas
                                    ref={displayCanvasRef}
                                    className="detection-canvas"
                                />

                                <div className={`detection-status ${faceDetected ? 'detected' : 'not-detected'}`}>
                                    {faceDetected ? (
                                        <>
                                            <div className="status-icon">✅</div>
                                            <p>Face Detected!</p>
                                            <p className="subtitle">{facesCount} face(s) found</p>
                                            {faceQuality && <p className="quality">{faceQuality}</p>}
                                        </>
                                    ) : (
                                        <>
                                            <div className="status-icon">⚠️</div>
                                            <p>Face Not Detected</p>
                                            <p className="subtitle">Please face the camera</p>
                                        </>
                                    )}
                                </div>

                                {/* Positioning guide */}
                                <div className="positioning-guide">
                                    <div className="face-outline"></div>
                                    <p className="guide-text">Position your face within the oval</p>
                                </div>
                            </div>
                        </div>

                        <div className="capture-controls">
                            <button
                                onClick={handleCapture}
                                disabled={!faceDetected}
                                className={`capture-button ${faceDetected ? 'active' : 'disabled'}`}
                            >
                                📸 Capture Face
                            </button>

                            {!faceDetected && (
                                <p className="help-text">
                                    💡 Look at the camera, keep your face centered in the frame
                                </p>
                            )}
                        </div>

                        <div className="detection-info">
                            <p>🎯 <strong>Detection Status:</strong> {faceDetected ? '✅ Ready to capture' : '⏳ Waiting for face'}</p>
                            <p>👥 <strong>Faces Detected:</strong> {facesCount}</p>
                            <p>📹 <strong>Camera:</strong> {isStreaming ? '🟢 Active' : '🔴 Inactive'}</p>
                            <p>📊 <strong>Quality:</strong> {faceQuality || '—'}</p>
                        </div>

                        <div className="tips-section">
                            <h3>✨ Tips for Best Results:</h3>
                            <ul>
                                <li>🔆 Ensure good lighting on your face</li>
                                <li>📐 Keep your face centered in the frame</li>
                                <li>😐 Look directly at the camera</li>
                                <li>🎯 Fill about 30-50% of the frame with your face</li>
                                <li>❌ Remove sunglasses or hats if possible</li>
                            </ul>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default FaceCaptureComponent;
