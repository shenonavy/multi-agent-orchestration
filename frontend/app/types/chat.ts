export interface Message {
  content: string;
  role: 'user' | 'assistant' | 'system';
  timestamp: string;
  source?: string;
  details?: Record<string, unknown>;
}

export interface ChatResponse {
  response: string;
  source: string;
  details: Record<string, unknown>;
}
