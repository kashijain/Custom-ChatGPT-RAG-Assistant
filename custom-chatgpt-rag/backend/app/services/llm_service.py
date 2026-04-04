import httpx
from fastapi import HTTPException, status


class LLMService:
    def __init__(
        self,
        api_base_url: str,
        api_key: str,
        model: str,
        temperature: float = 0.2,
    ) -> None:
        self.api_base_url = api_base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.temperature = temperature

    async def generate_answer(self, question: str, context: str) -> str:
        if not self.api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="API_KEY is not configured for answer generation.",
            )

        system_prompt = (
            "You are a retrieval-augmented assistant. Answer using only the supplied "
            "document context. If the answer is not present in the context, say that "
            "the uploaded document does not contain enough information."
        )
        user_prompt = (
            f"Document context:\n{context}\n\n"
            f"User question:\n{question}\n\n"
            "Provide a concise, grounded answer and avoid unsupported claims."
        )

        payload = {
            "model": self.model,
            "temperature": self.temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{self.api_base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"LLM API request failed: {exc.response.text}",
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"LLM API request failed: {str(exc)}",
            ) from exc

        choices = response.json().get("choices", [])
        if not choices:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="LLM API returned no completion choices.",
            )

        return choices[0]["message"]["content"].strip()
