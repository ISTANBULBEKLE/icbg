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
        file_path = f"source_files/{filename}"
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
        # Content Generation
        jobs[job_id]["progress"] = 40
        jobs[job_id]["message"] = "Generating story and title..."
        
        story_data = await content_engine.generate_story(source_text, specs)
        pages = story_data.get("pages", [])
        book_title = story_data.get("title", "My Islamic Children's Book")
        
        # Image Generation
        jobs[job_id]["progress"] = 60
        jobs[job_id]["message"] = "Creating illustrations..."
        
        for i, page in enumerate(pages):
            image_prompt = page.get("image_prompt", "")
            if image_prompt:
                # Add style modifiers based on theme
                style_prompt = f"children's book illustration, {specs.get('theme', 'islamic art style')}, {image_prompt}, warm colors, soft lighting, high quality"
                image_path = await image_engine.generate_image(style_prompt)
                page["image_path"] = image_path
            
            # Update progress per page
            jobs[job_id]["progress"] = 60 + int((i / len(pages)) * 30)
            jobs[job_id]["message"] = f"Illustrating page {i+1} of {len(pages)}..."
        
        # PDF Construction
        jobs[job_id]["progress"] = 90
        jobs[job_id]["message"] = "Assembling PDF..."
        
        output_filename = f"book_{job_id}.pdf"
        output_path = await pdf_generator.create_book_pdf(pages, output_filename, title=book_title)
        
        jobs[job_id]["progress"] = 100
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["message"] = "Book generated successfully!"
        jobs[job_id]["result_url"] = f"/download/{job_id}"
        jobs[job_id]["file_path"] = output_path
        jobs[job_id]["book_title"] = book_title # Pass title to frontend
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["message"] = f"Error: {str(e)}"
        print(f"Job {job_id} failed: {e}")
    finally:
        # Create manifest for cleanup
        manifest = {
            "pdf_path": jobs[job_id].get("file_path"),
            "images": [p.get("image_path") for p in pages if p.get("image_path")]
        }
        manifest_path = f"generated_books/manifest_{job_id}.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f)
            
        # NOTE: We no longer delete the source file here to allow for "Recent Source Files" download.
        # It will be deleted via the explicit DELETE endpoint.

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
    # Save uploaded file to persistent source_files directory
    os.makedirs("source_files", exist_ok=True)
    file_path = f"source_files/{file.filename}"
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
                "result_url": job.get("result_url"),
                "book_title": job.get("book_title")
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
    book_title = jobs[job_id].get("book_title", "my_islamic_book")
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    # Sanitize filename
    safe_title = "".join([c for c in book_title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    filename = f"{safe_title}.pdf"
        
    return FileResponse(file_path, filename=filename, media_type="application/pdf")

# --- Source File Management ---

@app.get("/source_files/{filename}")
async def download_source_file(filename: str):
    file_path = f"source_files/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Source file not found")
    return FileResponse(file_path, filename=filename)

@app.delete("/source_files/{filename}")
async def delete_source_file(filename: str):
    file_path = f"source_files/{filename}"
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"status": "deleted", "file": filename}
    raise HTTPException(status_code=404, detail="Source file not found")

# --- Generated Book Management ---

@app.delete("/books/{job_id}")
async def delete_book(job_id: str):
    # 1. Try to find manifest
    manifest_path = f"generated_books/manifest_{job_id}.json"
    
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
            
            # Delete PDF
            pdf_path = manifest.get("pdf_path")
            if pdf_path and os.path.exists(pdf_path):
                os.remove(pdf_path)
                
            # Delete Images
            for img_path in manifest.get("images", []):
                if img_path and os.path.exists(img_path):
                    os.remove(img_path)
            
            # Delete Manifest
            os.remove(manifest_path)
            
            return {"status": "deleted", "job_id": job_id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error cleaning up book: {str(e)}")
    else:
        # Fallback: Try to find just the PDF if manifest missing
        pdf_path = f"generated_books/book_{job_id}.pdf"
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            return {"status": "deleted", "job_id": job_id, "note": "Manifest not found, deleted PDF only"}
            
        raise HTTPException(status_code=404, detail="Book resources not found")
