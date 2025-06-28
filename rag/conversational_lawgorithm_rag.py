import sys
import os
import json
import time
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lawgorithm_rag_interface import LawgorithmRAGInterface

class ConversationalLawgorithmRAG:
    def __init__(self):
        vector_store_path = os.path.join(os.path.dirname(__file__), "vector_store_lawgorithm", "vector_store.json")
        self.rag = LawgorithmRAGInterface(vector_store_path)
        self.conversation_history = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Test connection on startup
        self.test_ollama_connection()
        
    def test_ollama_connection(self):
        """Test if Ollama is running and lawgorithm model is available"""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                if "lawgorithm:latest" in model_names:
                    print("✅ Ollama connection successful - lawgorithm:latest is available")
                    return True
                else:
                    print(f"⚠️ lawgorithm:latest not found. Available models: {model_names}")
                    return False
            else:
                print("❌ Cannot connect to Ollama. Is it running?")
                return False
        except Exception as e:
            print(f"❌ Error testing Ollama connection: {e}")
            print("💡 Make sure Ollama is running: ollama serve")
            return False
        
    def add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_conversation_context(self, max_messages: int = 5) -> str:
        """Get recent conversation context for the LLM"""
        recent_messages = self.conversation_history[-max_messages:] if len(self.conversation_history) > max_messages else self.conversation_history
        
        context = "Previous conversation:\n"
        for msg in recent_messages:
            if msg['role'] != 'system':  # Skip system messages
                context += f"{msg['role'].title()}: {msg['content']}\n"
        
        return context
    
    def generate_conversational_response(self, user_message: str) -> str:
        """Generate a conversational response using RAG + LLM"""
        try:
            # Get relevant legal context from RAG
            print("🔍 Searching legal knowledge base...")
            rag_result = self.rag.query(user_message, top_k=2)
            
            # Extract legal context
            legal_context = ""
            if rag_result['context_sources']:
                # Combine context from multiple sources
                contexts = []
                for doc in rag_result['context_sources']:
                    contexts.append(doc['document'][:300])  # Limit each document
                legal_context = "\n\n".join(contexts)
            
            # Get conversation history (limit to last 3 messages)
            conversation_context = self.get_conversation_context(max_messages=3)
            
            # Create enhanced prompt with conversation context
            prompt = f"""You are Lawgorithm, a specialized legal AI assistant trained on Indian law and court cases.

RECENT CONVERSATION:
{conversation_context}

LEGAL CONTEXT AND PRECEDENTS:
{legal_context}

CURRENT QUESTION:
{user_message}

As Lawgorithm, provide a conversational but professional legal answer that:
1. Addresses the specific question asked
2. References relevant legal principles from the context when applicable
3. Maintains conversation flow
4. Uses clear, professional legal language
5. Is helpful and informative

ANSWER:"""

            print("🤖 Generating response with lawgorithm model...")
            
            # Use the RAG interface's generate_response method
            response = self.rag.generate_response(user_message, legal_context)
            
            if response and not response.startswith("Error:"):
                return response
            else:
                return "I apologize, but I'm having trouble connecting to my legal knowledge base right now. Please try again."
                
        except Exception as e:
            print(f"❌ Error in generate_conversational_response: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    def start_conversation(self):
        """Start the conversational interface"""
        print("🤖 Welcome to Lawgorithm RAG - Your Conversational Legal Assistant!")
        print("=" * 60)
        print("💬 I'm powered by:")
        print("   • Your lawgorithm LLM")
        print("   • 440+ legal Q&A pairs from Indian courts")
        print("   • Case law and precedents")
        print("   • Legal principles and procedures")
        print("\n💡 You can ask me about:")
        print("   • Legal advice and guidance")
        print("   • Case law and precedents")
        print("   • Petition drafting help")
        print("   • Court procedures")
        print("   • Legal research questions")
        print("   • General legal discussions")
        print("\n🔄 I remember our conversation context for better responses.")
        print("📝 Type 'save' to save our conversation, 'quit' to exit.")
        print("🔧 Type 'test' to test Ollama connection.\n")
        
        # Add system greeting
        self.add_to_history('system', 'Conversation started with Lawgorithm RAG assistant')
        
        while True:
            try:
                # Get user input
                user_input = input("👤 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("\n👋 Thank you for using Lawgorithm RAG! Goodbye!")
                    break
                
                elif user_input.lower() == 'save':
                    self.save_conversation()
                    continue
                
                elif user_input.lower() == 'history':
                    self.show_history()
                    continue
                
                elif user_input.lower() == 'clear':
                    self.conversation_history = []
                    print("🗑️ Conversation history cleared!")
                    continue
                
                elif user_input.lower() == 'test':
                    self.test_ollama_connection()
                    continue
                
                # Add user message to history
                self.add_to_history('user', user_input)
                
                # Generate response
                print("🤔 Thinking...")
                response = self.generate_conversational_response(user_input)
                
                # Add assistant response to history
                self.add_to_history('assistant', response)
                
                # Display response
                print(f"\n🤖 Assistant: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Conversation interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again.\n")
    
    def save_conversation(self):
        """Save the conversation to a file"""
        try:
            filename = f"conversation_{self.session_id}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'session_id': self.session_id,
                    'timestamp': datetime.now().isoformat(),
                    'conversation': self.conversation_history
                }, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Conversation saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving conversation: {e}")
    
    def show_history(self):
        """Show conversation history"""
        if not self.conversation_history:
            print("📝 No conversation history yet.")
            return
        
        print("\n📚 Conversation History:")
        print("-" * 40)
        for i, msg in enumerate(self.conversation_history, 1):
            if msg['role'] != 'system':
                role_emoji = "👤" if msg['role'] == 'user' else "🤖"
                print(f"{i}. {role_emoji} {msg['role'].title()}: {msg['content'][:100]}...")
        print("-" * 40)

def main():
    # Initialize conversational RAG
    conversational_rag = ConversationalLawgorithmRAG()
    
    # Start conversation
    conversational_rag.start_conversation()

if __name__ == "__main__":
    main() 