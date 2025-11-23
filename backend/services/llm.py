from transformers import pipeline
import torch

class ContentEngine:
    def __init__(self):
        print("Loading LLM model...")
        # Use a small, fast instruction-tuned model
        self.model_id = "HuggingFaceTB/SmolLM-1.7B-Instruct"
        
        # Determine device
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"Using device: {device}")
        
        try:
            self.pipe = pipeline(
                "text-generation",
                model=self.model_id,
                device=device,
                torch_dtype=torch.float32, # Use float32 for stability on MPS
                max_new_tokens=2048, # Increased for 10 pages
            )
            print("LLM loaded successfully.")
        except Exception as e:
            print(f"Failed to load LLM: {e}")
            self.pipe = None

    async def generate_story(self, source_text: str, params: dict) -> dict:
        if not self.pipe:
            print("LLM not loaded, returning dummy data.")
            return {"title": "Error Generating Title", "pages": [{"text": "Error: Model not loaded.", "image_prompt": "Error icon"}]}

        theme = params.get("theme", "General Islamic Values")
        age_group = params.get("ageGroup", "6-8")
        humor = params.get("humor", 5)
        
        # Truncate source text to avoid context window issues (approx 2000 chars)
        truncated_source = source_text[:2000] + "..." if len(source_text) > 2000 else source_text

        prompt = f"""<|im_start|>system
You are a creative children's book author. You write engaging, fact-based stories for Muslim children based on provided source material.
Your goal is to adapt the source text into a short story suitable for {age_group} year olds.
The theme is: {theme}.
Humor level: {humor}/10.

Output Format:
1. First line: "Book Title: [Insert Creative Title Here]"
2. Then output the story as a list of 10 pages.
3. For each page, provide the 'Story Text' and a 'Illustration Description'.
4. Separate pages with '---PAGE BREAK---'.

Example:
Book Title: The Boy Who Spoke Truth
Page 1 Text: Once upon a time...
Page 1 Image: A bright sunny day in Medina...
---PAGE BREAK---
Page 2 Text: ...
<|im_end|>
<|im_start|>user
Source Material:
{truncated_source}

Write the story now.
<|im_end|>
<|im_start|>assistant
"""
        
        try:
            output = self.pipe(
                prompt,
                do_sample=True,
                temperature=0.7,
                top_p=0.95,
                repetition_penalty=1.15
            )[0]['generated_text']
            
            # DEBUG: Print raw output
            print("RAW LLM OUTPUT:")
            print(output)
            print("-----------------")

            # Extract the assistant's response
            response = output.split("<|im_start|>assistant")[-1].strip()
            
            # Parse Title
            title = "My Islamic Children's Book" # Default
            lines = response.split('\n')
            if lines and "Book Title:" in lines[0]:
                title = lines[0].split("Book Title:", 1)[1].strip()
                # Remove title line from response for page parsing
                response = "\n".join(lines[1:]).strip()
            
            pages = []
            raw_pages = response.split("---PAGE BREAK---")
            
            for i, raw_page in enumerate(raw_pages):
                if not raw_page.strip():
                    continue
                    
                # Robust parsing logic
                lines = raw_page.strip().split('\n')
                text = ""
                image_prompt = ""
                
                current_section = None # 'text' or 'image'
                
                for line in lines:
                    clean_line = line.strip()
                    if not clean_line:
                        continue
                        
                    if "Text:" in clean_line:
                        current_section = 'text'
                        text += clean_line.split("Text:", 1)[1].strip() + " "
                    elif "Image:" in clean_line:
                        current_section = 'image'
                        image_prompt += clean_line.split("Image:", 1)[1].strip() + " "
                    elif "Description:" in clean_line:
                        current_section = 'image'
                        image_prompt += clean_line.split("Description:", 1)[1].strip() + " "
                    else:
                        # Append to current section if it's a continuation
                        if current_section == 'text':
                            text += clean_line + " "
                        elif current_section == 'image':
                            image_prompt += clean_line + " "
                        else:
                            # If no section defined yet, assume it's text
                            current_section = 'text'
                            text += clean_line + " "
                
                # Fallback if parsing failed but content exists
                if not text.strip() and len(lines) > 0:
                    text = raw_page.strip()
                if not image_prompt.strip():
                    image_prompt = f"Illustration for page {i+1} about {theme}"
                
                pages.append({"text": text.strip(), "image_prompt": image_prompt.strip()})
            
            # Ensure we have at least one page
            if not pages or (len(pages) == 1 and len(pages[0]['text']) > 500):
                print("Parsing failed or single long page detected. Using Smart Splitter.")
                
                # Use the raw response (or the single page text)
                full_text = response
                if pages:
                    full_text = pages[0]['text']
                
                # Split into sentences (simple heuristic)
                import re
                sentences = re.split(r'(?<=[.!?]) +', full_text)
                
                # Group sentences into pages (e.g., 3 sentences per page)
                sentences_per_page = 3
                chunks = [sentences[i:i + sentences_per_page] for i in range(0, len(sentences), sentences_per_page)]
                
                pages = []
                for i, chunk in enumerate(chunks):
                    page_text = " ".join(chunk).strip()
                    if not page_text: continue
                    
                    # Generate a generic image prompt based on the chunk
                    # Ideally we'd ask the LLM, but for speed/fallback we use the text + theme
                    image_prompt = f"Illustration for: {page_text[:50]}..., theme: {theme}"
                    
                    pages.append({"text": page_text, "image_prompt": image_prompt})
                
                # Ensure we have at least 10 pages if possible, or just use what we have
                # If we have too many, truncate. If too few, that's okay for fallback.
            
            return {"title": title, "pages": pages[:10]}

        except Exception as e:
            print(f"Error generating story: {e}")
            return {"title": "Error", "pages": [{"text": "Sorry, I couldn't generate a story at this time.", "image_prompt": "Sad robot"}]}
