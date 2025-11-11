// lib/api/client.ts
import axios from 'axios';
import type { GenerateRequest, GenerateResponse, TransposeRequest, TransposeResponse } from '@/types/progression';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiClient = {
  // Health check
  async healthCheck() {
    const response = await api.get('/api/health');
    return response.data;
  },

  // Generate chord progressions
  async generateProgressions(request: GenerateRequest): Promise<GenerateResponse> {
    const response = await api.post<GenerateResponse>('/api/generate', request);
    return response.data;
  },

  // Transpose progression
  async transposeProgression(request: TransposeRequest): Promise<TransposeResponse> {
    const response = await api.post<TransposeResponse>('/api/transpose', request);
    return response.data;
  },
};

export default apiClient;

