# Islamic Children's Book Generator (ICBG)

## Purpose
ICBG is an AI-powered application designed to transform existing Islamic literature (PDFs, EPUBs) into engaging, illustrated children's stories. It ensures the content is fact-based and suitable for specific age groups while adding visual appeal.

## How It Works
1.  **Upload**: User uploads a source document (e.g., a book on Prophet's life).
2.  **Ingest**: The system extracts relevant text from the document.
3.  **Generate**:
    -   **Story**: A local LLM (`SmolLM-1.7B`) adapts the text into a 10-page story.
    -   **Illustrate**: A local Diffusion model (`SD-Turbo`) generates images for each page.
4.  **Assemble**: A downloadable PDF is created with images at the top and text at the bottom.

## Tech Stack
-   **Frontend**: Next.js 16, TypeScript, CSS Modules.
-   **Backend**: FastAPI, Python 3.11.
-   **AI Models**:
    -   Text: `HuggingFaceTB/SmolLM-1.7B-Instruct` (via `transformers`)
    -   Image: `stabilityai/sd-turbo` (via `diffusers`)
-   **Tools**: PyMuPDF (PDF parsing), ReportLab (PDF generation).

## Quick Start

### Prerequisites
-   Node.js & npm
-   Python 3.10+
-   Mac with Apple Silicon (recommended for MPS acceleration)

### Commands

**Start the Application:**
```bash
./start-dev.sh
```
*This script handles starting both the backend (port 8000) and frontend (port 3000).*

**Stop the Application:**
Press `Ctrl+C` in the terminal. The script will automatically kill all related processes.

**Install Dependencies:**
```bash
make install
```

## Documentation
For detailed documentation, see the `frontend/docs/` directory:
-   [Architecture Overview](frontend/docs/architecture_overview.md)
-   [Frontend Docs](frontend/docs/frontend_documentation.md)
-   [Backend Docs](frontend/docs/backend_documentation.md)
-   [AI Logic](frontend/docs/ai_logic.md)
