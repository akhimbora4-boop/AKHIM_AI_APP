import os
GEMINI_API_KEYS = os.environ.get("GEMINI_API_KEYS", "").split(",")
GROQ_API_KEYS = os.environ.get("GROQ_API_KEYS", "").split(",")
OPENROUTER_API_KEYS = os.environ.get("OPENROUTER_API_KEYS", "").split(",")
MISTRAL_API_KEYS = os.environ.get("MISTRAL_API_KEYS", "").split(",")