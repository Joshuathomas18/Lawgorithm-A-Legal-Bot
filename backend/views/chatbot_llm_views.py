import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))  # Add project root to path

from fastapi import APIRouter
from pydantic import BaseModel
import datetime
import uuid
from comprehensive_gemini_rag_chatbot import ComprehensiveGeminiRAGChatbot

router = APIRouter()

class ChatbotMessageRequest(BaseModel):
    message: str
    session_id: str
    conversation_id: str

class ChatbotMessageResponse(BaseModel):
    message_id: str
    user_message: str
    assistant_response: str
    timestamp: str
    session_id: str
    conversation_id: str

chatbot = ComprehensiveGeminiRAGChatbot()
chatbot_initialized = False

async def ensure_chatbot_initialized():
    global chatbot_initialized
    if not chatbot_initialized:
        await chatbot.initialize()
        chatbot_initialized = True

@router.post("/message", response_model=ChatbotMessageResponse)
async def chatbot_message(request: ChatbotMessageRequest):
    await ensure_chatbot_initialized()
    user_message = request.message
    response = await chatbot.chat(user_message)
    return ChatbotMessageResponse(
        message_id=str(uuid.uuid4()),
        user_message=user_message,
        assistant_response=response,
        timestamp=datetime.datetime.now().isoformat(),
        session_id=request.session_id,
        conversation_id=request.conversation_id
    ) 