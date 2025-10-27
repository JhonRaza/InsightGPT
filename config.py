"""
Configuration management for InsightGPT
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # OpenAI Settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_MODEL = "gpt-4"
    FALLBACK_MODEL = "gpt-3.5-turbo"
    
    # Document Processing
    MAX_FILE_SIZE_MB = 10
    CHUNK_SIZE = 1000  # Characters per chunk
    CHUNK_OVERLAP = 200  # Overlap between chunks
    
    # Embedding Settings
    EMBEDDING_MODEL = "text-embedding-ada-002"
    EMBEDDING_DIMENSION = 1536
    TOP_K_RESULTS = 3  # Number of relevant chunks to retrieve
    
    # UI Settings
    APP_TITLE = "InsightGPT – Intelligent Knowledge Explorer"
    APP_ICON = "🧠"
    SIDEBAR_STATE = "expanded"
    
    # Temperature settings for different tasks
    TEMPERATURE_SUMMARY = 0.3
    TEMPERATURE_EXTRACTION = 0.2
    TEMPERATURE_QA = 0.7
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate that API key is set and not a placeholder"""
        if not api_key:
            return False
        if api_key in ["your_openai_api_key_here", "sk-..."]:
            return False
        if not api_key.startswith("sk-"):
            return False
        return True
