class ContentEngine:
    def __init__(self):
        # TODO: Initialize Local LLM (Ollama)
        pass

    async def generate_story(self, source_text: str, params: dict) -> list:
        # TODO: Implement story generation logic
        # Should return a list of pages (text + image prompt)
        return [{"text": "Page 1 text", "image_prompt": "Page 1 image prompt"}]
