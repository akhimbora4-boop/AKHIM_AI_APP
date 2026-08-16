cd /storage/emulated/0/AKHIM_AI
cat > research/analyzer.py <<'PY'
from ai.manager import AIManager


class ResearchAnalyzer:

    def __init__(self, ai):
        self.ai = ai

    def analyze(self, question, results):

        if not results:
            return "No web research sources were found."

        research_context = ""

        for i, result in enumerate(
            results,
            start=1
        ):

            research_context += f"""
SOURCE {i}

TITLE:
{result.get('title', '')}

URL:
{result.get('url', '')}

SEARCH SNIPPET:
{result.get('snippet', '')}

PAGE CONTENT:
{result.get('content', '')}
date = result.get("date", "")
source = result.get("source", "")

--------------------------------
"""

        prompt = f"""
You are AKHIM AI Research Assistant.

USER QUESTION:

{question}

Use the web research below to answer the user's question.

IMPORTANT RULES:

1. Use the actual information found in PAGE CONTENT.
2. Do not invent facts.
3. Do not treat advertisements as news.
4. Do not treat a homepage description as a
   specific news article.
5. If the sources do not contain specific
   information, clearly say so.
6. Give a concise and useful answer.
7. Mention important source numbers.
8. If dates are available, include them.
9. For "latest" questions, prioritize the
   newest information available.
10. Distinguish facts from uncertainty.
11. Do not claim something is latest unless
    the available source information supports it.

WEB RESEARCH:

{research_context}

Now answer the user's question.
"""

        try:

            answer = self.ai.ask(prompt)

            if not answer:
                return "I could not generate an answer from the research sources."

            return answer

        except Exception as e:

            print(
                "[Analyzer error:]",
                e
            )

            return (
                "I found web sources, but I could not "
                "analyze them successfully."
            )
PY