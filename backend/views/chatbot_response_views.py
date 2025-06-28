from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import datetime
import uuid
import asyncio
from comprehensive_gemini_rag_chatbot import ComprehensiveGeminiRAGChatbot

router = APIRouter()

class MessageRequest(BaseModel):
    message: str
    session_id: str
    conversation_id: str

class MessageResponse(BaseModel):
    message_id: str
    user_message: str
    assistant_response: str
    timestamp: str
    session_id: str
    conversation_id: str

# Initialize chatbot once for all requests
chatbot = ComprehensiveGeminiRAGChatbot()
chatbot_initialized = False

async def ensure_chatbot_initialized():
    global chatbot_initialized
    if not chatbot_initialized:
        await chatbot.initialize()
        chatbot_initialized = True

@router.post("/message", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    await ensure_chatbot_initialized()
    user_message = request.message
    # Generate response using the real chatbot
    response = await chatbot.chat(user_message)
    # Example improvement check (as in test_natural_language.py)
    checks = {
        "Natural language (uses pronouns)": any(word in response.lower() for word in ["she", "her", "herself"]),
        "Varied sentence structure": response.count("that the petitioner") < 3,
        "NO verification section": "verification" not in response.lower(),
        "NO duplicates": response.count("arguments:") <= 1,
        "List of Documents included": "list of documents" in response.lower(),
        "Salutations after prayer": "and for this act of kindness" in response.lower(),
        "Arguments A-E present": all(letter in response.lower() for letter in ["a.", "b.", "c.", "d.", "e."])
    }
    improvement_summary = "\n".join([f"{k}: {'✅' if v else '❌'}" for k, v in checks.items()])
    response += f"\n\nImprovement checks:\n{improvement_summary}"
    return MessageResponse(
        message_id=str(uuid.uuid4()),
        user_message=user_message,
        assistant_response=response,
        timestamp=datetime.datetime.now().isoformat(),
        session_id=request.session_id,
        conversation_id=request.conversation_id
    ) 