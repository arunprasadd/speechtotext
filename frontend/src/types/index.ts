// frontend/src/types/index.ts
export interface TranscriptionResponse {
  id: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  text?: string;
  error?: string;
}

export interface UploadResponse {
  id: number;
  message: string;
}