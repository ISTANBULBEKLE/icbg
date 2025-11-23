# Frontend Documentation

## Overview
The frontend is a single-page application built with Next.js 16. It provides an intuitive interface for users to upload documents, configure book settings, and view the generation progress in real-time.

## Key Components

### `page.tsx` (Main Controller)
-   **State**: Manages global state for the file, segmentation params, book specs, generation progress, and history.
-   **Logic**:
    -   `handleGenerate`: Submits the form data to `POST /generate`.
    -   **SSE Listener**: Connects to `GET /events/{job_id}` to receive real-time updates (progress %, status messages).
    -   `addToHistory`: Persists completed books to `localStorage`.
    -   `handleReset`: Resets the UI to the initial state for a new session.

### `BookHistoryDrawer.tsx`
-   **Purpose**: Displays a list of the last 5 generated books.
-   **Props**: 
    -   `books: Book[]`
    -   `onDelete: (id: string) => void`
-   **Styling**: Sticky sidebar on the left.
-   **Persistence**: Reads/Writes to browser `localStorage` key `bookHistory`.
-   **Features**:
    -   **Download**: Link to download the PDF.
    -   **Delete**: Button to remove the book from history and storage.

### `UploadZone.tsx`
-   **Purpose**: Drag-and-drop file upload area.
-   **Validation**: Accepts PDF and EPUB formats.

### `DocumentSegmentation.tsx`
-   **Purpose**: Form fields for specifying which part of the document to process.
-   **Fields**: Section Description, Additional Context, Page Range (Start/End).

### `BookSpecs.tsx`
-   **Purpose**: Controls for customizing the output.
-   **Fields**: Theme (Text input), Humor (Slider 1-10), Age Group (Dropdown).

## API Integration

### 1. Trigger Generation
-   **Endpoint**: `POST http://localhost:8000/generate`
-   **Body**: `FormData` (file, theme, humor, ageGroup, sectionDescription, etc.)
-   **Response**: `{ "job_id": "uuid", "status": "submitted" }`

### 2. Progress Stream
-   **Endpoint**: `GET http://localhost:8000/events/{job_id}`
-   **Format**: Server-Sent Events (text/event-stream)
-   **Events**:
    ```json
    {
      "status": "processing",
      "progress": 40,
      "message": "Generating story...",
      "result_url": null
    }
    ```

### 3. Download
-   **Endpoint**: `GET http://localhost:8000/download/{job_id}`
-   **Response**: Binary PDF file.
