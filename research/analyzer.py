from research.evidence import ResearchEvidence


class ResearchAnalyzer:

    def __init__(self, ai):

        self.ai = ai

        self.evidence = ResearchEvidence()


    # =================================
    # BUILD SOURCE TEXT
    # =================================

    def build_source_text(self, results):

        if not results:
            return "No research sources available."

        parts = []

        for index, result in enumerate(
            results,
            start=1
        ):

            title = str(
                result.get(
                    "title",
                    ""
                )
            ).strip()

            source = str(
                result.get(
                    "source",
                    ""
                )
            ).strip()

            url = str(
                result.get(
                    "url",
                    ""
                )
            ).strip()

            content = str(
                result.get(
                    "content",
                    ""
                )
            ).strip()

            snippet = str(
                result.get(
                    "snippet",
                    ""
                )
            ).strip()

            status = str(
                result.get(
                    "status",
                    "UNKNOWN"
                )
            ).strip()

            freshness = str(
                result.get(
                    "freshness",
                    "UNKNOWN"
                )
            ).strip()

            evidence = result.get(
                "evidence_score",
                0
            )


            text = content

            if not text:
                text = snippet


            # Limit very large pages
            if len(text) > 5000:
                text = text[:5000]


            parts.append(
                "\n".join(
                    [
                        f"SOURCE {index}",
                        f"Title: {title}",
                        f"Source: {source}",
                        f"URL: {url}",
                        f"Status: {status}",
                        f"Freshness: {freshness}",
                        f"Evidence score: {evidence}",
                        f"Content: {text}",
                    ]
                )
            )


        return "\n\n".join(parts)


    # =================================
    # BUILD PROMPT
    # =================================

    def build_prompt(
        self,
        question,
        source_text
    ):

        return f"""
You are AKHIM AI, a careful research assistant.

User question:
{question}

Research sources:
{source_text}

Instructions:

1. Answer the user's question directly.
2. Use the research sources as the main evidence.
3. Do not invent facts that are not supported by the sources.
4. If sources disagree, explain the disagreement.
5. Clearly distinguish confirmed information from reported information.
6. Do not treat an evidence score as a truth score.
7. For current or latest questions, prefer newer sources.
8. If the sources are insufficient, say what is uncertain.
9. Do not say "latest AI news" unless the question actually asks about AI news.
10. Answer in the same language as the user's question when possible.
11. Be concise but informative.
12. Include source numbers when useful.

Now answer the user.
"""


    # =================================
    # CALL AI
    # =================================

    def call_ai(self, prompt):

        # Try the project's AI manager methods
        methods = [
            "ask",
            "generate",
            "chat",
            "complete",
        ]

        for method_name in methods:

            method = getattr(
                self.ai,
                method_name,
                None
            )

            if not callable(method):
                continue

            try:

                result = method(
                    prompt
                )

                if result is None:
                    continue

                text = str(
                    result
                ).strip()

                if text:
                    return text

            except TypeError:

                try:

                    result = method(
                        prompt=prompt
                    )

                    if result is None:
                        continue

                    text = str(
                        result
                    ).strip()

                    if text:
                        return text

                except Exception:
                    continue

            except Exception:
                continue


        raise RuntimeError(
            "AI manager could not generate an answer."
        )


    # =================================
    # ANALYZE
    # =================================

    def analyze(
        self,
        question,
        results
    ):

        if not results:

            return (
                "I could not find reliable "
                "research sources for this question."
            )


        # Add evidence information
        try:

            results = self.evidence.enrich(
                results
            )

        except Exception:
            pass


        # Rank evidence
        try:

            results = self.evidence.sort(
                results
            )

        except Exception:
            pass


        source_text = self.build_source_text(
            results
        )

        prompt = self.build_prompt(
            question,
            source_text
        )


        print(
            "[AI analysis in progress...]"
        )


        try:

            answer = self.call_ai(
                prompt
            )

            return answer

        except Exception as error:

            print(
                "[AI analysis failed:",
                error,
                "]"
            )

            # Simple source-based fallback
            return self.simple_fallback(
                question,
                results
            )


    # =================================
    # SIMPLE FALLBACK
    # =================================

    def simple_fallback(
        self,
        question,
        results
    ):

        if not results:

            return (
                "No reliable sources were found."
            )


        lines = []

        lines.append(
            "Based on the available sources:"
        )

        lines.append("")


        count = 0

        for result in results:

            if count >= 7:
                break

            title = str(
                result.get(
                    "title",
                    ""
                )
            ).strip()

            snippet = str(
                result.get(
                    "snippet",
                    ""
                )
            ).strip()

            content = str(
                result.get(
                    "content",
                    ""
                )
            ).strip()

            status = str(
                result.get(
                    "status",
                    "UNKNOWN"
                )
            ).strip()

            if not snippet:
                snippet = content

            if not title:
                continue

            if len(snippet) > 350:
                snippet = snippet[:350] + "..."

            lines.append(
                f"{count + 1}. {title}"
            )

            if snippet:

                lines.append(
                    f"   {snippet}"
                )

            lines.append(
                f"   Status: {status}"
            )

            lines.append("")

            count += 1


        if count == 0:

            return (
                "The available research sources "
                "do not contain enough readable "
                "information to answer confidently."
            )


        return "\n".join(lines)