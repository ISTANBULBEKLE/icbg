# Project Purpose & Architecture

## Project Summary
The **Islamic Children Book Generator** is a web application designed to transform complex Islamic literature (PDFs, EPUBs, Web resources) into engaging, 20-page digital children's books. 

**Core Philosophy**:
- **Fact-Based**: Strictly adheres to Islamic facts derived from the source text (e.g., Quran, Hadith, Seerah).
- **Engaging**: Uses GenAI to simplify language for children and create relevant, modest digital art.
- **Format**: Each page consists of half text and half illustration.

## How It Works
1.  **Upload**: The user uploads a source document (e.g., "Surah Maryam" or a biography of a Prophet).
2.  **Specify**: The user sets parameters:
    -   **Theme**: e.g., "Honesty", "Patience".
    -   **Humor Level**: 1-10 scale.
    -   **Age Group**: Target audience (e.g., 6-8 years).
3.  **Generate**: The system processes the input and produces a downloadable PDF.

## Step-by-Step Implementation (Backend Logic)

### 1. Document Ingestion
-   **Input**: User uploads a file via the Next.js frontend.
-   **Process**: 
    -   The FastAPI backend receives the file.
    -   `PyMuPDF` (for PDFs) or `BeautifulSoup` (for Web/EPUB) extracts the raw text.
    -   Text is cleaned and chunked for processing.

### 2. Content Analysis & Generation (Text)
-   **Engine**: Local LLM (via **Ollama**, e.g., Llama 3 or Mistral).
-   **Process**:
    -   **Fact Extraction**: The LLM extracts key facts related to the user's specified theme.
    -   **Storyboarding**: The LLM creates a 20-page storyboard. Each "page" entry contains:
        -   **Story Text**: Simplified, age-appropriate narrative.
        -   **Image Prompt**: A detailed description for the image generator (ensuring Islamic appropriateness).

### 3. Image Generation
-   **Engine**: Local **Stable Diffusion** (via HuggingFace `diffusers`).
-   **Process**:
    -   The backend iterates through the 20 image prompts generated in step 2.
    -   Stable Diffusion generates a high-quality digital art image for each page.

### 4. PDF Assembly
-   **Engine**: `ReportLab`.
-   **Process**:
    -   The system combines the generated text and images.
    -   Layout: Top half image, bottom half text (or vice versa).
    -   Final output is saved as a PDF and returned to the user.

## Tech Stack

### Frontend
-   **Framework**: **Next.js v16** (App Router).
-   **Language**: TypeScript.
-   **Styling**: **Pure CSS** (CSS Modules) with an Islamic-inspired design system.
-   **State**: React Hooks (`useState`).

### Backend
-   **Framework**: **FastAPI** (Python).
-   **AI Orchestration**: LangChain (optional) or direct API calls.
-   **Local AI Models**:
    -   **Text**: Ollama.
    -   **Image**: Stable Diffusion.
-   **Libraries**: `PyMuPDF`, `ReportLab`, `Diffusers`, `Torch`.

### Infrastructure
-   **DevOps**: `Makefile` for unified development commands.
-   **Hardware Requirement**: GPU recommended for local inference.
