import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 300000, // 5 minutes for emotion analysis
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor
api.interceptors.request.use(
    (config) => {
        // Add any auth tokens if needed
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
    }
);

export const searchFaces = async (payload) => {
    try {
        const response = await api.post('/api/v1/search', payload);
        return response.data;
    } catch (error) {
        throw new Error(error.response?.data?.detail || 'Search failed');
    }
};

export const healthCheck = async () => {
    try {
        const response = await api.get('/api/health');
        return response.data;
    } catch (error) {
        throw new Error('Backend unreachable');
    }
};

export const getLocalImages = async (emotion = null) => {
    try {
        const params = emotion ? { emotion } : {};
        const response = await api.get('/api/v1/local-images', { params });
        return response.data;
    } catch (error) {
        console.error('Error fetching local images:', error);
        throw new Error(error.response?.data?.error || 'Failed to fetch local images');
    }
};

export const getStorageStats = async () => {
    try {
        const response = await api.get('/api/v1/storage-stats');
        return response.data;
    } catch (error) {
        console.error('Error fetching storage stats:', error);
        throw new Error(error.response?.data?.error || 'Failed to fetch storage stats');
    }
};

export const analyzeFace = async (formData) => {
    try {
        const response = await api.post('/api/v1/analyze-face', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        console.error('Error analyzing face:', error);
        throw new Error(error.response?.data?.error || 'Failed to analyze face');
    }
};

export default api;
