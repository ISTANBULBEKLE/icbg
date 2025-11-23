from fastapi import FastAPI, BackgroundTasks, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from typing import Annotated
import shutil
import os
import asyncio
import json
import uuid
from services.pdf_builder import PDFGenerator

app = FastAPI(title="Islamic Children Book Generator API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store
jobs = {}

pdf_generator = PDFGenerator()

async def process_book_generation(job_id: str, filename: str, specs: dict):
    """
    Simulates the book generation pipeline with progress updates.
    """
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 0
        jobs[job_id]["message"] = "Starting ingestion..."
        
        # Simulate Ingestion
        await asyncio.sleep(2)
        jobs[job_id]["progress"] = 20
        jobs[job_id]["message"] = "Analyzing content..."
        
        # Simulate Content Generation
        await asyncio.sleep(2)
        jobs[job_id]["progress"] = 40
        jobs[job_id]["message"] = "Generating story..."
        
        # Simulate Image Generation
        await asyncio.sleep(3)
        jobs[job_id]["progress"] = 70
        jobs[job_id]["message"] = "Creating illustrations..."
        
        # Simulate PDF Construction
        await asyncio.sleep(2)
        jobs[job_id]["progress"] = 90
        jobs[job_id]["message"] = "Assembling PDF..."
        
        # Generate Dummy PDF
        pages = [
            {"text": f"This is a story about {specs.get('theme', 'something')}.\nIdeally suited for {specs.get('ageGroup', 'children')}."},
            {"text": "Once upon a time..."}
        ]
        output_filename = f"book_{job_id}.pdf"
        output_path = await pdf_generator.create_book_pdf(pages, output_filename)
        
        jobs[job_id]["progress"] = 100
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["message"] = "Book generated successfully!"
        jobs[job_id]["result_url"] = f"/download/{job_id}"
        jobs[job_id]["file_path"] = output_path
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["message"] = f"Error: {str(e)}"
        print(f"Job {job_id} failed: {e}")
    finally:
        # Cleanup temporary file
        file_path = f"temp/{filename}"
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Cleaned up temporary file: {file_path}")
            except Exception as cleanup_error:
                print(f"Failed to cleanup file {file_path}: {cleanup_error}")

@app.post("/generate")
async def generate_book(
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File()],
    theme: Annotated[str, Form()],
    humor: Annotated[int, Form()],
    ageGroup: Annotated[str, Form()],
    # Section selection parameters
    sectionDescription: Annotated[str, Form()] = "",
    additionalContext: Annotated[str, Form()] = "",
    pageStart: Annotated[int | None, Form()] = None,
    pageEnd: Annotated[int | None, Form()] = None
):
    # Save uploaded file temporarily
    os.makedirs("temp", exist_ok=True)
    file_path = f"temp/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "id": job_id,
        "status": "pending",
        "progress": 0,
        "message": "Queued",
        "specs": {
            "theme": theme,
            "humor": humor,
            "ageGroup": ageGroup
        }
    }
    
    background_tasks.add_task(process_book_generation, job_id, file.filename, jobs[job_id]["specs"])
    
    return {"job_id": job_id, "status": "submitted"}

@app.get("/events/{job_id}")
async def event_stream(job_id: str):
    async def event_generator():
        if job_id not in jobs:
            yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
            return

        while True:
            job = jobs[job_id]
            data = {
                "status": job["status"],
                "progress": job["progress"],
                "message": job["message"],
                "result_url": job.get("result_url")
            }
            yield f"data: {json.dumps(data)}\n\n"
            
            if job["status"] in ["completed", "failed"]:
                break
            
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/download/{job_id}")
async def download_book(job_id: str):
    if job_id not in jobs or jobs[job_id]["status"] != "completed":
        raise HTTPException(status_code=404, detail="Book not found or not ready")
    
    file_path = jobs[job_id].get("file_path")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(file_path, filename="my_islamic_book.pdf", media_type="application/pdf")
