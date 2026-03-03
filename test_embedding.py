import requests
import json
import sys

def test_ollama_embedding():
    """Test getting embeddings from Ollama"""
    print("===== Testing Ollama Embeddings =====")
    
    # First, check available models
    try:
        print("Checking available models...")
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code != 200:
            print(f"Error: Failed to get models. Status code: {response.status_code}")
            print(response.text)
            return False
        
        models_data = response.json()
        models = [model["name"] for model in models_data["models"]]
        print(f"Available models: {models}")
        
        if "bge-m3" not in models:
            print("Warning: bge-m3 model not found in the list")
            print("Attempting to use it anyway...")
        
        # Try to get embeddings using bge-m3
        print("\nTesting embedding generation with bge-m3...")
        url = "http://localhost:11434/api/embeddings"
        payload = {
            "model": "bge-m3",
            "prompt": "This is a test sentence for embedding."
        }
        
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Error: Failed to get embedding. Status code: {response.status_code}")
            print(response.text)
            return False
        
        embedding_data = response.json()
        embedding = embedding_data.get("embedding")
        
        if not embedding:
            print("Error: No embedding returned in response")
            print(json.dumps(embedding_data, indent=2))
            return False
        
        print(f"Success! Got embedding with {len(embedding)} dimensions")
        print(f"First 5 values: {embedding[:5]}")
        
        # Now try with gemma3:12b as a fallback
        print("\nTesting embedding generation with gemma3:12b...")
        payload["model"] = "gemma3:12b"
        
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Error: Failed to get embedding with gemma3:12b. Status code: {response.status_code}")
            print(response.text)
        else:
            embedding_data = response.json()
            embedding = embedding_data.get("embedding")
            
            if not embedding:
                print("Error: No embedding returned in response")
                print(json.dumps(embedding_data, indent=2))
            else:
                print(f"Success! Got embedding with {len(embedding)} dimensions")
                print(f"First 5 values: {embedding[:5]}")
        
        return True
        
    except Exception as e:
        print(f"Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_ollama_embedding()
    sys.exit(0 if success else 1) 