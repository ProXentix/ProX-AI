# ProX AI Architecture

## 1. Current Frontend Architecture
The current ProX AI interface is a modern single-page application built with:
- **Framework:** React 19 + TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS 4, `clsx`, `tailwind-merge`
- **State Management:** Zustand (global state) & React Query (server state/caching)
- **Routing:** React Router v7
- **UI Components:** Lucide React for icons, Framer Motion for animations
- **Markdown & Code Rendering:** `react-markdown`, `remark-gfm`, `remark-math`, `rehype-katex`, `katex`, `prismjs`, `mermaid`

## 2. Existing Functionality
The frontend contains structural foundations for:
- Layout, routing, and navigation
- A chat interface and prompt composer
- Projects and explore views
- A sidebar and standard UI primitives
- Syntax highlighting and math rendering

## 3. Missing Functionality
Currently, the system is a frontend prototype. It lacks:
- **Backend Infrastructure:** No API gateway, auth, or database.
- **AI Integration:** No connection to a model inference engine.
- **Model Registry:** No dynamic detection of available models.
- **State Persistence:** Interactions are either local or non-persistent.
- **Real-Time Streaming:** The chat UI needs connection to a streaming backend (e.g., SSE or WebSockets).

## 4. Proposed Backend
The backend should be robust and decouple the frontend from the AI infrastructure.
- **API Gateway:** Handles authentication, rate limiting, and request validation.
- **Model Router:** Dynamically routes requests based on task (Neurix, Logix, Optix).
- **Core Services:** Conversation Service, Memory Service (RAG/Vector DB), Agent Service.
- **Tech Stack:** Node.js/TypeScript (e.g., NestJS or Express) or Python (e.g., FastAPI), integrating closely with an inference backend.

## 5. Model Architecture Overview
ProX AI will develop three specialized model families instead of a monolithic model:
- **Neurix:** General-purpose AI.
- **Logix:** Coding & Reasoning AI.
- **Optix:** Vision & Image AI.
These will operate through a central model registry tracking their versions, quantization, and deployment status.

## 6. Neurix Architecture (General AI)
- **Role:** Everyday productivity, writing, instruction following.
- **Architecture:** Decoder-only Transformer.
- **Focus:** Low latency, general knowledge, multilingual capabilities (specialized for Indian languages).

## 7. Logix Architecture (Coding & Reasoning)
- **Role:** Complex problem solving, coding, mathematics.
- **Architecture:** Reasoning-optimized language model.
- **Focus:** Structured outputs, multi-step reasoning, tool usage, long-context window, and deep understanding of ProXPL.

## 8. Optix Architecture (Vision & Image)
- **Role:** Multimodal interaction.
- **Architecture:** Modular composite (Vision Encoder + Multimodal Projector + Language Decoder + Image Generation Pipeline).
- **Focus:** OCR, screenshot/diagram analysis, UI understanding, image-to-text, and text-to-image generation.

## 9. Training Infrastructure
A dedicated training module (`prox-ai/training`) will be separate from the production application.
- **Capabilities:** Checkpointing, mixed-precision, distributed training, experiment tracking.
- **Hardware Agnosticism:** Scalable from local single-GPU experiments up to multi-node clusters.

## 10. Dataset Pipeline
A legally and ethically sourced data pipeline is required:
- **Stages:** Ingestion → License Check → Deduplication → Language Detection → Quality Filtering → PII/Safety Filtering → Tokenization.
- **Versioning:** Strict tracking of dataset versions (e.g., `prox-dataset-v1.0`).

## 11. Evaluation Infrastructure
- **ProXBench:** A comprehensive internal benchmark suite.
- **Metrics:** Covers General, Reasoning, Coding, Math, Multilingual, Vision, Tool Use, and Safety.
- **Requirement:** No model deployment without reproducible evaluation benchmarks compared against previous versions.

## 12. Inference Infrastructure
A dedicated inference engine abstraction sits behind the AI Gateway:
- **Technologies:** vLLM, TensorRT-LLM, or llama.cpp.
- **Features:** Continuous batching, streaming output, KV caching, multi-quantization support (FP16, INT8, INT4).

## 13. Database
- **Relational:** PostgreSQL for application state (users, conversations, model registries).
- **Vector/Semantic:** Specialized vector store for project context, user memory, and RAG.

## 14. API
- **Design:** RESTful APIs or gRPC for internal microservices. Exposes standardized endpoints (`/v1/chat/completions`, `/v1/models`, `/v1/images/generations`).
- **SDK:** Future plans include TypeScript and Python SDKs wrapping these endpoints.

## 15. Security
- Complete isolation of model infrastructure from the frontend.
- Secure secrets management (never exposing DB, GPU, or internal API keys).
- Input filtering, sandbox code execution (especially for Logix), and prompt injection defenses.

## 16. Deployment
- **Staged Environments:** Development (mocked/local models) → Staging → Production.
- **Model Statuses:** The UI dynamically adapts based on if a model is "Training", "Development", or "Available".

## 17. Cost Considerations
- **Start Small:** Train tiny models to validate the pipeline before scaling.
- **Optimize Inference:** Aggressively benchmark quantization levels to reduce VRAM requirements without degrading quality.

## 18. Development Roadmap (Next Steps)
1. **Phase 1 (ProX AI Foundation):** Setup DB, API Gateway, and Model Registry. Connect the React frontend to the backend with streaming.
2. **Phase 2 (Neurix):** Implement the dataset pipeline and tokenizer, starting with Phase A (tiny models).
3. **Phase 3 (Logix):** Curate reasoning datasets, build code evaluation sandboxes, and perform coding-specific fine-tuning.
4. **Phase 4 (Optix):** Integrate a vision encoder and build the image generation pipeline.
5. **Phase 5 (ProX Agents):** Introduce memory, RAG, tool use, and complex agent planning.
6. **Phase 6 (Production):** Finalize security, scaling, monitoring, and robust CI/CD.
