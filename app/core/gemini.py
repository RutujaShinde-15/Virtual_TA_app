import google.generativeai as genai
from google.generativeai import types
from typing import Optional, Tuple
import os
from PIL import Image
import io
import base64
import numpy as np
import requests

class GeminiProcessor:
    def __init__(self):
        # Load Gemini API key from environment variable
        self.api_key = os.environ.get("GEMINI_API_KEY")  # Set GEMINI_API_KEY in your .env or environment
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.vision_model = genai.GenerativeModel('gemini-1.5-flash')
        # If you want vision, use the correct vision model name if available, or remove if not needed
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding using AIPipe's OpenAI embeddings."""
        try:
            EMBEDDING_ENDPOINT = "https://aiproxy.sanand.workers.dev/openai/v1/embeddings"
            AIPIPE_API_KEY = os.environ.get("AIPIPE_API_KEY")  # Set AIPIPE_API_KEY in your .env or environment
            if not AIPIPE_API_KEY:
                raise ValueError("AIPIPE_API_KEY environment variable not set.")
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {AIPIPE_API_KEY}"
            }
            
            data = {
                "model": "text-embedding-3-small",
                "input": text
            }
            
            response = requests.post(EMBEDDING_ENDPOINT, headers=headers, json=data)
            if response.status_code == 200:
                embedding = response.json()['data'][0]['embedding']
                return np.array(embedding)
            else:
                raise Exception(f"Embedding API error: {response.text}")
        except Exception as e:
            raise Exception(f"Error getting embedding: {str(e)}")
    
    def process_image(self, image_base64: str) -> Tuple[str, np.ndarray]:
        """Process image using Gemini Vision and get both text description and embedding."""
        try:
            # Decode base64 image
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # Get image description using Gemini Vision
            prompt = "Describe this image in detail, focusing on any text, diagrams, or technical content that might be relevant for a data science course."
            response = self.vision_model.generate_content([prompt, image])
            image_description = response.text
            
            # Get embedding for the image description
            image_embedding = self.get_embedding(image_description)
            
            return image_description, image_embedding
            
        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")
    
    def generate_answer(self, question: str, context: str, image_description: Optional[str] = None) -> str:
        """Generate an answer using Gemini based on the question, context, and optional image description."""
        prompt = f"""You are a helpful Teaching Assistant for IIT Madras' Tools in Data Science course.
        Based on the following context, answer the student's question:
        
        Context: {context}
        
        {f'Image Description: {image_description}' if image_description else ''}
        
        Question: {question}
        
        Please provide a clear, concise, and accurate answer. If the context doesn't contain enough information
        to answer the question fully, say so and provide the best possible answer with the available information."""
        
        response = self.model.generate_content(prompt)
        return response.text 