import { ModelId, Citation, ReasoningStep } from '../types/chat';

interface StreamCallbacks {
  onReasoningStart?: () => void;
  onReasoningStep?: (step: ReasoningStep) => void;
  onCitations?: (citations: Citation[]) => void;
  onToken: (token: string) => void;
  onComplete: () => void;
  onError?: (error: string) => void;
}

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';

export async function generateStreamResponse(
  prompt: string,
  modelId: ModelId,
  webSearchEnabled: boolean,
  callbacks: StreamCallbacks,
  signal?: AbortSignal
) {
  try {
    const response = await fetch(`${API_BASE_URL}/v1/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: modelId,
        messages: [{ role: 'user', content: prompt }],
        stream: true
      }),
      signal
    });

    if (!response.ok) {
      throw new Error(`Neurix Gateway returned status ${response.status}. Please check backend logs.`);
    }

    if (!response.body) {
      throw new Error('ReadableStream is not supported in this browser.');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.replace('data: ', '').trim();
          if (dataStr === '[DONE]') {
            continue;
          }
          if (dataStr) {
            try {
              const chunk = JSON.parse(dataStr);
              const content = chunk.choices?.[0]?.delta?.content;
              if (content) {
                callbacks.onToken(content);
              }
            } catch (e) {
              console.error('Error parsing SSE chunk', e);
            }
          }
        }
      }
    }

    callbacks.onComplete();
  } catch (err: any) {
    if (!signal?.aborted) {
      const errorMessage = err?.message || 'Unable to connect to ProX AI inference gateway.';
      callbacks.onError?.(`${modelId.toUpperCase()} model engine unavailable: ${errorMessage}`);
    }
  }
}
