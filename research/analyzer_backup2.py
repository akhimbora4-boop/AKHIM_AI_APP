class ResearchAnalyzer:

    def __init__(self, ai):
        self.ai = ai

    def analyze(self, question, results):

        if not results:
            return "No web research sources were found."

        research_context = ""

        for i, result in enumerate(results, start=1):

            title = result.get("title", "")
            url = result.get("url", "")
            snippet = result.get("snippet", "")
            content = result.get("content", "")

            research_context += f"""
==============================
SOURCE {i}
==============================

TITLE:
{title}

URL:
{url}

SEARCH SNIPPET:
{snippet}

PAGE CONTENT:
{content}

==============================
"""

        prompt = f"""
You are AKHIM AI, a careful web research assistant.

USER QUESTION:
{question}

Your job is to answer ONLY using the supplied web research.

STRICT SOURCE VERIFICATION RULES:

1. PAGE CONTENT is the primary evidence.

2. A search snippet alone is NOT enough to confirm
   an important factual claim.

3. Never invent facts, names, dates, numbers,
   events, companies or URLs.

4. Never assume that a homepage contains a specific
   news article.

5. Never claim that Reuters, BBC, Google, TechCrunch,
   or any other publication reported something unless
   that information is actually supported by the
   supplied source content.

6. If a source is an aggregator such as Google News,
   identify the original publication only when the
   publication name is clearly present in the supplied
   content.

7. For "today", "latest", "recent", "this week", etc.,
   prefer information with the newest visible date.

8. If no date is visible, write:
   "Date not available in source."

9. If a claim is uncertain or only partially supported,
   clearly say so.

10. Do not combine unrelated information from different
    sources to create a new claim.

11. Every important news item MUST have a source number.

12. Only include a URL that actually exists in the
    supplied source data.

13. Do not create or guess URLs.

14. If the research does not contain enough evidence,
    say:
    "The available sources do not provide enough
    evidence to confirm this."

15. Keep the answer concise and factual.

OUTPUT FORMAT:

AKHIM AI:

[Short summary]

Latest developments:

1. [News item]
   Source: Source X
   Date: [date if available]
   URL: [URL if available]

2. [News item]
   Source: Source X
   Date: [date if available]
   URL: [URL if available]

3. [News item]
   Source: Source X
   Date: [date if available]
   URL: [URL if available]

Only include items that are actually supported
by the research.

Sources:

Source 1:
[title]
[URL]

Source 2:
[title]
[URL]

Source 3:
[title]
[URL]

WEB RESEARCH:

{research_context}

Now answer the user's question.
"""

        try:

            answer = self.ai.ask(prompt)

            if not answer:
                return (
                    "I found web sources, but I could not "
                    "generate a research-based answer."
                )

            return answer

        except Exception as e:

            print("[Analyzer error:]", e)

            return (
                "I found web sources, but the research "
                "analysis failed."
            )
