import os
import time
import json
from datetime import datetime

def monitor_training_progress():
    """Monitor the dual RAG training progress"""
    output_dir = "dual_rag_indexes"
    
    print("🔍 Monitoring Dual RAG Training Progress")
    print("=" * 50)
    
    while True:
        try:
            # Check if training is complete
            if os.path.exists(os.path.join(output_dir, "rag_metadata.json")):
                print("✅ Training Complete!")
                
                with open(os.path.join(output_dir, "rag_metadata.json"), 'r') as f:
                    metadata = json.load(f)
                
                print(f"📊 Training Results:")
                print(f"  - Structure documents: {metadata.get('structure_docs', 0):,}")
                print(f"  - Content documents: {metadata.get('content_docs', 0):,}")
                print(f"  - Structure model: {metadata.get('structure_model', 'N/A')}")
                print(f"  - Content model: {metadata.get('content_model', 'N/A')}")
                print(f"  - Chunk size: {metadata.get('chunk_size', 'N/A')}")
                print(f"  - Created at: {metadata.get('created_at', 'N/A')}")
                
                # Check file sizes
                structure_index_size = os.path.getsize(os.path.join(output_dir, "structure_index.faiss")) / (1024*1024)
                content_index_size = os.path.getsize(os.path.join(output_dir, "content_index.faiss")) / (1024*1024)
                
                print(f"  - Structure index size: {structure_index_size:.1f} MB")
                print(f"  - Content index size: {content_index_size:.1f} MB")
                
                break
            
            # Check for partial progress
            structure_exists = os.path.exists(os.path.join(output_dir, "structure_index.faiss"))
            content_exists = os.path.exists(os.path.join(output_dir, "content_index.faiss"))
            
            if structure_exists and not content_exists:
                print(f"⏳ Structure RAG complete, Content RAG in progress... {datetime.now().strftime('%H:%M:%S')}")
            elif not structure_exists:
                print(f"⏳ Training starting... {datetime.now().strftime('%H:%M:%S')}")
            
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            break
        except Exception as e:
            print(f"❌ Error monitoring: {e}")
            time.sleep(30)

if __name__ == "__main__":
    monitor_training_progress() 