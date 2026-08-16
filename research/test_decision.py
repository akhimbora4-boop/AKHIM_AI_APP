from research.decision import ResearchDecision

from ai.manager import AIManager

from ai.gemini import GeminiAI
from ai.groq import GroqAI
from ai.openrouter import OpenRouterAI
from ai.mistral import MistralAI

from config.settings import (
    GEMINI_API_KEYS,
    GROQ_API_KEYS,
    OPENROUTER_API_KEYS,
    MISTRAL_API_KEYS
)


print("================================")
print("   AKHIM AI DECISION TEST")
print("================================")


gemini = GeminiAI(GEMINI_API_KEYS)

groq = GroqAI(GROQ_API_KEYS)

openrouter = OpenRouterAI(
    OPENROUTER_API_KEYS
)

mistral = MistralAI(
    MISTRAL_API_KEYS
)


ai = AIManager(
    gemini,
    groq,
    openrouter,
    mistral
)


decision = ResearchDecision(ai)


questions = [
    "Hi",
    "What is your name?",
    "What is the capital of Assam?",
    "Who is the current Prime Minister of India?",
    "What is the latest AI news?"
]


for question in questions:

    print()
    print("Question:", question)

    if decision.needs_research(question):

        print("Decision: RESEARCH")

    else:

        print("Decision: DIRECT")


print()
print("Decision test finished.")