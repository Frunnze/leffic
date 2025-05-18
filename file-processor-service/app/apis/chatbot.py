from fastapi import APIRouter
from pydantic import BaseModel
from .. import ai_factory


chatbot = APIRouter()


class ChatbotRequest(BaseModel):
    conversation: list[dict]

@chatbot.post("/chat")
def chat(req_data: ChatbotRequest):
    ai = ai_factory.get_ai()
    ans = ai.get_ai_res_hist(
        system_prompt="You are a very helpful assistant! You always answer shortly and clearly",
        history=req_data.conversation
    )
    return {"answer": ans}