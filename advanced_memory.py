import chromadb
import uuid
from typing import List, Dict, Any, Optional
import os
from datetime import datetime

class AdvancedMemory:
    def __init__(self, db_path: str = "chroma_db"):
        """Initialize ChromaDB for vector storage"""
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection("creations")
        
        # Ensure Ollama is available for embedding generation
        try:
            import ollama
            self.ollama_available = True
        except ImportError:
            self.ollama_available = False
            print("Warning: Ollama not available for embeddings. Using fallback.")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text using Ollama"""
        if not self.ollama_available:
            # Fallback with simple hash-based embedding
            return [hash(word) % 1000 / 1000 for word in text.split()[:20]]
        
        try:
            response = ollama.embeddings(model="deepseek-r1:14b", prompt=text)
            return response['embedding']
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Fallback
            return [hash(word) % 1000 / 1000 for word in text.split()[:20]]
    
    def save_creation(self, original_prompt: str, enhanced_prompt: str, 
                      image_path: str, model_path: str) -> str:
        """Save creation with vector embedding for similarity search"""
        creation_id = str(uuid.uuid4())
        
        # Generate embedding from original prompt
        embedding = self.generate_embedding(original_prompt)
        
        # Add to ChromaDB
        self.collection.add(
            ids=[creation_id],
            embeddings=[embedding],
            metadatas=[{
                "original_prompt": original_prompt,
                "enhanced_prompt": enhanced_prompt,
                "image_path": image_path,
                "model_path": model_path,
                "timestamp": datetime.now().isoformat()
            }]
        )
        
        return creation_id
    
    def find_similar_creations(self, prompt: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find creations similar to the provided prompt"""
        embedding = self.generate_embedding(prompt)
        
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=limit
        )
        
        if not results['metadatas']:
            return []
        
        return [
            {
                "id": id,
                "metadata": metadata,
                "distance": distance
            }
            for id, metadata, distance in zip(
                results['ids'][0], 
                results['metadatas'][0],
                results['distances'][0]
            )
        ]
    
    def get_all_creations(self) -> List[Dict[str, Any]]:
        """Get all creations from the database"""
        results = self.collection.get()
        
        if not results['metadatas']:
            return []
        
        return [
            {
                "id": id,
                "metadata": metadata
            }
            for id, metadata in zip(results['ids'], results['metadatas'])
        ]
    
    def get_creation_by_id(self, creation_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific creation by ID"""
        try:
            result = self.collection.get(ids=[creation_id])
            
            if not result['metadatas']:
                return None
            
            return {
                "id": result['ids'][0],
                "metadata": result['metadatas'][0]
            }
        except:
            return None
