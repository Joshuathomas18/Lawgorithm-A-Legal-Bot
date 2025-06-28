#!/usr/bin/env python3
"""
Interactive RAG Bot for Petition Queries
Run this script to chat with your RAG-enhanced petition bot!
"""

import sys
import os
from inference.rag_petition_bot import RAGPetitionBot
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("🤖 Welcome to the Interactive RAG Petition Bot!")
    print("=" * 60)
    print("This bot uses your petition dataset to provide accurate legal information.")
    print("Type 'quit' or 'exit' to end the session.")
    print("=" * 60)
    
    # Initialize the RAG bot
    try:
        bot = RAGPetitionBot(
            api_key="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",
            model="google/gemini-pro-1.5"
        )
        print("✅ RAG Bot initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing bot: {e}")
        return
    
    print("\n💡 Example queries you can try:")
    print("• What is the title of petition 10112739?")
    print("• What court is petition 105925409 filed in?")
    print("• What is the content of petition 107187354?")
    print("• Tell me about land acquisition cases")
    print("• How to file a writ petition?")
    print("• Find cases about fundamental rights")
    print("-" * 60)
    
    # Interactive loop
    while True:
        try:
            # Get user input
            query = input("\n🤔 Your question: ").strip()
            
            # Check for exit commands
            if query.lower() in ['quit', 'exit', 'bye', 'q']:
                print("👋 Thanks for using the RAG Petition Bot! Goodbye!")
                break
            
            if not query:
                print("❌ Please enter a question!")
                continue
            
            print(f"\n🔍 Searching for: '{query}'")
            print("⏳ Generating response...")
            
            # Get response from RAG bot
            response = bot.generate_response(query)
            
            if 'error' in response:
                print(f"❌ Error: {response['error']}")
                continue
            
            # Display response
            print("\n" + "=" * 60)
            print("📋 RAG Bot Response:")
            print("=" * 60)
            print(response['response'])
            
            # Show context info
            if response.get('context_length', 0) > 0:
                print(f"\n📊 Context used: {response['context_length']} characters")
                print("💡 This response was enhanced with relevant petition data!")
            else:
                print("\n💡 This response was generated from general knowledge.")
            
            print("=" * 60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            continue

if __name__ == "__main__":
    main() 