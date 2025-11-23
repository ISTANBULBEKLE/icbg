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
                max_new_tokens=1024,
            )
            print("LLM loaded successfully.")
        except Exception as e:
            print(f"Failed to load LLM: {e}")
            self.pipe = None

    async def generate_story(self, source_text: str, params: dict) -> list:
        if not self.pipe:
            print("LLM not loaded, returning dummy data.")
            return [{"text": "Error: Model not loaded.", "image_prompt": "Error icon"}]

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
You must output the story as a list of 5 pages.
For each page, provide the 'Story Text' and a 'Illustration Description'.
Separate pages with '---PAGE BREAK---'.

Example:
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
            # Extract the assistant's response
            response = output.split("<|im_start|>assistant")[-1].strip()
            
            pages = []
            raw_pages = response.split("---PAGE BREAK---")
            
            for i, raw_page in enumerate(raw_pages):
                if not raw_page.strip():
                    continue
                    
                # Simple parsing logic
                lines = raw_page.strip().split('\n')
                text = ""
                image_prompt = ""
                
                for line in lines:
                    if "Text:" in line:
                        text = line.split("Text:", 1)[1].strip()
                    elif "Image:" in line:
                        image_prompt = line.split("Image:", 1)[1].strip()
                    elif "Description:" in line: # Handle variation
                         image_prompt = line.split("Description:", 1)[1].strip()
                
                # Fallback if parsing failed but content exists
                if not text and len(lines) > 0:
                    text = lines[0]
                if not image_prompt:
                    image_prompt = f"Illustration for page {i+1} about {theme}"
                
                pages.append({"text": text, "image_prompt": image_prompt})
            
            # Ensure we have at least one page
            if not pages:
                pages.append({"text": response, "image_prompt": f"Scene about {theme}"})
                
            return pages[:10] # Limit to 10 pages max

        except Exception as e:
            print(f"Error generating story: {e}")
            return [{"text": "Sorry, I couldn't generate a story at this time.", "image_prompt": "Sad robot"}]
