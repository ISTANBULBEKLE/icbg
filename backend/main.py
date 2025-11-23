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
from services.ingestion import DocumentIngestionService
from services.llm import ContentEngine
from services.image_gen import ImageEngine

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

# Initialize Services
print("Initializing Services...")
pdf_generator = PDFGenerator()
ingestion_service = DocumentIngestionService()
content_engine = ContentEngine()
image_engine = ImageEngine()
print("Services Initialized.")

async def process_book_generation(job_id: str, filename: str, specs: dict, segmentation: dict):
    """
    Executes the book generation pipeline.
    """
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 5
        jobs[job_id]["message"] = "Starting ingestion..."
        
        # 1. Ingestion
        file_path = f"temp/{filename}"
        source_text = await ingestion_service.ingest_pdf(
            file_path,
            section_description=segmentation.get("sectionDescription"),
            additional_context=segmentation.get("additionalContext"),
            page_start=segmentation.get("pageStart"),
            page_end=segmentation.get("pageEnd")
        )
        
        if not source_text:
            raise Exception("Failed to extract text from document.")
            
        jobs[job_id]["progress"] = 20
        jobs[job_id]["message"] = "Generating story..."
        
        # 2. Story Generation
        pages = await content_engine.generate_story(source_text, specs)
        
        jobs[job_id]["progress"] = 40
        jobs[job_id]["message"] = "Creating illustrations..."
        
        # 3. Image Generation
        total_pages = len(pages)
        for i, page in enumerate(pages):
            prompt = page.get("image_prompt", "")
            if prompt:
                # Add style modifiers based on theme
                style_prompt = f"children's book illustration, {specs.get('theme', 'islamic art style')}, {prompt}, warm colors, soft lighting, high quality"
                image_path = await image_engine.generate_image(style_prompt)
                page["image_path"] = image_path
            
            # Update progress incrementally
            current_progress = 40 + int((i + 1) / total_pages * 40) # 40% to 80%
            jobs[job_id]["progress"] = current_progress
            jobs[job_id]["message"] = f"Illustrating page {i+1} of {total_pages}..."
        
        jobs[job_id]["progress"] = 85
        jobs[job_id]["message"] = "Assembling PDF..."
        
        # 4. PDF Construction
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
    
    background_tasks.add_task(
        process_book_generation, 
        job_id, 
        file.filename, 
        jobs[job_id]["specs"],
        {
            "sectionDescription": sectionDescription,
            "additionalContext": additionalContext,
            "pageStart": pageStart,
            "pageEnd": pageEnd
        }
    )
    
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
