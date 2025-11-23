from diffusers import AutoPipelineForText2Image
import torch
import os
import uuid

class ImageEngine:
    def __init__(self):
        print("Loading Image Generation model...")
        self.model_id = "stabilityai/sd-turbo"
        
        # Determine device
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        try:
            self.pipe = AutoPipelineForText2Image.from_pretrained(
                self.model_id, 
                torch_dtype=torch.float16 if self.device == "mps" else torch.float32, 
                variant="fp16" if self.device == "mps" else None
            )
            self.pipe.to(self.device)
            print("Image Gen model loaded successfully.")
        except Exception as e:
            print(f"Failed to load Image Gen model: {e}")
            self.pipe = None
            
        self.output_dir = "generated_images"
        os.makedirs(self.output_dir, exist_ok=True)

    async def generate_image(self, prompt: str) -> str:
        if not self.pipe:
            print("Image Gen model not loaded, skipping.")
            return ""

        try:
            # Generate image
            # SD-Turbo needs only 1-4 steps
            image = self.pipe(prompt=prompt, num_inference_steps=1, guidance_scale=0.0).images[0]
            
            # Save to file
            filename = f"{uuid.uuid4()}.png"
            filepath = os.path.join(self.output_dir, filename)
            image.save(filepath)
            
            return filepath
        except Exception as e:
            print(f"Error generating image: {e}")
            return ""
