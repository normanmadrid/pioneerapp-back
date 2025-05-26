from ninja import NinjaAPI, Schema
from typing import Dict, Any
from .models import Message
from .schemas import MessageSchema
from .services.groq_service import groq_call

api = NinjaAPI()

class PromptRequest(Schema):
    prompt: str

@api.get("/messages", response=list[MessageSchema])
def list_messages(request):
    return Message.objects.all()

@api.post("/search-restaurants")
def search_restaurants(request, payload: PromptRequest) -> Dict[str, Any]:
    return groq_call(payload.prompt)
