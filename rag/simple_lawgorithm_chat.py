#!/usr/bin/env python3
"""
Simple Lawgorithm Chat
======================

Direct conversation with the lawgorithm:latest Ollama model.
No RAG, no complex system - just pure chat.
"""

import requests
import json

class SimpleLawgorithmChat:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.model_name = "lawgorithm:latest"
        self.legal_mode = False
        
    def chat(self, message):
        """Send a message to lawgorithm and get response"""
        try:
            # Add legal language instructions if in legal mode
            if self.legal_mode:
                enhanced_message = f"""
You are an experienced lawyer responding to a legal query. Use proper legal language, court-appropriate jargon, and formal legal terminology in your response.

QUERY: {message}

Respond as a lawyer would in a professional legal context, using formal legal language and appropriate legal terminology.
"""
            else:
                enhanced_message = message
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": enhanced_message,
                    "stream": False,
                    "options": {
                        "temperature": 0.9,
                        "top_p": 0.95,
                        "top_k": 50,
                        "max_tokens": 1500,
                        "repeat_penalty": 1.1
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'No response generated')
            else:
                return f"Error: {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def start_chat(self):
        """Start the chat interface"""
        print("🤖 Lawgorithm Chat - Natural Legal Assistant")
        print("=" * 50)
        print("💬 Direct conversation with lawgorithm:latest")
        print("💡 Ask legal questions, write petitions, or just chat!")
        print("📝 Type 'quit' to exit")
        print("🔧 Type 'legal_mode' to toggle legal language mode")
        print("=" * 50)
        print()
        
        while True:
            try:
                user_input = input("👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() == 'legal_mode':
                    self.legal_mode = not self.legal_mode
                    mode_status = "ON" if self.legal_mode else "OFF"
                    print(f"🔧 Legal language mode: {mode_status}")
                    continue
                
                if not user_input:
                    continue
                
                print("🤔 Lawgorithm is thinking...")
                response = self.chat(user_input)
                print(f"\n🤖 Lawgorithm: {response}\n")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    chat = SimpleLawgorithmChat()
    chat.start_chat()

if __name__ == "__main__":
    main() 