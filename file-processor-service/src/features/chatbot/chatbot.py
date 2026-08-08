from typing import cast

from fastapi import APIRouter
from pydantic import BaseModel

from shared.ai_manager import AiMessage, ai_factory

chatbot = APIRouter()

_SYSTEM_PROMPT = (
    "You are a very helpful assistant! "
    "You always answer shortly and clearly"
)


class ChatbotRequest(BaseModel):
    conversation: list[dict[str, str]]


@chatbot.post("/chat")
def chat(req_data: ChatbotRequest) -> dict[str, str]:
    ai = ai_factory.get_ai()
    answer = ai.get_ai_res_hist(
        system_prompt=_SYSTEM_PROMPT,
        history=cast("list[AiMessage]", req_data.conversation),
    )

    return {"answer": answer}
