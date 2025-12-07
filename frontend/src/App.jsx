import React, { useState, useEffect } from 'react';
import FaceCaptureComponent from './components/FaceCaptureComponent';
import MetadataFormComponent from './components/MetadataFormComponent';
import ResultsComponent from './components/ResultsComponent';
import { analyzeFace, healthCheck } from './utils/api';

function App() {
    const [stage, setStage] = useState('capture'); // capture, form, results
    const [capturedImage, setCapturedImage] = useState(null);
    const [results, setResults] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [backendOnline, setBackendOnline] = useState(false);

    // Check backend health on mount
    useEffect(() => {
        const checkBackend = async () => {
            try {
                await healthCheck();
                setBackendOnline(true);
            } catch (err) {
                setBackendOnline(false);
                console.error('Backend offline:', err);
            }
        };

        checkBackend();
    }, []);

    const handleCapture = (base64Image) => {
        setCapturedImage(base64Image);
        setStage('form');
        setError(null);
    };

    const handleSearch = async (payload) => {
        setIsLoading(true);
        setError(null);

        try {
            // Convert base64 image to File for upload
            const base64Image = payload.captured_image;
            const base64Data = base64Image.split(',')[1] || base64Image;
            const byteCharacters = atob(base64Data);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], { type: 'image/jpeg' });
            const file = new File([blob], 'captured.jpg', { type: 'image/jpeg' });

            // Create FormData
            const formData = new FormData();
            formData.append('image', file);
            formData.append('user_name', payload.user_name || 'Guest');
            formData.append('privacy_agreed', payload.privacy_policy_agreed || true);

            const response = await analyzeFace(formData);
            setResults(response);
            setStage('results');
        } catch (err) {
            setError(err.message || 'Analysis failed. Please try again.');
            console.error('Analysis error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleNewSearch = () => {
        setStage('capture');
        setCapturedImage(null);
        setResults(null);
        setError(null);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-teal-50 via-cyan-50 to-teal-100">
            <div className="max-w-6xl mx-auto px-4 py-8">
                {/* Header with RIVION Branding */}
                <div className="text-center mb-12">
                    <div className="inline-block mb-4">
                        <h1 className="text-6xl font-bold bg-gradient-to-r from-teal-600 to-cyan-500 bg-clip-text text-transparent mb-2">
                            RIVION
                        </h1>
                        <div className="h-1 w-32 mx-auto bg-gradient-to-r from-teal-600 to-cyan-500 rounded-full"></div>
                    </div>
                    <p className="text-xl text-gray-700 font-medium">
                        Face Emotion Analyzer
                    </p>
                    <p className="text-gray-600 mt-2">
                        Capture your face and discover your emotional state
                    </p>
                    {!backendOnline && (
                        <div className="mt-6 max-w-md mx-auto bg-red-50 border-2 border-red-300 text-red-700 px-6 py-3 rounded-lg shadow-md">
                            ⚠️ Backend offline. Please ensure the server is running at localhost:8000
                        </div>
                    )}
                </div>

                {/* Progress Steps */}
                <div className="flex justify-center items-center mb-12 max-w-2xl mx-auto">
                    <div className="flex items-center w-full">
                        {/* Step 1 */}
                        <div className="flex flex-col items-center flex-1">
                            <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg transition-all duration-300 ${
                                stage === 'capture' || stage === 'form' || stage === 'results'
                                    ? 'bg-teal-600 text-white shadow-lg scale-110'
                                    : 'bg-gray-300 text-gray-600'
                            }`}>
                                1
                            </div>
                            <p className={`mt-2 text-sm font-medium ${
                                stage === 'capture' || stage === 'form' || stage === 'results'
                                    ? 'text-teal-600'
                                    : 'text-gray-500'
                            }`}>
                                Capture
                            </p>
                        </div>
                        <div className={`flex-1 h-1 mx-2 transition-all duration-300 ${
                            stage === 'form' || stage === 'results'
                                ? 'bg-teal-600'
                                : 'bg-gray-300'
                        }`}></div>
                        
                        {/* Step 2 */}
                        <div className="flex flex-col items-center flex-1">
                            <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg transition-all duration-300 ${
                                stage === 'form' || stage === 'results'
                                    ? 'bg-teal-600 text-white shadow-lg scale-110'
                                    : 'bg-gray-300 text-gray-600'
                            }`}>
                                2
                            </div>
                            <p className={`mt-2 text-sm font-medium ${
                                stage === 'form' || stage === 'results'
                                    ? 'text-teal-600'
                                    : 'text-gray-500'
                            }`}>
                                Details
                            </p>
                        </div>
                        <div className={`flex-1 h-1 mx-2 transition-all duration-300 ${
                            stage === 'results'
                                ? 'bg-teal-600'
                                : 'bg-gray-300'
                        }`}></div>
                        
                        {/* Step 3 */}
                        <div className="flex flex-col items-center flex-1">
                            <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg transition-all duration-300 ${
                                stage === 'results'
                                    ? 'bg-teal-600 text-white shadow-lg scale-110'
                                    : 'bg-gray-300 text-gray-600'
                            }`}>
                                3
                            </div>
                            <p className={`mt-2 text-sm font-medium ${
                                stage === 'results'
                                    ? 'text-teal-600'
                                    : 'text-gray-500'
                            }`}>
                                Results
                            </p>
                        </div>
                    </div>
                </div>

                {/* Main Content Card */}
                <div className="bg-white rounded-2xl shadow-2xl p-8 md:p-12 mb-8 border border-teal-100">
                    {error && (
                        <div className="mb-6 bg-red-50 border-2 border-red-300 text-red-700 px-6 py-4 rounded-lg shadow-md animate-fade-in">
                            <div className="flex items-center">
                                <span className="text-2xl mr-3">⚠️</span>
                                <div>
                                    <p className="font-bold">Error</p>
                                    <p>{error}</p>
                                </div>
                            </div>
                        </div>
                    )}

                    {isLoading && (
                        <div className="mb-6 bg-teal-50 border-2 border-teal-300 text-teal-700 px-6 py-4 rounded-lg shadow-md">
                            <div className="flex items-center justify-center">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600 mr-3"></div>
                                <p className="font-semibold">Analyzing your face and searching for similar images...</p>
                            </div>
                        </div>
                    )}

                    {stage === 'capture' && (
                        <div className="animate-fade-in">
                            <h2 className="text-3xl font-bold text-gray-800 mb-2">
                                Step 1: Capture Your Face
                            </h2>
                            <p className="text-gray-600 mb-6">
                                Position your face in front of the camera and capture your image
                            </p>
                            <FaceCaptureComponent onCapture={handleCapture} />
                        </div>
                    )}

                    {stage === 'form' && (
                        <div className="animate-fade-in">
                            <h2 className="text-3xl font-bold text-gray-800 mb-2">
                                Step 2: Enter Your Details
                            </h2>
                            <p className="text-gray-600 mb-6">
                                Provide your information to complete the analysis
                            </p>
                            <MetadataFormComponent
                                capturedImage={capturedImage}
                                onSearch={handleSearch}
                                isLoading={isLoading}
                            />
                        </div>
                    )}

                    {stage === 'results' && (
                        <div className="animate-fade-in">
                            <div className="flex justify-between items-center mb-6">
                                <div>
                                    <h2 className="text-3xl font-bold text-gray-800 mb-2">
                                        Step 3: Your Results
                                    </h2>
                                    <p className="text-gray-600">
                                        Emotion analysis and similar images found
                                    </p>
                                </div>
                                <button
                                    onClick={handleNewSearch}
                                    className="px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 font-semibold shadow-md transition-all duration-200 hover:scale-105"
                                >
                                    🔄 New Search
                                </button>
                            </div>
                            <ResultsComponent results={results} />
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="text-center text-gray-600 text-sm">
                    <p className="mb-2">
                        🔒 Your facial data is temporary and auto-deleted after 24 hours
                    </p>
                    <p className="text-xs text-gray-500">
                        RIVION © 2024 - Face Emotion Analyzer
                    </p>
                </div>
            </div>
        </div>
    );
}

export default App;
