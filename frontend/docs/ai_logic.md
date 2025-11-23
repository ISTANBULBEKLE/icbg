# AI Logic & Models

## Philosophy
The system is designed to run **locally** on consumer hardware (e.g., MacBook M1/M2/M3). To achieve this, we prioritize **efficiency** and **speed** over massive parameter counts.

## 1. Text Generation (The Storyteller)

### Model: `HuggingFaceTB/SmolLM-1.7B-Instruct`
-   **Type**: Small Language Model (SLM)
-   **Size**: 1.7 Billion Parameters
-   **Format**: PyTorch (`float32` on MPS for stability)
-   **Why this model?**
    -   It fits easily into RAM (requires ~3-4GB).
    -   It is instruction-tuned, meaning it follows prompts like "Write a story..." well.
    -   It is significantly faster than 7B+ models (Llama 3, Mistral) while still being capable of simple creative writing.

### Prompt Engineering
We use a structured prompt to guide the model:
```text
System: You are a creative children's book author...
Goal: Adapt source text for {age_group}...
Format: Output 10 pages with 'Text:' and 'Image:'...
User: Source Material: {extracted_text}
```
This ensures the model doesn't just summarize but actually *adapts* the content into a narrative format. We request **10 pages** to create a substantial book.

## 2. Image Generation (The Illustrator)

### Model: `stabilityai/sd-turbo`
-   **Type**: Latent Diffusion Model
-   **Architecture**: Adversarial Diffusion Distillation (ADD)
-   **Why this model?**
    -   **Speed**: It generates high-quality images in **1 single step**. Standard Stable Diffusion takes 20-50 steps.
    -   **Efficiency**: Reduces generation time from ~10-20 seconds per image to <1 second on Apple Silicon.

### Style Consistency
To ensure the images look like a book and not photorealistic noise, we append style modifiers to every prompt:
> "... children's book illustration, {theme}, warm colors, soft lighting, high quality"

## 3. Data Ingestion (The Reader)

### Logic
-   We do not simply dump the whole PDF into the LLM (context window limits).
-   We allow the user to specify a **Page Range** and **Section Description**.
-   The ingestion service extracts text *only* from those pages.
-   It prepends the "Focus Section" metadata so the LLM knows what to prioritize in the story.
