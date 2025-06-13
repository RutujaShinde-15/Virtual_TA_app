import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Optional
import os
from app.core.gemini import GeminiProcessor

class RAGEngine:
    def __init__(self):
        self.gemini = GeminiProcessor()
        
        # Correct path to embeddings
        embeddings_dir = os.path.join(os.path.dirname(__file__), "..", "..", "embeddings")
        embeddings_dir = os.path.abspath(embeddings_dir)
        
        try:
            # Load course content
            self.course_embeddings = np.load(os.path.join(embeddings_dir, "course_embeddings.npy"))
            self.course_metadata = pd.read_csv(os.path.join(embeddings_dir, "course_metadata.csv"))
            
            # Load posts content
            self.posts_embeddings = np.load(os.path.join(embeddings_dir, "posts_embeddings.npy"))
            self.posts_metadata = pd.read_csv(os.path.join(embeddings_dir, "posts_metadata.csv"))
            
            # Load full texts
            self.course_texts = pd.read_csv(os.path.join(embeddings_dir, "course_texts.csv"))
            self.posts_texts = pd.read_csv(os.path.join(embeddings_dir, "posts_texts.csv"))
        except Exception as e:
            print(f"Warning: Could not load embeddings: {e}")
            # Initialize empty embeddings for testing
            self.course_embeddings = np.array([])
            self.course_metadata = pd.DataFrame()
            self.posts_embeddings = np.array([])
            self.posts_metadata = pd.DataFrame()
    
    def get_relevant_context(self, question_embedding: List[float], image_embedding: Optional[np.ndarray] = None, top_k: int = 3) -> List[Dict]:
        """Get most relevant context from embeddings using cosine similarity."""
        if len(self.course_embeddings) == 0 and len(self.posts_embeddings) == 0:
            return [{"text": "No embeddings available yet. This is a test response.", "url": None}]
        
        # Calculate cosine similarity for text
        course_scores = np.dot(self.course_embeddings, question_embedding) / (
            np.linalg.norm(self.course_embeddings, axis=1) * np.linalg.norm(question_embedding)
        )
        posts_scores = np.dot(self.posts_embeddings, question_embedding) / (
            np.linalg.norm(self.posts_embeddings, axis=1) * np.linalg.norm(question_embedding)
        )
        
        # If image embedding is provided, combine scores
        if image_embedding is not None:
            image_course_scores = np.dot(self.course_embeddings, image_embedding) / (
                np.linalg.norm(self.course_embeddings, axis=1) * np.linalg.norm(image_embedding)
            )
            image_posts_scores = np.dot(self.posts_embeddings, image_embedding) / (
                np.linalg.norm(self.posts_embeddings, axis=1) * np.linalg.norm(image_embedding)
            )
            
            # Combine text and image scores with equal weight
            course_scores = (course_scores + image_course_scores) / 2
            posts_scores = (posts_scores + image_posts_scores) / 2
        
        # Debug: Print top 10 course chunks by similarity
        print("\nTop 10 course context candidates:")
        top_course_indices_debug = np.argsort(course_scores)[-10:][::-1]
        for idx in top_course_indices_debug:
            section = self.course_metadata.iloc[idx]["section"] if "section" in self.course_metadata.columns else "?"
            text = self.course_metadata.iloc[idx]["text"] if "text" in self.course_metadata.columns else "?"
            print(f"Score: {course_scores[idx]:.4f} | Section: {section} | Text: {text[:100]}")
        
        # Get top matches from both sources
        top_course_indices = np.argsort(course_scores)[-top_k:]
        top_posts_indices = np.argsort(posts_scores)[-top_k:]
        
        context = []
        
        # Add course content
        for idx in top_course_indices:
            context.append({
                "text": self.course_metadata.iloc[idx]["text"],
                "url": self.course_metadata.iloc[idx]["url"] if "url" in self.course_metadata.columns else None,
                "score": float(course_scores[idx])
            })
        
        # Add posts
        for idx in top_posts_indices:
            context.append({
                "text": self.posts_metadata.iloc[idx]["text"] if "text" in self.posts_metadata.columns else "?",
                "url": self.posts_metadata.iloc[idx]["url"] if "url" in self.posts_metadata.columns else None,
                "score": float(posts_scores[idx])
            })
        
        return sorted(context, key=lambda x: x.get("score", 0), reverse=True)[:top_k]
    
    def _cosine_similarity(self, query_embedding: np.ndarray, embeddings: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity between query and all embeddings."""
        # Normalize embeddings
        query_norm = np.linalg.norm(query_embedding)
        embeddings_norm = np.linalg.norm(embeddings, axis=1)
        
        # Calculate similarity
        similarities = np.dot(embeddings, query_embedding) / (embeddings_norm * query_norm)
        
        return similarities
    
    def get_answer(self, question: str, image_base64: Optional[str] = None) -> Tuple[str, List[Dict[str, str]]]:
        """Get answer for a question using RAG."""
        try:
            # For testing, return a dummy response when no embeddings are available
            if len(self.course_embeddings) == 0 and len(self.posts_embeddings) == 0:
                return (
                    "This is a test response. The embeddings are not loaded yet.",
                    [{"url": "https://example.com", "text": "Example reference"}]
                )
            
            # Get question embedding
            question_embedding = self.gemini.get_embedding(question)
            
            # Process image if provided
            image_description = None
            image_embedding = None
            if image_base64:
                image_description, image_embedding = self.gemini.process_image(image_base64)
            
            # Get relevant context
            context = self.get_relevant_context(question_embedding, image_embedding)
            
            # Combine all context texts
            combined_context = "\n".join([c["text"] for c in context])
            
            # Generate answer using Gemini
            answer = self.gemini.generate_answer(question, combined_context, image_description)
            
            # Format links from context
            links = [
                {"url": ctx["url"], "text": ctx["text"][:100] + "..."} 
                for ctx in context 
                if ctx["url"] is not None
            ]
            
            return answer, links
            
        except Exception as e:
            print(f"Error in get_answer: {e}")
            return "I apologize, but I encountered an error while processing your question.", [] 