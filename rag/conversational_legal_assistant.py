#!/usr/bin/env python3
"""
Conversational Legal Assistant
==============================

A continuous conversation interface for legal discussions using the RAG system.
"""

import json
import sys
import os
from datetime import datetime
from rag.lawgorithm_rag_interface import LawgorithmRAGInterface

class ConversationalLegalAssistant:
    def __init__(self):
        """Initialize the conversational assistant"""
        print("🤖 Initializing Lawgorithm RAG System...")
        
        try:
            self.rag = LawgorithmRAGInterface("rag/vector_store_lawgorithm/vector_store.json")
            print("✅ RAG system initialized successfully!")
        except Exception as e:
            print(f"❌ Error initializing RAG system: {e}")
            sys.exit(1)
        
        self.conversation_history = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def display_welcome(self):
        """Display welcome message"""
        print("\n" + "="*70)
        print("🏛️  WELCOME TO LAWGORITHM CONVERSATIONAL LEGAL ASSISTANT")
        print("="*70)
        print("💡 I'm your AI legal assistant, trained on Indian law and court cases.")
        print("📚 I can help you with:")
        print("   • Legal questions and advice")
        print("   • Case law research")
        print("   • Legal procedure guidance")
        print("   • Document analysis")
        print("   • Legal terminology explanations")
        print("\n💬 Just ask me anything legal! Type 'quit' to exit.")
        print("="*70)
    
    def save_conversation(self):
        """Save the conversation history"""
        try:
            filename = f"conversation_{self.session_id}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'session_id': self.session_id,
                    'created_at': datetime.now().isoformat(),
                    'conversation': self.conversation_history
                }, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 Conversation saved to: {filename}")
            
            # Also save as text
            text_filename = f"conversation_{self.session_id}.txt"
            with open(text_filename, 'w', encoding='utf-8') as f:
                f.write("LAWGORITHM CONVERSATION LOG\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Session: {self.session_id}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for i, exchange in enumerate(self.conversation_history, 1):
                    f.write(f"Exchange {i}:\n")
                    f.write(f"User: {exchange['user']}\n")
                    f.write(f"Assistant: {exchange['assistant']}\n")
                    f.write("-" * 40 + "\n\n")
            
            print(f"📄 Conversation also saved as text: {text_filename}")
            
        except Exception as e:
            print(f"❌ Error saving conversation: {e}")
    
    def process_command(self, user_input):
        """Process special commands"""
        if user_input.lower().startswith('save'):
            self.save_conversation()
            return True
        
        if user_input.lower().startswith('clear'):
            self.conversation_history = []
            print("🗑️ Conversation history cleared!")
            return True
        
        if user_input.lower().startswith('history'):
            if self.conversation_history:
                print("\n📜 CONVERSATION HISTORY:")
                print("-" * 40)
                for i, exchange in enumerate(self.conversation_history[-5:], 1):  # Show last 5
                    print(f"{i}. User: {exchange['user'][:50]}...")
                    print(f"   Assistant: {exchange['assistant'][:50]}...")
                    print()
            else:
                print("📜 No conversation history yet.")
            return True
        
        if user_input.lower().startswith('help'):
            print("\n🔧 AVAILABLE COMMANDS:")
            print("   • save - Save conversation to file")
            print("   • clear - Clear conversation history")
            print("   • history - Show recent conversation history")
            print("   • help - Show this help message")
            print("   • quit/exit - Exit the program")
            return True
        
        return False
    
    def start_conversation(self):
        """Start the conversational interface"""
        self.display_welcome()
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thank you for using Lawgorithm! Goodbye!")
                    if self.conversation_history:
                        save_choice = input("Would you like to save this conversation? (y/n): ").strip().lower()
                        if save_choice in ['y', 'yes']:
                            self.save_conversation()
                    break
                
                if not user_input:
                    continue
                
                # Check for special commands
                if self.process_command(user_input):
                    continue
                
                # Process legal question with RAG
                print("\n🤖 Lawgorithm: Thinking...")
                
                try:
                    rag_result = self.rag.query(user_input, top_k=3)
                    
                    if rag_result and 'response' in rag_result:
                        response = rag_result['response']
                        print(f"\n🤖 Lawgorithm: {response}")
                        
                        # Store in conversation history
                        self.conversation_history.append({
                            'user': user_input,
                            'assistant': response,
                            'timestamp': datetime.now().isoformat(),
                            'sources_used': rag_result.get('total_sources', 0)
                        })
                        
                    else:
                        error_msg = "I'm sorry, I couldn't generate a response for that question."
                        print(f"\n🤖 Lawgorithm: {error_msg}")
                        self.conversation_history.append({
                            'user': user_input,
                            'assistant': error_msg,
                            'timestamp': datetime.now().isoformat(),
                            'sources_used': 0
                        })
                        
                except Exception as e:
                    error_msg = f"I encountered an error: {e}. Please try rephrasing your question."
                    print(f"\n🤖 Lawgorithm: {error_msg}")
                    self.conversation_history.append({
                        'user': user_input,
                        'assistant': error_msg,
                        'timestamp': datetime.now().isoformat(),
                        'sources_used': 0
                    })
                
            except KeyboardInterrupt:
                print("\n\n👋 Conversation interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("Please try again.")

def main():
    """Main function"""
    assistant = ConversationalLegalAssistant()
    assistant.start_conversation()

if __name__ == "__main__":
    main() 