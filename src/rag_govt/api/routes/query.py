"""POST /query — answer a question over the ingested scheme documents."""
import asyncio
import json
import queue
import threading
from functools import partial

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from rag_govt.api.main import get_generator, get_retriever
from rag_govt.generation.generator import Generator
from rag_govt.retrieval.retriever import Retriever

router = APIRouter()

_STREAM_TIMEOUT = 30  # seconds before we give up waiting for a token


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5


class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]


@router.post("/", response_model=QueryResponse)
async def query_schemes(
    req: QueryRequest,
    retriever: Retriever = Depends(get_retriever),
    generator: Generator = Depends(get_generator),
) -> QueryResponse:
    loop = asyncio.get_running_loop()
    chunks = await loop.run_in_executor(
        None, partial(retriever.retrieve, req.question, top_k=req.top_k)
    )
    answer = await loop.run_in_executor(
        None, partial(generator.generate, req.question, chunks)
    )
    return QueryResponse(answer=answer, sources=chunks)


@router.post("/stream/")
async def query_stream(
    req: QueryRequest,
    retriever: Retriever = Depends(get_retriever),
    generator: Generator = Depends(get_generator),
) -> StreamingResponse:
    loop = asyncio.get_running_loop()
    chunks = await loop.run_in_executor(
        None, partial(retriever.retrieve, req.question, top_k=req.top_k)
    )

    # Sentinel objects placed on the queue to signal done / error.
    _DONE = object()
    _TIMEOUT = object()

    token_queue: queue.Queue = queue.Queue()

    def produce():
        try:
            for token in generator.generate_stream(req.question, chunks):
                token_queue.put(token)
            token_queue.put(_DONE)
        except Exception as exc:
            token_queue.put(("__error__", str(exc)))

    threading.Thread(target=produce, daemon=True).start()

    async def event_stream():
        yield f"data: {json.dumps({'type': 'sources', 'data': chunks})}\n\n"
        while True:
            try:
                item = await asyncio.wait_for(
                    loop.run_in_executor(None, token_queue.get),
                    timeout=_STREAM_TIMEOUT,
                )
            except asyncio.TimeoutError:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Response timed out — try again'})}\n\n"
                yield "data: [DONE]\n\n"
                break

            if item is _DONE:
                yield "data: [DONE]\n\n"
                break
            if isinstance(item, tuple) and item[0] == "__error__":
                yield f"data: {json.dumps({'type': 'error', 'message': item[1]})}\n\n"
                yield "data: [DONE]\n\n"
                break
            # Normal token string
            yield f"data: {json.dumps({'type': 'token', 'text': item})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
