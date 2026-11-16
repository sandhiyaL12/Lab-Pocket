import asyncio

from app.config import Settings
from app.retrieval import CHUNK_OVERLAP, embed_texts, parse_source


def test_parse_source_preserves_section_pages_and_headings():
    chunks = parse_source(
        "library/machine.Pin.rst",
        "Pin\n===\n\nPin objects control I/O pins.\n\nMethods\n-------\n\nUse value() to read a pin.",
    )

    assert [(chunk.page, chunk.heading) for chunk in chunks] == [(1, "Pin"), (2, "Methods")]
    assert "Pin objects control I/O pins." in chunks[0].content
    assert chunks[1].source == "library/machine.Pin.rst"


def test_parse_source_splits_long_sections_with_overlap():
    chunks = parse_source("guide.txt", "x" * 3000)

    assert len(chunks) == 3
    assert [chunk.chunk_index for chunk in chunks] == [0, 1, 2]
    assert chunks[0].content[-CHUNK_OVERLAP:] == chunks[1].content[:CHUNK_OVERLAP]


def test_gemini_embedding_uses_native_batch_api(monkeypatch):
    request_data = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"embeddings": [{"values": [0.1, 0.2, 0.3]}, {"values": [0.4, 0.5, 0.6]}]}

    class FakeClient:
        def __init__(self, **_kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            pass

        async def post(self, url, *, headers, json):
            request_data.update(url=url, headers=headers, json=json)
            return FakeResponse()

    monkeypatch.setattr("app.retrieval.httpx.AsyncClient", FakeClient)
    settings = Settings(
        primary_api_key="test-key",
        primary_base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        embedding_dimensions=3,
    )

    vectors = asyncio.run(embed_texts(settings, ["one", "two"], task_type="RETRIEVAL_DOCUMENT"))

    assert vectors == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    assert request_data["url"] == (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-embedding-001:batchEmbedContents"
    )
    assert request_data["headers"] == {"x-goog-api-key": "test-key"}
    assert request_data["json"]["requests"][0]["taskType"] == "RETRIEVAL_DOCUMENT"
    assert request_data["json"]["requests"][0]["outputDimensionality"] == 3