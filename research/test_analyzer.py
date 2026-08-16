from research.web_search import WebSearch
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
print("     AKHIM AI RESEARCH TEST")
print("================================")
print()

question = "What is the latest AI news?"

print("Question:", question)
print()
print("Searching web...")
print()


# --------------------------------
# Web Search
# --------------------------------

searcher = WebSearch()

results = searcher.research(
    question,
    max_results=5
)


if not results:

    print("ERROR: No search results found.")
    raise SystemExit


print(
    f"Found {len(results)} sources."
)

print()


# --------------------------------
# Show sources
# --------------------------------

for i, result in enumerate(
    results,
    start=1
):

    print(
        f"[{i}] {result['title']}"
    )

    print(
        "URL:",
        result["url"]
    )

    print(
        "Snippet:",
        result["snippet"]
    )

    print(
        "-" * 50
    )


# --------------------------------
# Build research context
# --------------------------------

research_context = ""

for i, result in enumerate(
    results,
    start=1
):

    research_context = ""

for i, result in enumerate(
    results,
    start=1
):

    research_context += f"""
SOURCE {i}

TITLE:
{result['title']}

URL:
{result['url']}

SEARCH SNIPPET:
{result['snippet']}

PAGE CONTENT:
{result.get('content', '')}

--------------------------------
"""
# --------------------------------
# AI Providers
# --------------------------------

gemini = GeminiAI(
    GEMINI_API_KEYS
)

groq = GroqAI(
    GROQ_API_KEYS
)

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


# --------------------------------
# Analysis
# --------------------------------

print()
print("Analyzing sources...")
print()


prompt = f"""
You are AKHIM AI Research Assistant.

The user asked:

{question}

You MUST answer using ONLY the web search
sources provided below.

IMPORTANT RULES:

1. Do not invent news.
2. Do not add information that is not present
   in the sources.
3. Identify actual news or useful information
   from the sources.
4. If the sources are only general pages and
   do not contain specific news, clearly say so.
5. Do not pretend that a general news homepage
   is a specific news article.
6. Keep the answer concise and useful.
7. Mention the source number for each important
   claim.
8. If there are no specific latest news details,
   say that clearly.

WEB SOURCES:

{research_context}

Now provide the best possible answer.
"""


answer = ai.ask(prompt)


# --------------------------------
# Final output
# --------------------------------

print("================================")
print("          AKHIM AI")
print("================================")

print(answer)

print()
print("Research test finished.")