#!/usr/bin/env python3
"""
Ollama Connection Diagnostic Tool
================================

This script helps diagnose Ollama connection issues and verify the lawgorithm model.
"""

import requests
import json
import sys
import time

def test_ollama_server():
    """Test if Ollama server is running"""
    print("🔍 Testing Ollama server connection...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            print("✅ Ollama server is running!")
            return True
        else:
            print(f"❌ Ollama server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama server")
        print("💡 Make sure Ollama is running: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")
        return False

def test_lawgorithm_model():
    """Test if lawgorithm model is available"""
    print("\n🔍 Testing lawgorithm model availability...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            
            print(f"📋 Available models: {model_names}")
            
            if "lawgorithm:latest" in model_names:
                print("✅ lawgorithm:latest is available!")
                return True
            else:
                print("❌ lawgorithm:latest not found!")
                print("💡 You may need to pull the model: ollama pull lawgorithm:latest")
                return False
        else:
            print(f"❌ Failed to get model list: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing model availability: {e}")
        return False

def test_model_generation():
    """Test if lawgorithm model can generate responses"""
    print("\n🔍 Testing model generation...")
    try:
        test_prompt = "Hello, can you respond with a simple greeting?"
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "lawgorithm:latest",
                "prompt": test_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 100
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', '')
            print("✅ Model generation successful!")
            print(f"📝 Response: {generated_text[:100]}...")
            return True
        else:
            print(f"❌ Model generation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing model generation: {e}")
        return False

def test_embedding_generation():
    """Test if embedding generation works"""
    print("\n🔍 Testing embedding generation...")
    try:
        test_text = "This is a test for embedding generation"
        
        # Try nomic-embed-text first
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": test_text},
            timeout=30
        )
        
        if response.status_code == 200:
            embedding = response.json()['embedding']
            print(f"✅ nomic-embed-text embedding successful! Length: {len(embedding)}")
            return True
        else:
            print(f"⚠️ nomic-embed-text failed ({response.status_code}), trying lawgorithm...")
            
            # Try lawgorithm model
            response = requests.post(
                "http://localhost:11434/api/embeddings",
                json={"model": "lawgorithm:latest", "prompt": test_text},
                timeout=30
            )
            
            if response.status_code == 200:
                embedding = response.json()['embedding']
                print(f"✅ lawgorithm embedding successful! Length: {len(embedding)}")
                return True
            else:
                print(f"❌ Both embedding models failed")
                return False
                
    except Exception as e:
        print(f"❌ Error testing embedding generation: {e}")
        return False

def main():
    """Run all diagnostic tests"""
    print("🔧 Ollama Connection Diagnostic Tool")
    print("=" * 40)
    
    # Test server connection
    server_ok = test_ollama_server()
    if not server_ok:
        print("\n❌ Ollama server is not accessible!")
        print("💡 Solutions:")
        print("   1. Start Ollama: ollama serve")
        print("   2. Check if Ollama is installed: ollama --version")
        print("   3. Check if port 11434 is available")
        return
    
    # Test model availability
    model_ok = test_lawgorithm_model()
    if not model_ok:
        print("\n❌ lawgorithm model is not available!")
        print("💡 Solutions:")
        print("   1. Pull the model: ollama pull lawgorithm:latest")
        print("   2. Check available models: ollama list")
        return
    
    # Test model generation
    generation_ok = test_model_generation()
    if not generation_ok:
        print("\n❌ Model generation is not working!")
        print("💡 The model may be corrupted or incompatible")
        return
    
    # Test embedding generation
    embedding_ok = test_embedding_generation()
    if not embedding_ok:
        print("\n⚠️ Embedding generation may have issues, but RAG can still work with fallback")
    
    print("\n🎉 All tests completed!")
    if server_ok and model_ok and generation_ok:
        print("✅ Your Ollama setup is working correctly!")
        print("💡 You can now run the conversational RAG system")
    else:
        print("❌ Some issues were found. Please fix them before using the RAG system.")

if __name__ == "__main__":
    main() 