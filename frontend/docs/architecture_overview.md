# Islamic Children's Book Generator (ICBG) - Architecture Overview

## Project Description
The Islamic Children's Book Generator (ICBG) is an AI-powered application that transforms existing Islamic literature (PDFs, EPUBs) into engaging, fact-based children's stories. It leverages local Large Language Models (LLMs) and Image Generation models to create illustrated PDF books tailored to specific age groups, themes, and humor levels.

## Business Logic
1.  **User Input**: Users upload a source document and specify parameters (Age Group, Theme, Humor Level, Focus Section).
2.  **Ingestion**: The system extracts text from the uploaded document, focusing on relevant sections if specified.
3.  **Story Generation**: An AI model adapts the extracted content into a 5-page children's story.
4.  **Illustration**: An AI image generator creates unique illustrations for each page based on the story content and theme.
5.  **PDF Assembly**: The text and images are compiled into a downloadable PDF.
6.  **History**: Users can view and download their previously generated books.

## Technology Stack

### Frontend
-   **Framework**: Next.js 16 (React)
-   **Language**: TypeScript
-   **Styling**: CSS Modules (Vanilla CSS)
-   **State Management**: React Hooks (`useState`, `useEffect`) + `localStorage` for history persistence.
-   **Communication**: REST API (FormData for uploads) + Server-Sent Events (SSE) for real-time progress updates.

### Backend
-   **Framework**: FastAPI (Python)
-   **Server**: Uvicorn
-   **Task Queue**: FastAPI `BackgroundTasks` (In-memory)
-   **PDF Processing**: `PyMuPDF` (fitz)
-   **PDF Generation**: `ReportLab`

### AI & Machine Learning (Local)
-   **Orchestration**: `Transformers` & `Diffusers` libraries (Hugging Face)
-   **Text Generation (LLM)**: `HuggingFaceTB/SmolLM-1.7B-Instruct`
    -   *Reasoning*: Lightweight, fast, instruction-tuned, suitable for creative writing on consumer hardware.
-   **Image Generation**: `stabilityai/sd-turbo`
    -   *Reasoning*: Extremely fast (1-step inference), optimized for real-time applications.
-   **Hardware Acceleration**: MPS (Metal Performance Shaders) for macOS / CUDA for NVIDIA.

## Directory Structure
```
icbg/
├── backend/
│   ├── main.py                 # API Entry point & Orchestration
│   ├── services/
│   │   ├── ingestion.py        # PDF Text Extraction
│   │   ├── llm.py              # Story Generation (SmolLM)
│   │   ├── image_gen.py        # Image Generation (SD-Turbo)
│   │   └── pdf_builder.py      # PDF Assembly (ReportLab)
│   ├── temp/                   # Temporary uploads
│   ├── generated_books/        # Output PDFs
│   └── generated_images/       # Intermediate images
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx        # Main UI Controller
│   │   │   └── page.module.css # Styles
│   │   └── components/         # Reusable UI Components
│   └── docs/                   # Project Documentation
├── Makefile                    # Build & Run commands
└── start-dev.sh                # Robust startup script (handles process cleanup)
```
