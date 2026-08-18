from research.evidence import ResearchEvidence

class ResearchAnalyzer:

    def __init__(self, ai):
        self.ai = ai
        self.evidence = ResearchEvidence()

    def build_source_text(self, results):
        if not results:
            return "No research sources available."

        parts = []
        for index, result in enumerate(results, start=1):
            title = str(result.get("title", "")).strip()
            source = str(result.get("source", "")).strip()
            url = str(result.get("url", "")).strip()
            content = str(result.get("content", "")).strip()
            snippet = str(result.get("snippet", "")).strip()
            status = str(result.get("status", "UNKNOWN")).strip()

            text = content if content else snippet
            if len(text) > 5000:
                text = text[:5000]

            parts.append(
                "\n".join([
                    f"SOURCE {index}",
                    f"Title: {title}",
                    f"Source: {source}",
                    f"URL: {url}",
                    f"Status: {status}",
                    f"Content: {text}",
                ])
            )
        return "\n\n".join(parts)

    def build_prompt(self, question, source_text):
        return f"""
You are AKHIM AI, an advanced and highly accurate research assistant.

User question:
{question}

Research sources:
{source_text}

STRICT INSTRUCTIONS:
1. Answer the user's question directly and accurately based ONLY on the provided sources.
2. If the user asks in Assamese, answer in beautiful and correct Assamese. If in English, answer in English.
3. Do not invent or fabricate any information. If the sources do not contain the answer, clearly state that you don't have enough verified information.
4. If there are conflicting facts in the sources, mention the most reliable one (Status: CONFIRMED).
5. Be concise, clear, and professional. 
6. Do not include internal system messages like "Based on the sources". Just give the direct answer.

Now provide the best possible answer.
"""

    def call_ai(self, prompt):
        methods = ["ask", "generate", "chat", "complete"]
        
        for method_name in methods:
            method = getattr(self.ai, method_name, None)
            if not callable(method):
                continue
            
            try:
                result = method(prompt)
                if result is not None:
                    text = str(result).strip()
                    if text:
                        return text
            except TypeError:
                try:
                    result = method(prompt=prompt)
                    if result is not None:
                        text = str(result).strip()
                        if text:
                            return text
                except Exception:
                    continue
            except Exception:
                continue

        raise RuntimeError("AI manager could not generate an answer.")

    def analyze(self, question, results):
        if not results:
            return "মাফ কৰিব, এই প্ৰশ্নটোৰ বাবে কোনো নিৰ্ভৰযোগ্য ৱেব তথ্য পোৱা নগ'ল।"

        try:
            results = self.evidence.enrich(results)
            results = self.evidence.sort(results)
        except Exception:
            pass

        source_text = self.build_source_text(results)
        prompt = self.build_prompt(question, source_text)

        try:
            answer = self.call_ai(prompt)
            return answer
        except Exception as error:
            return self.simple_fallback(question, results)

    def simple_fallback(self, question, results):
        if not results:
            return "No reliable sources were found."

        lines = ["Based on the available sources:\n"]
        count = 0

        for result in results:
            if count >= 4:
                break
            title = str(result.get("title", "")).strip()
            snippet = str(result.get("snippet", "")).strip()
            content = str(result.get("content", "")).strip()
            status = str(result.get("status", "UNKNOWN")).strip()

            if not snippet:
                snippet = content
            if not title:
                continue

            if len(snippet) > 200:
                snippet = snippet[:200] + "..."

            lines.append(f"{count + 1}. {title}")
            if snippet:
                lines.append(f"   {snippet}")
            lines.append("")
            count += 1

        if count == 0:
            return "The available research sources do not contain enough readable information."
            
        return "\n".join(lines)
