import React from 'react';

const ResultsComponent = ({ results }) => {
    if (!results) {
        return (
            <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Loading results...</p>
            </div>
        );
    }

    if (!results.success) {
        return (
            <div className="bg-red-50 border-2 border-red-300 text-red-700 px-6 py-4 rounded-lg">
                <p className="font-bold">Error</p>
                <p>{results.error || 'Failed to load results'}</p>
            </div>
        );
    }

    const { dominant_emotion, emotion_confidence, all_emotions, statement, similar_images } = results;

    const emotionEmoji = {
        happy: '😊',
        sad: '😢',
        angry: '😠',
        neutral: '😐',
        fear: '😨',
        surprise: '😲',
        disgust: '🤢',
    };

    const emotionColors = {
        happy: { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-300' },
        sad: { bg: 'bg-blue-100', text: 'text-blue-800', border: 'border-blue-300' },
        angry: { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-300' },
        neutral: { bg: 'bg-gray-100', text: 'text-gray-800', border: 'border-gray-300' },
        fear: { bg: 'bg-yellow-100', text: 'text-yellow-800', border: 'border-yellow-300' },
        surprise: { bg: 'bg-purple-100', text: 'text-purple-800', border: 'border-purple-300' },
        disgust: { bg: 'bg-pink-100', text: 'text-pink-800', border: 'border-pink-300' },
    };

    const confidencePercent = Math.round(emotion_confidence * 100);
    const emotionStyle = emotionColors[dominant_emotion] || emotionColors.neutral;

    return (
        <div className="w-full space-y-8 animate-fade-in">
            {/* Dominant Emotion Card */}
            <div className={`${emotionStyle.bg} ${emotionStyle.border} border-2 rounded-2xl p-8 shadow-lg`}>
                <div className="text-center">
                    <div className="text-7xl mb-4">{emotionEmoji[dominant_emotion] || '😊'}</div>
                    <h1 className={`text-5xl font-bold ${emotionStyle.text} mb-3`}>
                        {dominant_emotion.toUpperCase()}
                    </h1>
                    <div className="inline-block bg-white px-6 py-2 rounded-full mb-4 shadow-md">
                        <span className="text-2xl font-bold text-teal-600">{confidencePercent}%</span>
                        <span className="text-gray-600 ml-2">Confidence</span>
                    </div>
                    <p className="text-lg text-gray-700 mt-4 font-medium">{statement}</p>
                </div>
            </div>

            {/* All Emotions Distribution */}
            {all_emotions && Object.keys(all_emotions).length > 0 && (
                <div className="bg-white rounded-2xl p-6 shadow-lg border border-teal-100">
                    <h3 className="text-2xl font-bold text-gray-800 mb-4">Emotion Distribution</h3>
                    <div className="space-y-3">
                        {Object.entries(all_emotions)
                            .sort(([, a], [, b]) => b - a)
                            .map(([emotion, value]) => {
                                const percent = Math.round(value * 100);
                                const emoStyle = emotionColors[emotion] || emotionColors.neutral;
                                return (
                                    <div key={emotion} className="space-y-1">
                                        <div className="flex justify-between items-center">
                                            <span className="font-semibold text-gray-700 capitalize flex items-center gap-2">
                                                <span className="text-xl">{emotionEmoji[emotion] || '😊'}</span>
                                                {emotion}
                                            </span>
                                            <span className="text-gray-600 font-medium">{percent}%</span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                                            <div
                                                className={`h-full ${emoStyle.bg.replace('bg-', 'bg-')} transition-all duration-500 rounded-full`}
                                                style={{ width: `${percent}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                );
                            })}
                    </div>
                </div>
            )}

            {/* Similar Images Grid */}
            {similar_images && similar_images.length > 0 ? (
                <div className="bg-white rounded-2xl p-6 shadow-lg border border-teal-100">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-2xl font-bold text-gray-800">
                            Similar Images Found
                        </h3>
                        <span className="bg-teal-100 text-teal-800 px-4 py-1 rounded-full font-semibold">
                            {similar_images.length} {similar_images.length === 1 ? 'image' : 'images'}
                        </span>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        {similar_images.map((image, idx) => {
                            const imgEmoStyle = emotionColors[image.emotion] || emotionColors.neutral;
                            const imgConfidence = Math.round((image.confidence || 0.8) * 100);
                            return (
                                <div
                                    key={idx}
                                    className="bg-white rounded-xl overflow-hidden shadow-md border-2 border-gray-200 hover:shadow-xl transition-all duration-300 card-hover"
                                >
                                    {/* Image */}
                                    <div className="relative w-full h-48 bg-gray-100 overflow-hidden">
                                        {image.image_base64 ? (
                                            <img
                                                src={image.image_base64}
                                                alt={image.filename || `Image ${idx + 1}`}
                                                className="w-full h-full object-cover"
                                            />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center text-gray-400">
                                                <span className="text-4xl">🖼️</span>
                                            </div>
                                        )}
                                    </div>
                                    
                                    {/* Image Info */}
                                    <div className="p-4 space-y-2">
                                        <div className="flex items-center justify-between">
                                            <span className={`${imgEmoStyle.text} font-bold text-lg capitalize flex items-center gap-1`}>
                                                <span>{emotionEmoji[image.emotion] || '😊'}</span>
                                                {image.emotion}
                                            </span>
                                            <span className="text-sm font-semibold text-gray-600">
                                                {imgConfidence}%
                                            </span>
                                        </div>
                                        
                                        {/* Face Match Score */}
                                        {image.similarity !== undefined && (
                                            <div className="flex items-center gap-2 text-xs">
                                                <span className="text-gray-600 font-medium">Face Match:</span>
                                                <span className={`font-bold ${
                                                    image.similarity >= 0.8 ? 'text-green-600' :
                                                    image.similarity >= 0.6 ? 'text-yellow-600' :
                                                    'text-orange-600'
                                                }`}>
                                                    {Math.round(image.similarity * 100)}%
                                                </span>
                                            </div>
                                        )}
                                        
                                        <div className="flex items-center justify-between text-xs">
                                            <span className={`px-2 py-1 rounded ${image.source === 'local_folder' ? 'bg-teal-100 text-teal-700' : 'bg-blue-100 text-blue-700'} font-medium`}>
                                                {image.source === 'local_folder' ? '📁 Local' : '💾 Storage'}
                                            </span>
                                            <span className="text-gray-500 truncate max-w-[120px]" title={image.filename}>
                                                {image.filename}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            ) : (
                <div className="bg-yellow-50 border-2 border-yellow-300 text-yellow-700 px-6 py-4 rounded-lg">
                    <p className="font-semibold">No similar images found</p>
                    <p className="text-sm mt-1">Try capturing a different expression or check if images exist in the frontend/Images folder.</p>
                </div>
            )}
        </div>
    );
};

export default ResultsComponent;
