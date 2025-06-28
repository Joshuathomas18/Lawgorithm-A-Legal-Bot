#!/usr/bin/env python3
"""
Ollama Setup Helper
==================

This script helps set up Ollama and the lawgorithm model for the RAG system.
"""

import subprocess
import sys
import time
import requests
import os

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama is not properly installed")
            return False
    except FileNotFoundError:
        print("❌ Ollama is not installed")
        print("💡 Install Ollama from: https://ollama.ai/")
        return False

def start_ollama_server():
    """Start Ollama server"""
    print("🚀 Starting Ollama server...")
    try:
        # Check if Ollama is already running
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama server is already running!")
            return True
    except:
        pass
    
    try:
        # Start Ollama server in background
        if os.name == 'nt':  # Windows
            subprocess.Popen(['ollama', 'serve'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        else:  # Unix/Linux/Mac
            subprocess.Popen(['ollama', 'serve'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL,
                           start_new_session=True)
        
        # Wait for server to start
        print("⏳ Waiting for Ollama server to start...")
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    print("✅ Ollama server started successfully!")
                    return True
            except:
                pass
            time.sleep(1)
        
        print("❌ Ollama server failed to start within 30 seconds")
        return False
        
    except Exception as e:
        print(f"❌ Error starting Ollama server: {e}")
        return False

def check_lawgorithm_model():
    """Check if lawgorithm model is available"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            
            if "lawgorithm:latest" in model_names:
                print("✅ lawgorithm:latest model is available!")
                return True
            else:
                print("❌ lawgorithm:latest model not found")
                return False
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return False

def pull_lawgorithm_model():
    """Pull the lawgorithm model"""
    print("📥 Pulling lawgorithm:latest model...")
    print("⚠️ This may take several minutes depending on your internet connection...")
    
    try:
        result = subprocess.run(['ollama', 'pull', 'lawgorithm:latest'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ lawgorithm:latest model pulled successfully!")
            return True
        else:
            print(f"❌ Error pulling model: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error pulling model: {e}")
        return False

def main():
    """Main setup function"""
    print("🔧 Ollama Setup Helper")
    print("=" * 30)
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        print("\n💡 Please install Ollama first:")
        print("   Windows: Download from https://ollama.ai/")
        print("   Mac: brew install ollama")
        print("   Linux: curl -fsSL https://ollama.ai/install.sh | sh")
        return
    
    # Start Ollama server
    if not start_ollama_server():
        print("\n❌ Failed to start Ollama server")
        print("💡 Try running 'ollama serve' manually in a terminal")
        return
    
    # Check if lawgorithm model is available
    if not check_lawgorithm_model():
        print("\n📥 lawgorithm model not found, pulling...")
        if not pull_lawgorithm_model():
            print("\n❌ Failed to pull lawgorithm model")
            print("💡 Try running 'ollama pull lawgorithm:latest' manually")
            return
    
    print("\n🎉 Setup completed successfully!")
    print("💡 You can now run the conversational RAG system:")
    print("   python rag/conversational_lawgorithm_rag.py")

if __name__ == "__main__":
    main() 