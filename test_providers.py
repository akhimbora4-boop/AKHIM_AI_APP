import time
import traceback

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


# ============================================================
# AKHIM AI — PROVIDER DIAGNOSTIC TEST
# ============================================================

print("=" * 60)
print("              AKHIM AI PROVIDER TEST")
print("=" * 60)
print()

QUESTION = "Say only: TEST OK"


# ============================================================
# HELPERS
# ============================================================

def normalize_keys(keys):
    """
    Convert API-key configuration into a clean list.
    """

    if keys is None:
        return []

    if isinstance(keys, str):
        keys = [keys]

    try:
        return [
            str(key).strip()
            for key in keys
            if str(key).strip()
        ]
    except Exception:
        return []


def mask_key(key):
    """
    Hide API key in terminal output.
    """

    if not key:
        return "NONE"

    if len(key) <= 8:
        return "********"

    return (
        key[:4]
        + "..."
        + key[-4:]
    )


def print_keys(name, keys):

    clean = normalize_keys(keys)

    print(
        f"{name} API keys : {len(clean)}"
    )

    for index, key in enumerate(
        clean,
        start=1
    ):

        print(
            f"   Key {index}: {mask_key(key)}"
        )

    if not clean:
        print(
            "   ⚠ No API keys configured."
        )

    print()


def extract_result(response):

    """
    Provider methods may return:

        result
        (result, error)

    Handle both safely.
    """

    if isinstance(response, tuple):

        result = response[0] if len(response) > 0 else None
        error = response[1] if len(response) > 1 else None

        return result, error

    return response, None


def is_success(result):

    if result is None:
        return False

    text = str(result).strip()

    if not text:
        return False

    error_words = [
        "error:",
        "api error",
        "authentication error",
        "unauthorized",
        "invalid api key",
        "rate limit",
        "failed"
    ]

    lower = text.lower()

    for word in error_words:

        if word in lower:
            return False

    return True


# ============================================================
# PROVIDER TEST
# ============================================================

def test_provider(
    number,
    name,
    provider_class,
    keys
):

    print("-" * 60)

    print(
        f"[{number}] Testing {name}..."
    )

    print()

    clean_keys = normalize_keys(keys)

    print(
        f"Configured keys: {len(clean_keys)}"
    )

    if not clean_keys:

        print(
            f"{name}: ❌ FAILED"
        )

        print(
            "Reason: No API keys configured."
        )

        print()

        return False

    start_time = time.time()

    try:

        provider = provider_class(
            clean_keys
        )

        response = provider.ask(
            QUESTION
        )

        result, error = extract_result(
            response
        )

        elapsed = (
            time.time()
            - start_time
        )

        if is_success(result):

            print(
                f"{name}: ✅ WORKING"
            )

            print(
                f"Response time: {elapsed:.2f}s"
            )

            print(
                "Response:"
            )

            print(
                str(result).strip()
            )

            return True

        print(
            f"{name}: ❌ FAILED"
        )

        print(
            f"Response time: {elapsed:.2f}s"
        )

        if error:

            print(
                "Error:"
            )

            print(
                str(error)
            )

        elif result:

            print(
                "Provider response:"
            )

            print(
                str(result)
            )

        else:

            print(
                "Empty response."
            )

        return False

    except Exception as error:

        elapsed = (
            time.time()
            - start_time
        )

        print(
            f"{name}: ❌ FAILED"
        )

        print(
            f"Response time: {elapsed:.2f}s"
        )

        print(
            "Exception:"
        )

        print(
            str(error)
        )

        return False


# ============================================================
# SHOW CONFIGURATION
# ============================================================

print("API KEY CONFIGURATION")
print("=" * 60)

print_keys(
    "Gemini",
    GEMINI_API_KEYS
)

print_keys(
    "Groq",
    GROQ_API_KEYS
)

print_keys(
    "OpenRouter",
    OPENROUTER_API_KEYS
)

print_keys(
    "Mistral",
    MISTRAL_API_KEYS
)


# ============================================================
# RUN TESTS
# ============================================================

results = {}


results["Gemini"] = test_provider(
    1,
    "Gemini",
    GeminiAI,
    GEMINI_API_KEYS
)

print()


results["Groq"] = test_provider(
    2,
    "Groq",
    GroqAI,
    GROQ_API_KEYS
)

print()


results["OpenRouter"] = test_provider(
    3,
    "OpenRouter",
    OpenRouterAI,
    OPENROUTER_API_KEYS
)

print()


results["Mistral"] = test_provider(
    4,
    "Mistral",
    MistralAI,
    MISTRAL_API_KEYS
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 60)
print("                 TEST SUMMARY")
print("=" * 60)
print()

working = 0
failed = 0

for name, status in results.items():

    if status:

        print(
            f"{name:<15} : ✅ WORKING"
        )

        working += 1

    else:

        print(
            f"{name:<15} : ❌ FAILED"
        )

        failed += 1


print()

print(
    f"Working providers : {working}"
)

print(
    f"Failed providers  : {failed}"
)

print()

if working > 0:

    print(
        "AKHIM AI has at least one "
        "working AI provider."
    )

else:

    print(
        "⚠ No AI provider is working."
    )

print()

print("=" * 60)
print("                  TEST FINISHED")
print("=" * 60)