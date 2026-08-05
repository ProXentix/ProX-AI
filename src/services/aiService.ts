import { ModelId, Citation, ReasoningStep } from '../types/chat';

interface StreamCallbacks {
  onReasoningStart?: () => void;
  onReasoningStep?: (step: ReasoningStep) => void;
  onCitations?: (citations: Citation[]) => void;
  onToken: (token: string) => void;
  onComplete: () => void;
  onError?: (error: string) => void;
}

export async function generateStreamResponse(
  prompt: string,
  modelId: ModelId,
  webSearchEnabled: boolean,
  callbacks: StreamCallbacks,
  signal?: AbortSignal
) {
  try {
    const isReasoningModel = modelId === 'logix' || modelId === 'neurix';

    // 1. Simulate Reasoning / Thinking process if applicable
    if (isReasoningModel) {
      callbacks.onReasoningStart?.();
      await delay(400);

      const steps: ReasoningStep[] = [
        {
          id: 'step-1',
          title: 'Parsing query intent & context window',
          content: `Extracting semantic tokens from prompt "${prompt.slice(0, 40)}..."`,
        },
        {
          id: 'step-2',
          title: 'Generating architectural solution & code blocks',
          content: 'Optimizing syntactic structure, checking TypeScript types, and styling via Tailwind CSS.',
        },
      ];

      for (const step of steps) {
        if (signal?.aborted) return;
        callbacks.onReasoningStep?.(step);
        await delay(500);
      }
    }

    // 2. Simulate Web Citations if Web Search is enabled
    if (webSearchEnabled) {
      const citations: Citation[] = [
        {
          id: 'cit-1',
          title: 'Official Documentation & Standards 2026',
          url: 'https://docs.prox.ai/specifications',
          snippet: 'Comprehensive specification for modern AI web interfaces and high-performance streaming architectures.',
          domain: 'docs.prox.ai',
        },
        {
          id: 'cit-2',
          title: 'High-Performance Web Design Benchmarks',
          url: 'https://developer.mozilla.org/en-US/docs/Web/Performance',
          snippet: 'Optimizing web application rendering speed, animation frame rates, and memory footprint.',
          domain: 'developer.mozilla.org',
        },
      ];
      callbacks.onCitations?.(citations);
      await delay(400);
    }

    // 3. Select Response Template based on prompt keywords
    const responseText = getResponseContentForPrompt(prompt, modelId);
    
    // 4. Stream tokens chunks with slight jitter for natural typing feel
    const words = responseText.split(' ');
    for (let i = 0; i < words.length; i++) {
      if (signal?.aborted) return;
      const word = words[i] + (i === words.length - 1 ? '' : ' ');
      callbacks.onToken(word);
      await delay(Math.floor(Math.random() * 20) + 15);
    }

    callbacks.onComplete();
  } catch (err) {
    if (!signal?.aborted) {
      callbacks.onError?.('An error occurred while generating the response.');
    }
  }
}

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function getResponseContentForPrompt(prompt: string, modelId: ModelId): string {
  const p = prompt.toLowerCase();

  if (p.includes('code') || p.includes('function') || p.includes('component') || p.includes('react') || p.includes('typescript')) {
    return `### High-Performance TypeScript Component

Here is a modular, production-ready implementation tailored for **${modelId}**:

\`\`\`typescript
import React, { useState, useCallback, useTransition } from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  changePercentage: number;
  trend: 'up' | 'down' | 'neutral';
}

export const MetricCard: React.FC<MetricCardProps> = React.memo(({
  title,
  value,
  changePercentage,
  trend,
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isPending, startTransition] = useTransition();

  const handleRefresh = useCallback(() => {
    startTransition(() => {
      // Execute state transition without blocking UI main thread
      console.log(\`Refreshing metric data for: \${title}\`);
    });
  }, [title]);

  const isPositive = trend === 'up';

  return (
    <div
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={\`relative p-5 rounded-2xl border transition-all duration-300 \${
        isHovered
          ? 'bg-slate-800/90 border-emerald-500/40 shadow-lg shadow-emerald-500/10 -translate-y-0.5'
          : 'bg-slate-900/60 border-slate-800 shadow-sm'
      }\`}
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          {title}
        </span>
        <button
          onClick={handleRefresh}
          disabled={isPending}
          className="text-slate-500 hover:text-emerald-400 transition-colors"
        >
          ⚡
        </button>
      </div>

      <div className="flex items-baseline justify-between">
        <span className="text-2xl font-bold text-slate-100 tracking-tight">
          {value}
        </span>
        <span
          className={\`text-xs font-semibold px-2 py-0.5 rounded-full border \${
            isPositive
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
              : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
          }\`}
        >
          {isPositive ? '↑' : '↓'} {Math.abs(changePercentage)}%
        </span>
      </div>
    </div>
  );
});

MetricCard.displayName = 'MetricCard';
\`\`\`

#### Key Architecture Highlights:
- **Automatic React 19 Transitions**: Non-blocking updates using \`useTransition\`.
- **Custom Tailwind Glassmorphic Hover**: Soft glow and border highlights.
- **Memoized Callbacks**: Prevents redundant re-renders.`;
  }

  if (p.includes('mermaid') || p.includes('flowchart') || p.includes('architecture') || p.includes('system')) {
    return `### Microservices Architecture Blueprint

Here is an enterprise system design for scalable AI event processing:

\`\`\`mermaid
graph TD
    Client[Web Client - React 19] --> API[API Gateway / Edge Proxy]
    API --> Auth[OAuth2 / JWT Service]
    API --> StreamEngine[Real-Time Event Streamer]
    StreamEngine --> Kafka{Apache Kafka Cluster}
    Kafka --> LLMWorker[LLM Worker Ingestion Node]
    LLMWorker --> VectorDB[(Qdrant Vector Database)]
    LLMWorker --> ModelInference[DeepSeek R1 / Claude API]
    ModelInference --> Cache[(Redis Cache Layer)]
    Cache --> Client
\`\`\`

#### Component Breakdown:
| Layer | Technology | Primary Function |
| :--- | :--- | :--- |
| **Frontend** | React 19 + Zustand | Streamed Token Rendering & WebSockets |
| **Messaging** | Apache Kafka | Event Queuing & Load Balancing |
| **Vector DB** | Qdrant | RAG Semantic Context Indexing |
| **Cache** | Redis 7 | Prompt Response & Token Cache |`;
  }

  if (p.includes('math') || p.includes('formula') || p.includes('equation') || p.includes('proof')) {
    return `### Euler's Identity & Complex Analysis

One of the most remarkable results in mathematical analysis connects five fundamental constants:

$$ e^{i\\pi} + 1 = 0 $$

#### Derivation via Taylor Series Expansion:

Recall the power series for $e^z$, $\\sin z$, and $\\cos z$:

$$ e^z = \\sum_{n=0}^{\\infty} \\frac{z^n}{n!} = 1 + z + \\frac{z^2}{2!} + \\frac{z^3}{3!} + \\cdots $$

Substituting $z = i\\theta$ where $i^2 = -1$:

$$ e^{i\\theta} = 1 + i\\theta - \\frac{\\theta^2}{2!} - i\\frac{\\theta^3}{3!} + \\frac{\\theta^4}{4!} + \\cdots $$

Grouping real and imaginary components:

$$ e^{i\\theta} = \\left(1 - \\frac{\\theta^2}{2!} + \\frac{\\theta^4}{4!} - \\cdots\\right) + i \\left(\\theta - \\frac{\\theta^3}{3!} + \\frac{\\theta^5}{5!} - \\cdots\\right) $$

$$ e^{i\\theta} = \\cos\\theta + i\\sin\\theta $$

Setting $\\theta = \\pi$:

$$ e^{i\\pi} = \\cos\\pi + i\\sin\\pi = -1 + 0 = -1 \\implies e^{i\\pi} + 1 = 0 $$`;
  }

  return `I have analyzed your query using **${modelId}**.

Here is a structured, step-by-step response to help you achieve your objective:

1. **Understand Core Requirements**: Align the problem statement with target outcomes and best practices.
2. **Execute Clean Strategy**: Utilize modular, scalable building blocks that guarantee consistency.
3. **Verify & Refine**: Ensure high precision, zero edge-case regressions, and smooth performance.

> **Note**: You can customize system persona defaults or enable live Web Search in the top control bar at any time for real-time web citations!

Is there a specific detail or code implementation you would like to explore further?`;
}
