
import sys
import os
import chromadb

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def check_count():
    try:
        client = chromadb.PersistentClient(path="data/chroma_db")
        collection = client.get_or_create_collection(name="rag_collection")
        count = collection.count()
        print(f"COUNT: {count}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_count()
