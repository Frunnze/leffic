from typing import Final, cast

from fastapi import APIRouter, Depends, HTTPException, params, status
from openai import OpenAIError
from pydantic import BaseModel

from shared.ai_manager import AiMessage, ai_factory
from shared.claims_extractor import get_user_id_from_jwt

chatbot = APIRouter()

_IDENTIFIED_CALLER_ONLY: Final[list[params.Depends]] = [
    Depends(get_user_id_from_jwt),
]

_SYSTEM_PROMPT = (
    "You are a very helpful assistant! "
    "You always answer shortly and clearly"
)
_MODEL_UNAVAILABLE = "The assistant is unavailable right now. Try again."


class ChatbotRequest(BaseModel):
    conversation: list[dict[str, str]]


@chatbot.post("/chat", dependencies=_IDENTIFIED_CALLER_ONLY)
def chat(request_data: ChatbotRequest) -> dict[str, str]:
    ai = ai_factory.get_ai()

    try:
        answer = ai.get_ai_res_hist(
            system_prompt=_SYSTEM_PROMPT,
            history=cast("list[AiMessage]", request_data.conversation),
        )
    except OpenAIError as unavailable:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_MODEL_UNAVAILABLE,
        ) from unavailable

    return {"answer": answer}
