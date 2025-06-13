import base64
from app.core.gemini import GeminiProcessor
import os

def test_image_embedding():
    # Initialize Gemini processor
    processor = GeminiProcessor()
    
    # Path to the test image
    image_path = os.path.join(os.path.dirname(__file__), "test_images", "project-tds-virtual-ta-q1.webp")
    
    try:
        # Read and encode image
        with open(image_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode()
        
        # Process image
        print("Processing image...")
        image_description, image_embedding = processor.process_image(image_base64)
        
        # Print results
        print("\nImage Description:")
        print("-" * 50)
        print(image_description)
        print("\nEmbedding shape:", image_embedding.shape)
        print("First few values of embedding:", image_embedding[:5])
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")

if __name__ == "__main__":
    test_image_embedding() 