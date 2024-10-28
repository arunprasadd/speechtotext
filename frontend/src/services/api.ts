// frontend/src/services/api.ts
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
});

export const transcriptionApi = {
    upload: async (file: File, language: string, model: string) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('language', language);
        formData.append('model_size', model);
        
        return api.post('/transcription/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
    },

    getStatus: async (id: number) => {
        return api.get(`/transcription/${id}`);
    },
};

export default api;