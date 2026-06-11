"""Generate answers from retrieved context using the Google Gemini API."""
from __future__ import annotations

SYSTEM_PROMPT = (
    "You are an expert on Indian government welfare schemes. "
    "Answer the user's question using only the provided context passages. "
    "If the answer is not in the context, say so clearly. "
    "Cite the source PDF and page number for every claim."
)


def build_context_block(chunks: list[dict]) -> str:
    parts = [
        f"[{i}] Source: {c['source']}, Page {c['page']}\n{c['text']}"
        for i, c in enumerate(chunks, 1)
    ]
    return "\n\n".join(parts)


def _safe_text(chunk) -> str:
    """Return chunk text or empty string — never raises."""
    try:
        return chunk.text or ""
    except Exception:
        return ""


class Generator:
    def __init__(self, api_key: str, model: str) -> None:
        self.model = model
        self._api_key = api_key
        self._client = None

    def _get_client(self):
        if self._client is None:
            from google import genai
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    def generate(self, query: str, chunks: list[dict]) -> str:
        from google.genai import types
        context = build_context_block(chunks)
        response = self._get_client().models.generate_content(
            model=self.model,
            contents=f"Context:\n{context}\n\nQuestion: {query}",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=4096,
            ),
        )
        return response.text

    def generate_stream(self, query: str, chunks: list[dict]):
        """Yield text tokens from the Gemini streaming API."""
        from google.genai import types
        context = build_context_block(chunks)
        token_count = 0
        finish_reason = None

        for chunk in self._get_client().models.generate_content_stream(
            model=self.model,
            contents=f"Context:\n{context}\n\nQuestion: {query}",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=4096,
            ),
        ):
            text = _safe_text(chunk)
            if text:
                token_count += 1
                yield text

            # Capture finish reason from the last candidate for error reporting
            try:
                if chunk.candidates:
                    finish_reason = str(chunk.candidates[0].finish_reason)
            except Exception:
                pass

        if token_count == 0:
            reason_msg = ""
            if finish_reason and "SAFETY" in finish_reason.upper():
                reason_msg = " (blocked by safety filter)"
            elif finish_reason and "RECITATION" in finish_reason.upper():
                reason_msg = " (recitation policy)"
            raise RuntimeError(
                f"Gemini returned no text{reason_msg} — try rephrasing your question."
            )
