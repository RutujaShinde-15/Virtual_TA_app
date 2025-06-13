import os

# Provider-specific configurations
PROVIDER_CONFIGS = {
    EmbeddingProvider.GEMINI: {
        "api_key": os.environ.get("GEMINI_API_KEY"),  # Set GEMINI_API_KEY in your .env or environment
        "model_name": "gemini-pro",
        "embedding_model": "gemini-embedding-exp-03-07",
        "max_output_tokens": 2048,
        "temperature": 0.7,
        "top_p": 1,
        "top_k": 1,
        "embedding_dim": 768
    },
    EmbeddingProvider.AIPROXY: {
        "api_key": os.environ.get("AIPIPE_API_KEY"),  # Set AIPIPE_API_KEY in your .env or environment
        "embedding_endpoint": "https://aiproxy.sanand.workers.dev/openai/v1/embeddings",
        "chat_endpoint": "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions",
        "embedding_model": "text-embedding-3-small",
        "chat_model": "gpt-4o-mini",
        "embedding_dim": 1536
    }
} 