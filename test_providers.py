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
print("     AKHIM AI PROVIDER TEST")
print("================================")
print()


question = "Say only: TEST OK"


# --------------------------------
# GEMINI
# --------------------------------

print("[1] Testing Gemini...")

try:

    gemini = GeminiAI(GEMINI_API_KEYS)

    result = gemini.ask(question)

    if result and "Error" not in result:
        print("Gemini: ✅ WORKING")
        print("Response:", result)

    else:
        print("Gemini: ❌ FAILED")
        print(result)

except Exception as e:

    print("Gemini: ❌ FAILED")
    print(e)


print()


# --------------------------------
# GROQ
# --------------------------------

print("[2] Testing Groq...")

try:

    groq = GroqAI(GROQ_API_KEYS)

    result, error = groq.ask(question)

    if result:

        print("Groq: ✅ WORKING")
        print("Response:", result)

    else:

        print("Groq: ❌ FAILED")
        print(error)

except Exception as e:

    print("Groq: ❌ FAILED")
    print(e)


print()


# --------------------------------
# OPENROUTER
# --------------------------------

print("[3] Testing OpenRouter...")

try:

    openrouter = OpenRouterAI(
        OPENROUTER_API_KEYS
    )

    result, error = openrouter.ask(question)

    if result:

        print("OpenRouter: ✅ WORKING")
        print("Response:", result)

    else:

        print("OpenRouter: ❌ FAILED")
        print(error)

except Exception as e:

    print("OpenRouter: ❌ FAILED")
    print(e)


print()


# --------------------------------
# MISTRAL
# --------------------------------

print("[4] Testing Mistral...")

try:

    mistral = MistralAI(
        MISTRAL_API_KEYS
    )

    result, error = mistral.ask(question)

    if result:

        print("Mistral: ✅ WORKING")
        print("Response:", result)

    else:

        print("Mistral: ❌ FAILED")
        print(error)

except Exception as e:

    print("Mistral: ❌ FAILED")
    print(e)


print()
print("================================")
print("       TEST FINISHED")
print("================================")