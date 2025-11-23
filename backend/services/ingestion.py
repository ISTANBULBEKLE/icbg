import fitz  # PyMuPDF
from typing import Optional

class DocumentIngestionService:
    def __init__(self):
        pass

    async def ingest_pdf(
        self, 
        file_path: str,
        section_description: str = "",
        additional_context: str = "",
        page_start: Optional[int] = None,
        page_end: Optional[int] = None
    ) -> str:
        """
        Extract text from PDF with optional section filtering.
        """
        try:
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            # Determine page range
            start_idx = 0
            end_idx = total_pages
            
            if page_start is not None:
                start_idx = max(0, page_start - 1)  # Convert to 0-indexed
            if page_end is not None:
                end_idx = min(total_pages, page_end)
            
            # Extract text from specified page range
            extracted_text = ""
            for page_num in range(start_idx, end_idx):
                if page_num < total_pages:
                    page = doc[page_num]
                    extracted_text += page.get_text() + "\n"
            
            doc.close()
            
            # Prepend context if provided
            if section_description:
                extracted_text = f"FOCUS SECTION: {section_description}\nCONTEXT: {additional_context}\n\nDOCUMENT CONTENT:\n{extracted_text}"
            
            return extracted_text.strip()
            
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            return ""

    async def ingest_web(self, url: str) -> str:
        # Placeholder for web ingestion
        return ""

