import requests
import json
import logging

class OllamaChat:
    """Interface for local Ollama LLM interactions"""
    
    def __init__(self, base_url="http://127.0.0.1:11434", model="llama3"):
        self.base_url = base_url
        self.is_available = self._check_availability()
        self.model = self._ensure_model_available(model) if self.is_available else model
        
    def _check_availability(self):
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        return False

    def _ensure_model_available(self, requested_model):
        """Check if model exists, if not pick the first available one to avoid errors"""
        try:
            available_models = self.get_model_list()
            if not available_models:
                return requested_model # No models found, might default to pull?
            
            # Check for exact match or substring match
            for m in available_models:
                if requested_model in m or m in requested_model:
                    return m
            
            # If requested not found, return the first available one (usually the best bet)
            print(f"Requested model '{requested_model}' not found. Using '{available_models[0]}'")
            return available_models[0]
        except:
            return requested_model
        
    def generate_response(self, user_query, context_data=None, system_prompt=None):
        """
        Generate a response using Ollama
        
        Args:
            user_query (str): The user's question
            context_data (str/dict): Retrieved data to be used as context
            system_prompt (str): Optional override for system prompt
            
        Returns:
            str: The LLM's response
        """
        if not self.is_available:
            return None
            
        # Default system prompt
        if not system_prompt:
            system_prompt = """You are an expert NBA AI assistant. 
            Use the provided context data to answer the user's question. 
            If the context contains statistics or predictions, cite them accurately.
            Be concise, professional, and helpful.
            If the context doesn't have the answer, admit you don't know based on the available data.
            Do not make up facts not present in the context.
            """
            
        # Format context
        formatted_context = ""
        if context_data:
            if isinstance(context_data, dict):
                formatted_context = f"CONTEXT DATA:\n{json.dumps(context_data, indent=2)}"
            else:
                formatted_context = f"CONTEXT DATA:\n{str(context_data)}"
        
        full_prompt = f"{system_prompt}\n\n{formatted_context}\n\nUSER QUESTION: {user_query}"
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                error_msg = f"Ollama API Error ({response.status_code}): {response.text}"
                logging.error(error_msg)
                return f"Error: {error_msg}"
                
        except Exception as e:
            error_msg = f"Connection Failed: {str(e)}"
            logging.error(error_msg)
            return f"Error: {error_msg}"

    def get_embedding(self, text, model=None):
        """Get embedding for text from Ollama"""
        if not self.is_available:
            return None
        
        # Use bge-m3 for embeddings if not specified
        if model is None:
            model = "bge-m3:latest"
            
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": model,
                    "prompt": text
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('embedding')
            else:
                logging.error(f"Ollama Embedding Error ({response.status_code}): {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Embedding Connection Failed: {str(e)}")
            return None

    def get_model_list(self):
        """Get list of available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [m['name'] for m in models]
        except:
            pass
        return []
