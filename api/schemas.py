from ninja import ModelSchema
from .models import Message

class MessageSchema(ModelSchema):
    class Config:
        model = Message
        model_fields = ['id', 'description']