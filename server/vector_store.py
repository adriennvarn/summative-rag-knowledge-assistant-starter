from typing import Any, List

import chromadb
import requests

from config import Config
from documents import DocumentChunk


def get_chroma_client():
    """
    Create and return a persistent Chroma client.

    TODO:
    - Use Config.CHROMA_PATH as the local storage path.
    - Return a chromadb.PersistentClient.
    """
    return chromadb.PersistentClient(path=Config.CHROMA_PATH)


def get_or_create_collection():
    """
    Get or create the Chroma collection for the knowledge assistant.

    TODO:
    - Use get_chroma_client().
    - Use Config.COLLECTION_NAME as the collection name.
    - Return the collection.
    """
    return get_chroma_client().get_or_create_collection(
        name=Config.COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )


def get_embedding(text: str) -> list[float]:
    """
    Create an embedding for a piece of text using the local model service.

    TODO:
    - Send a POST request to the Ollama embed endpoint (https://docs.ollama.com/api/embed).
    - Use Config.OLLAMA_BASE_URL.
    - Use Config.EMBEDDING_MODEL.
    - Return the embedding list from the response.

    Endpoint:
        POST {OLLAMA_BASE_URL}/api/embeddings

    Example request body:
        {
            "model": Config.EMBEDDING_MODEL,
            "prompt": text
        }
    """
    response = requests.post(f"{Config.OLLAMA_BASE_URL}/api/embeddings", {
        "model": Config.EMBEDDING_MODEL,
        "prompt": text
    })
    return response["embedding"]


def seed_vector_store(chunks: List[DocumentChunk]) -> int:
    """
    Add document chunks to the Chroma collection.

    TODO:
    - Get or create the collection.
    - Convert each chunk into:
        - id
        - document text
        - metadata with source, title, and chunk_index
        - embedding
    - Add or update the chunks in Chroma (recommend using collection.upsert(...) to prevent duplicating existing records).
    - Return the number of chunks added.

    Keep source metadata because the frontend needs to display sources.
    """
    collection = get_or_create_collection()
    ids = [document.id for document in chunks]
    documents = [
        f"{document.title}. {document.text}" for document in chunks
    ]
    metadatas = [
        {
            "title": document.title,
            "source": document.source,
            "chunk_index": document.chunk_index
        }
        for document in chunks
    ]
    embeddings = [get_embedding(document_text) for document_text in documents]
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )
    return collection.count()


def retrieve_relevant_chunks(
    question: str, top_k: int | None = None
) -> list[dict[str, Any]]:
    """
    Retrieve relevant chunks for a user question.

    TODO:
    - Create an embedding for the question.
    - Query the Chroma collection.
    - Return a list of dictionaries with:
        - text
        - source
        - title
        - chunk_index
        - optional distance or score

    The RAG workflow expects a list shaped like this:

        [
            {
                "text": "Relevant source text...",
                "source": "product_support.txt",
                "title": "Product Support Guide",
                "chunk_index": 0
            }
        ]
    """
    collection = get_or_create_collection()

    if collection.count() == 0:
        return []

    query_embedding = get_embedding(question)
    raw_results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    ids = raw_results.get("ids") or [[]]
    documents = raw_results.get("documents") or [[]]
    metadatas = raw_results.get("metadatas") or [[]]
    distances = raw_results.get("distances") or [[]]

    results = []

    for index, document_id in enumerate(ids[0]):
        metadata = metadatas[0][index] or {}
        distance = float(distances[0][index])
        score = 1 - distance
        results.append(
            {
                "id": document_id,
                "title": metadata.get("title", "Untitled source"),
                "source": metadata.get("source", "No source"),
                "text": documents[0][index],
                "chunk_index": metadata.get("chunk_index", "No chunk index"),
                "score": score,
            }
        )
    
    return results