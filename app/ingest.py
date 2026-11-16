import argparse
import asyncio
from pathlib import Path

from app.config import get_settings
from app.retrieval import embed_texts, iter_source_chunks, store_chunks

BATCH_SIZE = 32


async def ingest(root: Path) -> tuple[int, int]:
    settings = get_settings()
    chunks = list(iter_source_chunks(root))
    for offset in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[offset : offset + BATCH_SIZE]
        vectors = await embed_texts(
            settings,
            [chunk.content for chunk in batch],
            task_type="RETRIEVAL_DOCUMENT",
        )
        store_chunks(settings, batch, vectors)
        if (offset // BATCH_SIZE + 1) % 25 == 0:
            print(f"Indexed {min(offset + len(batch), len(chunks))}/{len(chunks)} chunks.", flush=True)
        if offset + BATCH_SIZE < len(chunks) and settings.embedding_request_delay_seconds:
            await asyncio.sleep(settings.embedding_request_delay_seconds)

    page_count = len({(chunk.source, chunk.page) for chunk in chunks})
    return page_count, len(chunks)


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse, embed, and index local source files.")
    parser.add_argument("root", nargs="?", type=Path, default=Path("data/raw"))
    args = parser.parse_args()
    pages, chunks = asyncio.run(ingest(args.root))
    print(f"Indexed {pages} source pages in {chunks} chunks.")


if __name__ == "__main__":
    main()