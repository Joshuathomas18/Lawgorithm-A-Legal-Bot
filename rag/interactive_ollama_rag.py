#!/usr/bin/env python3
"""
Interactive Ollama RAG Bot for Petition Queries
Run this script to chat with your RAG-enhanced petition bot using Ollama with Lawgorithm!
"""

import sys
import os
from inference.ollama_rag_bot import OllamaRAGBot
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("🤖 Welcome to the Interactive Ollama RAG Petition Bot!")
    print("=" * 60)
    print("This bot uses Ollama with Lawgorithm law model + your petition dataset.")
    print("Type 'quit' or 'exit' to end the session.")
    print("Type 'models' to see available Ollama models.")
    print("Type 'change <model_name>' to switch models.")
    print("Type 'pull lawgorithm' to download the Lawgorithm model.")
    print("=" * 60)
    
    # Initialize the RAG bot with Lawgorithm model
    model_name = "lawgorithm"  # Default to Lawgorithm law model
    
    try:
        bot = OllamaRAGBot(model_name=model_name)
        print(f"✅ Ollama RAG Bot initialized with model: {model_name}")
        
        # Show available models
        print("\n📋 Available Ollama models:")
        models_output = bot.list_available_models()
        print(models_output)
        
        # Check if Lawgorithm is available
        if "lawgorithm" not in models_output.lower():
            print("\n⚠️  Lawgorithm model not found. You can pull it with: 'pull lawgorithm'")
        
    except Exception as e:
        print(f"❌ Error initializing bot: {e}")
        return
    
    print("\n💡 Example legal queries you can try:")
    print("• What is the title of petition 10112739?")
    print("• What court is petition 105925409 filed in?")
    print("• What is the content of petition 107187354?")
    print("• Tell me about land acquisition cases")
    print("• How to file a writ petition?")
    print("• Find cases about fundamental rights")
    print("• I need help with a dowry case")
    print("• What are the legal requirements for filing a PIL?")
    print("• Explain the procedure for filing a criminal complaint")
    print("-" * 60)
    
    # Interactive loop
    while True:
        try:
            # Get user input
            query = input(f"\n🤔 Your legal question (using {model_name}): ").strip()
            
            # Check for exit commands
            if query.lower() in ['quit', 'exit', 'bye', 'q']:
                print("👋 Thanks for using the Ollama RAG Petition Bot! Goodbye!")
                break
            
            if not query:
                print("❌ Please enter a question!")
                continue
            
            # Check for model commands
            if query.lower() == 'models':
                print("\n📋 Available Ollama models:")
                print(bot.list_available_models())
                continue
            
            if query.lower() == 'pull lawgorithm':
                print("\n📥 Pulling Lawgorithm model...")
                success = bot.pull_lawgorithm()
                if success:
                    print("✅ Lawgorithm model is now available!")
                continue
            
            if query.lower().startswith('change '):
                new_model = query[7:].strip()
                try:
                    bot = OllamaRAGBot(model_name=new_model)
                    model_name = new_model
                    print(f"✅ Switched to model: {model_name}")
                except Exception as e:
                    print(f"❌ Error switching to model {new_model}: {e}")
                continue
            
            print(f"\n🔍 Searching for: '{query}'")
            print("⏳ Generating legal response with Lawgorithm...")
            
            # Get response from RAG bot
            response = bot.generate_response(query)
            
            if 'error' in response:
                print(f"❌ Error: {response['error']}")
                if "lawgorithm" in response['error'].lower():
                    print("💡 Try running 'pull lawgorithm' to download the model first.")
                continue
            
            # Display response
            print("\n" + "=" * 60)
            print("📋 Lawgorithm RAG Bot Response:")
            print("=" * 60)
            print(response['response'])
            
            # Show context info
            if response.get('context_length', 0) > 0:
                print(f"\n📊 Context used: {response['context_length']} characters")
                print("💡 This response was enhanced with relevant petition data!")
            else:
                print("\n💡 This response was generated from Lawgorithm's legal knowledge.")
            
            print(f"🤖 Model used: {response.get('model_used', model_name)}")
            print("=" * 60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            continue

if __name__ == "__main__":
    main() 