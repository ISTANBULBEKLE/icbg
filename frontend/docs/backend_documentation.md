# Backend Documentation

## Overview
The backend is a FastAPI application that orchestrates the AI pipeline. It handles file uploads, manages asynchronous background tasks for generation, and serves the final PDF files.

## API Endpoints

### `POST /generate`
-   **Description**: Initiates the book generation process.
-   **Parameters**:
    -   `file`: UploadFile (PDF/EPUB)
    -   `theme`: str
    -   `humor`: int
    -   `ageGroup`: str
    -   `sectionDescription`: str (optional)
    -   `pageStart`: int (optional)
    -   `pageEnd`: int (optional)
-   **Behavior**:
    1.  Saves the uploaded file to `temp/`.
    2.  Creates a unique `job_id`.
    3.  Initializes a job entry in the in-memory `jobs` dictionary.
    4.  Spawns a `BackgroundTask` to run `process_book_generation`.
    5.  Returns the `job_id` immediately.

### `GET /events/{job_id}`
-   **Description**: Streams progress updates for a specific job.
-   **Mechanism**: Infinite generator loop that yields data in SSE format.
-   **Polling**: Checks the `jobs` dictionary state every 1 second.

### `GET /download/{job_id}`
-   **Description**: Downloads the generated PDF.
-   **Validation**: Checks if the job is completed and the file exists.

## Core Services

### 1. `DocumentIngestionService` (`services/ingestion.py`)
-   **Library**: `PyMuPDF` (fitz)
-   **Logic**: Opens the PDF, iterates through the specified page range, and extracts text. Prepends context/section description to guide the LLM.

### 2. `ContentEngine` (`services/llm.py`)
-   **Library**: `transformers`
-   **Model**: `HuggingFaceTB/SmolLM-1.7B-Instruct`
-   **Configuration**:
    -   **Precision**: `float32` (for stability on MPS).
    -   **Context**: Increased `max_new_tokens` to 2048.
-   **Logic**:
    -   Constructs a prompt with system instructions (Persona: Children's Author).
    -   Injects the extracted source text.
    -   Requests a structured output (**10 pages**, Text + Image Prompts).
    -   **Robust Parsing**: Handles unstructured output and missing prefixes.

### 3. `ImageEngine` (`services/image_gen.py`)
-   **Library**: `diffusers`
-   **Model**: `stabilityai/sd-turbo`
-   **Logic**:
    -   Takes a prompt from the ContentEngine.
    -   Adds style modifiers (e.g., "children's book illustration", "warm colors").
    -   Runs inference (1 step for Turbo).
    -   Saves the image to `generated_images/`.

### 4. `PDFGenerator` (`services/pdf_builder.py`)
-   **Library**: `ReportLab`
-   **Logic**:
    -   Creates a canvas.
    -   Draws a Title Page.
    -   Iterates through pages:
        -   **Image**: Drawn at the **Top Half** (y=350-650).
        -   **Text**: Drawn at the **Bottom Half** (y=400 downwards).
    -   Saves the final PDF.
