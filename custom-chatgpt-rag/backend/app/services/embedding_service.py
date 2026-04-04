import httpx
from fastapi import HTTPException, status


class EmbeddingService:
    def __init__(self, api_base_url: str, api_key: str, model: str) -> None:
        self.api_base_url = api_base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if not self.api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="API_KEY is not configured for embedding generation.",
            )

        payload = {
            "model": self.model,
            "input": texts,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{self.api_base_url}/embeddings",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Embedding API request failed: {exc.response.text}",
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Embedding API request failed: {str(exc)}",
            ) from exc

        data = response.json().get("data", [])
        embeddings = [item["embedding"] for item in sorted(data, key=lambda item: item["index"])]

        if len(embeddings) != len(texts):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Embedding API returned an unexpected number of vectors.",
            )

        return embeddings
