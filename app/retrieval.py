from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import httpx

from app.config import Settings

CHUNK_SIZE = 1400
CHUNK_OVERLAP = 200
TEXT_EXTENSIONS = {".rst", ".md", ".txt", ".py", ".c", ".h", ".json", ".csv", ".yaml", ".yml"}
RST_ADORNMENTS = set("=-~^\"'`:+*#<>_")


@dataclass(frozen=True)
class SourceChunk:
    source: str
    page: int
    heading: str
    chunk_index: int
    content: str


def _sections(text: str) -> list[tuple[str, str]]:
    lines = text.splitlines()
    sections: list[tuple[str, list[str]]] = [("", [])]
    for index, line in enumerate(lines):
        heading = line.strip()
        if index + 1 < len(lines):
            underline = lines[index + 1].strip()
            if heading and len(underline) >= 3 and set(underline) <= RST_ADORNMENTS:
                sections.append((heading, []))
                continue
        markdown_heading = re.match(r"^#{1,6}\s+(.+?)\s*#*$", line)
        if markdown_heading:
            sections.append((markdown_heading.group(1), []))
            continue
        sections[-1][1].append(line)

    return [(heading, "\n".join(body).strip()) for heading, body in sections if "\n".join(body).strip()]


def parse_source(source: str, text: str) -> list[SourceChunk]:
    chunks: list[SourceChunk] = []
    for page, (heading, body) in enumerate(_sections(text), start=1):
        page_text = f"{heading}\n\n{body}" if heading else body
        start = 0
        chunk_index = 0
        while start < len(page_text):
            end = min(start + CHUNK_SIZE, len(page_text))
            content = page_text[start:end].strip()
            if content:
                chunks.append(SourceChunk(source, page, heading, chunk_index, content))
                chunk_index += 1
            if end == len(page_text):
                break
            start = end - CHUNK_OVERLAP
    return chunks


def iter_source_chunks(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            yield from parse_source(path.relative_to(root).as_posix(), text)


async def embed_texts(
    settings: Settings,
    texts: list[str],
    *,
    task_type: str = "RETRIEVAL_QUERY",
) -> list[list[float]]:
    api_key = settings.embedding_api_key or settings.primary_api_key
    base_url = settings.embedding_base_url or settings.primary_base_url
    if not api_key:
        raise RuntimeError("Set EMBEDDING_API_KEY or PRIMARY_API_KEY to create embeddings.")

    parsed_url = urlsplit(base_url)
    is_gemini = parsed_url.hostname == "generativelanguage.googleapis.com"
    if is_gemini:
        api_path = parsed_url.path.rstrip("/")
        if api_path.endswith("/openai"):
            api_path = api_path.removesuffix("/openai")
        api_root = urlunsplit((parsed_url.scheme, parsed_url.netloc, api_path, "", ""))
        model = settings.embedding_model
        if model == "text-embedding-3-small":
            model = "gemini-embedding-001"
        model = model.removeprefix("models/")
        url = f"{api_root}/models/{model}:batchEmbedContents"
        headers = {"x-goog-api-key": api_key}
        payload = {
            "requests": [
                {
                    "model": f"models/{model}",
                    "content": {"parts": [{"text": text}]},
                    "taskType": task_type,
                    "outputDimensionality": settings.embedding_dimensions,
                }
                for text in texts
            ]
        }
    else:
        url = f"{base_url.rstrip('/')}/embeddings"
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {"model": settings.embedding_model, "input": texts}

    for attempt in range(settings.embedding_max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=settings.timeout_seconds) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
            break
        except httpx.HTTPStatusError as error:
            retryable = error.response.status_code == 429 or error.response.status_code >= 500
            if not retryable or attempt == settings.embedding_max_retries:
                raise
            retry_after = error.response.headers.get("retry-after")
        except httpx.TransportError:
            if attempt == settings.embedding_max_retries:
                raise
            retry_after = None

        try:
            delay = float(retry_after) if retry_after is not None else 0
        except ValueError:
            delay = 0
        delay = max(delay, settings.embedding_retry_delay_seconds * (2**attempt))
        await asyncio.sleep(min(delay, 60))

    data = response.json()
    if is_gemini:
        vectors = [row["values"] for row in data.get("embeddings", [])]
    else:
        rows = data.get("data", [])
        vectors = [row["embedding"] for row in sorted(rows, key=lambda row: row["index"])]
    if len(vectors) != len(texts) or any(len(vector) != settings.embedding_dimensions for vector in vectors):
        raise ValueError("Embedding response count or dimensions do not match configuration.")
    return vectors


def store_chunks(settings: Settings, chunks: list[SourceChunk], vectors: list[list[float]]) -> None:
    import psycopg
    from pgvector.psycopg import register_vector

    with psycopg.connect(settings.database_url) as connection:
        connection.execute("CREATE EXTENSION IF NOT EXISTS vector")
        connection.commit()
        register_vector(connection)
        with connection.cursor() as cursor:
            cursor.execute(
                f"""CREATE TABLE IF NOT EXISTS document_chunks (
                    id BIGSERIAL PRIMARY KEY,
                    source TEXT NOT NULL,
                    page INTEGER NOT NULL,
                    heading TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    embedding VECTOR({settings.embedding_dimensions}) NOT NULL,
                    UNIQUE (source, page, chunk_index)
                )"""
            )
            cursor.executemany(
                """INSERT INTO document_chunks (source, page, heading, chunk_index, content, embedding)
                   VALUES (%s, %s, %s, %s, %s, %s)
                   ON CONFLICT (source, page, chunk_index) DO UPDATE SET
                       heading = EXCLUDED.heading, content = EXCLUDED.content,
                       embedding = EXCLUDED.embedding""",
                [
                    (chunk.source, chunk.page, chunk.heading, chunk.chunk_index, chunk.content, vector)
                    for chunk, vector in zip(chunks, vectors, strict=True)
                ],
            )


def search_chunks(settings: Settings, vector: list[float], limit: int = 5) -> list[dict[str, Any]]:
    import psycopg
    from pgvector.psycopg import register_vector

    with psycopg.connect(settings.database_url) as connection:
        register_vector(connection)
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT source, page, heading, content
                   FROM document_chunks
                   ORDER BY embedding <=> %s
                   LIMIT %s""",
                (vector, limit),
            )
            return [
                {"source": source, "page": page, "heading": heading, "content": content}
                for source, page, heading, content in cursor.fetchall()
            ]


async def retrieve_chunks(settings: Settings, question: str, limit: int = 5) -> list[dict[str, Any]]:
    try:
        vectors = await embed_texts(settings, [question], task_type="RETRIEVAL_QUERY")
    except (httpx.HTTPError, ValueError) as error:
        raise RuntimeError("Embedding request failed; verify the embedding endpoint and model.") from error
    try:
        return search_chunks(settings, vectors[0], limit)
    except Exception as error:
        raise RuntimeError("Vector search failed; verify PostgreSQL and the pgvector index.") from error