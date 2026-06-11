"""Split page text into overlapping chunks with metadata."""
from dataclasses import dataclass

MIN_WORDS = 20


@dataclass
class Chunk:
    text: str
    source: str
    page: int
    chunk_index: int


def chunk_pages(pages: list[dict], chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    """Split each page's text into fixed-size overlapping chunks.

    chunk_size and chunk_overlap are in words (whitespace-split).
    """
    chunks: list[Chunk] = []
    for page in pages:
        words = page["text"].split()
        source, page_num = page["source"], page["page"]
        start = 0
        chunk_index = 0
        while start < len(words):
            window = words[start : start + chunk_size]
            if len(window) >= MIN_WORDS:
                chunks.append(
                    Chunk(
                        text=" ".join(window),
                        source=source,
                        page=page_num,
                        chunk_index=chunk_index,
                    )
                )
                chunk_index += 1
            start += chunk_size - chunk_overlap
    return chunks
