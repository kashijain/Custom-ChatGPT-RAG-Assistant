import os
import hashlib
import logging
from openai import APIConnectionError, APIError, AuthenticationError, OpenAI, RateLimitError
from typing import List, Tuple

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
FALLBACK_EMBEDDING_DIM = int(os.getenv("FALLBACK_EMBEDDING_DIM", "1536"))
OPENAI_MODE = "openai"
FALLBACK_MODE = "fallback"


def get_openai_client() -> OpenAI | None:
    """
    Create the OpenAI client only when an API key exists.

    Returning None lets the app keep running in development and use a safe
    fallback embedding path instead of crashing during import/startup.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY is not set. Using fallback embeddings.")
        return None
    return OpenAI(api_key=api_key)


def _generate_fallback_embedding(text: str, dimension: int = FALLBACK_EMBEDDING_DIM) -> List[float]:
    """
    Generate a deterministic local embedding when no API key is available.

    This keeps upload/search flows working for local testing, but quality will
    be much lower than real API embeddings.
    """
    vector = [0.0] * dimension
    tokens = text.lower().split()

    if not tokens:
        return vector

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimension
        vector[index] += 1.0

    norm = sum(value * value for value in vector) ** 0.5
    if norm > 0:
        vector = [value / norm for value in vector]

    return vector


def _generate_fallback_embeddings(
    texts: List[str],
    fallback_dimension: int | None = None
) -> List[List[float]]:
    logger.info("Generating %d fallback embeddings in demo mode.", len(texts))
    dimension = fallback_dimension or FALLBACK_EMBEDDING_DIM
    return [_generate_fallback_embedding(text, dimension=dimension) for text in texts]


def _get_friendly_fallback_reason(error: Exception) -> str:
    """Translate OpenAI failures into short user-safe demo mode messages."""
    error_text = str(error).lower()
    status_code = getattr(error, "status_code", None)

    if isinstance(error, RateLimitError) or status_code == 429:
        if "insufficient_quota" in error_text:
            return "OpenAI quota is unavailable, so the app is running in demo mode."
        return "OpenAI rate limit was reached, so the app is running in demo mode."

    if isinstance(error, AuthenticationError) or status_code == 401:
        return "OpenAI authentication failed, so the app is running in demo mode."

    if isinstance(error, APIConnectionError):
        return "OpenAI is temporarily unreachable, so the app is running in demo mode."

    if isinstance(error, APIError):
        return "OpenAI embeddings are temporarily unavailable, so the app is running in demo mode."

    if "api_key" in error_text or "openai_api_key" in error_text:
        return "OpenAI API key is missing, so the app is running in demo mode."

    return "OpenAI embeddings are unavailable, so the app is running in demo mode."


def generate_embeddings_with_mode(
    texts: List[str],
    preferred_mode: str | None = None,
    fallback_dimension: int | None = None
) -> Tuple[List[List[float]], str, str | None]:
    """
    Generate embeddings and report which mode was used.

    preferred_mode="fallback" forces local embeddings so query vectors match
    documents that were indexed in demo mode.
    """
    if not texts:
        return [], preferred_mode or FALLBACK_MODE, None

    if preferred_mode == FALLBACK_MODE:
        return (
            _generate_fallback_embeddings(texts, fallback_dimension=fallback_dimension),
            FALLBACK_MODE,
            "Demo mode active: using fallback embeddings for this document.",
        )

    client = get_openai_client()
    if client is None:
        return (
            _generate_fallback_embeddings(texts, fallback_dimension=fallback_dimension),
            FALLBACK_MODE,
            "OpenAI API key is missing, so the app is running in demo mode.",
        )

    try:
        logger.info("Generating %d OpenAI embeddings with model %s.", len(texts), EMBEDDING_MODEL)
        response = client.embeddings.create(
            input=texts,
            model=EMBEDDING_MODEL,
        )
        return [data.embedding for data in response.data], OPENAI_MODE, None
    except (RateLimitError, APIConnectionError, AuthenticationError, APIError) as error:
        reason = _get_friendly_fallback_reason(error)
        logger.warning("OpenAI embedding failed, switching to fallback mode. Reason: %s", reason)
        return _generate_fallback_embeddings(texts, fallback_dimension=fallback_dimension), FALLBACK_MODE, reason
    except Exception as error:
        reason = _get_friendly_fallback_reason(error)
        logger.exception("Unexpected embedding failure, switching to fallback mode.")
        return _generate_fallback_embeddings(texts, fallback_dimension=fallback_dimension), FALLBACK_MODE, reason


def generate_embeddings(
    texts: List[str],
    preferred_mode: str | None = None,
    fallback_dimension: int | None = None
) -> List[List[float]]:
    """
    Generate embeddings for a list of texts.

    Uses OpenAI when OPENAI_API_KEY is configured, otherwise falls back to a
    deterministic local embedding function so the backend does not crash.
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        List of embedding vectors
    """
    embeddings, _, _ = generate_embeddings_with_mode(
        texts,
        preferred_mode=preferred_mode,
        fallback_dimension=fallback_dimension,
    )
    return embeddings
