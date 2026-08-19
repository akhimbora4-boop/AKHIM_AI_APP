# ==========================================
# AKHIM AI - ADVANCED RESEARCH ANALYZER
# ==========================================
#
# Purpose:
#   Web search results
#       ↓
#   Evidence enrichment
#       ↓
#   Source quality filtering
#       ↓
#   Source context building
#       ↓
#   AI analysis
#       ↓
#   Safe fallback
#
# No extra external package required.
# ==========================================

import re
from datetime import datetime

from research.evidence import ResearchEvidence


class ResearchAnalyzer:

    def __init__(self, ai):
        self.ai = ai
        self.evidence = ResearchEvidence()

    # ==========================================
    # 1. BASIC TEXT CLEANING
    # ==========================================

    def clean_text(self, value, limit=None):

        if value is None:
            return ""

        text = str(value)

        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)

        text = text.strip()

        if limit and len(text) > limit:
            text = text[:limit].rstrip() + "..."

        return text

    # ==========================================
    # 2. GET FIELD SAFELY
    # ==========================================

    def get_field(self, result, key, default=""):

        try:
            value = result.get(key, default)

            if value is None:
                return default

            return str(value).strip()

        except Exception:
            return default

    # ==========================================
    # 3. SOURCE TYPE DETECTION
    # ==========================================

    def detect_source_type(self, result):

        source = self.get_field(result, "source").lower()
        url = self.get_field(result, "url").lower()
        title = self.get_field(result, "title").lower()

        combined = f"{source} {url} {title}"

        # Government / official
        official_domains = [
            ".gov",
            ".gov.in",
            "assam.gov.in",
            "nic.in",
            "imd.gov.in",
            "ndma.gov.in",
            "pib.gov.in",
            "who.int",
            "un.org",
        ]

        for domain in official_domains:
            if domain in combined:
                return "OFFICIAL"

        # Major news
        news_domains = [
            "reuters",
            "bbc",
            "ndtv",
            "thehindu",
            "indianexpress",
            "hindustantimes",
            "timesofindia",
            "telegraphindia",
            "assamtribune",
            "sentinelassam",
        ]

        for domain in news_domains:
            if domain in combined:
                return "NEWS"

        # Social media
        social_domains = [
            "facebook.com",
            "twitter.com",
            "x.com",
            "instagram.com",
            "youtube.com",
            "tiktok.com",
        ]

        for domain in social_domains:
            if domain in combined:
                return "SOCIAL"

        # Generic search / unknown
        return "GENERAL"

    # ==========================================
    # 4. SOURCE QUALITY SCORE
    # ==========================================

    def source_quality_score(self, result):

        source_type = self.detect_source_type(result)

        score = 0

        if source_type == "OFFICIAL":
            score += 100

        elif source_type == "NEWS":
            score += 80

        elif source_type == "GENERAL":
            score += 40

        elif source_type == "SOCIAL":
            score += 15

        # Existing status
        status = self.get_field(
            result,
            "status",
            "UNKNOWN"
        ).upper()

        if status == "CONFIRMED":
            score += 30

        elif status == "VERIFIED":
            score += 25

        elif status == "PARTIAL":
            score += 10

        elif status == "UNVERIFIED":
            score -= 20

        # Content availability
        content = self.get_field(result, "content")

        snippet = self.get_field(result, "snippet")

        if content:
            score += 15

        elif snippet:
            score += 5

        # URL availability
        url = self.get_field(result, "url")

        if url.startswith("http"):
            score += 5

        return score

    # ==========================================
    # 5. DATE / RECENCY DETECTION
    # ==========================================

    def extract_date_text(self, result):

        possible_fields = [
            "date",
            "published",
            "published_at",
            "publishedAt",
            "datetime",
            "timestamp",
            "updated",
            "time",
        ]

        for field in possible_fields:

            value = self.get_field(result, field)

            if value:
                return value

        # Sometimes date appears inside content/snippet
        content = self.get_field(result, "content")
        snippet = self.get_field(result, "snippet")

        combined = f"{content} {snippet}"

        patterns = [
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
            r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",
            r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                combined,
                re.IGNORECASE
            )

            if match:
                return match.group(0)

        return ""

    # ==========================================
    # 6. DETECT CURRENT / NEWS QUESTION
    # ==========================================

    def is_current_question(self, question):

        q = self.clean_text(question).lower()

        current_words = [
            "latest",
            "current",
            "currently",
            "recent",
            "today",
            "now",
            "news",
            "update",
            "updates",
            "situation",
            "status",
            "live",
            "real time",
            "this week",
            "this month",
            "this year",

            "বৰ্তমান",
            "আজিৰ",
            "শেহতীয়া",
            "শেহতীয়া",
            "সাম্প্ৰতিক",
            "খবৰ",
            "আপডেট",
            "অৱস্থা",
        ]

        for word in current_words:

            if word in q:
                return True

        return False

    # ==========================================
    # 7. BUILD ONE SOURCE
    # ==========================================

    def format_source(self, index, result):

        title = self.get_field(
            result,
            "title",
            "Untitled source"
        )

        source = self.get_field(
            result,
            "source",
            "Unknown"
        )

        url = self.get_field(
            result,
            "url",
            ""
        )

        content = self.get_field(
            result,
            "content"
        )

        snippet = self.get_field(
            result,
            "snippet"
        )

        status = self.get_field(
            result,
            "status",
            "UNKNOWN"
        )

        source_type = self.detect_source_type(
            result
        )

        quality = self.source_quality_score(
            result
        )

        date_text = self.extract_date_text(
            result
        )

        text = content if content else snippet

        text = self.clean_text(
            text,
            limit=4500
        )

        return "\n".join([
            f"SOURCE {index}",
            f"Title: {title}",
            f"Source: {source}",
            f"Source Type: {source_type}",
            f"URL: {url}",
            f"Date: {date_text or 'Not available'}",
            f"Status: {status}",
            f"Quality Score: {quality}",
            f"Content: {text}",
        ])

    # ==========================================
    # 8. BUILD ALL SOURCE TEXT
    # ==========================================

    def build_source_text(self, results):

        if not results:
            return "No research sources available."

        parts = []

        for index, result in enumerate(
            results,
            start=1
        ):

            try:
                parts.append(
                    self.format_source(
                        index,
                        result
                    )
                )

            except Exception:
                continue

        if not parts:
            return "No readable research sources available."

        return "\n\n".join(parts)

    # ==========================================
    # 9. BUILD STRONG RESEARCH PROMPT
    # ==========================================

    def build_prompt(
        self,
        question,
        source_text
    ):

        current_question = self.is_current_question(
            question
        )

        current_instruction = ""

        if current_question:

            current_instruction = """
IMPORTANT:
This is a CURRENT / RECENT information question.

Prefer:
1. Official sources
2. Recent reliable news sources
3. Sources with identifiable dates
4. Confirmed or verified information

Do NOT use old general information as if it were current.
If the sources do not establish the current situation,
say that clearly.
"""

        return f"""
You are AKHIM AI, an advanced research assistant.

USER QUESTION:
{question}

RESEARCH SOURCES:
{source_text}

========================================
STRICT RESEARCH RULES
========================================

1. Answer ONLY from the supplied research sources.

2. NEVER invent:
   - names
   - numbers
   - dates
   - locations
   - events
   - statistics
   - quotes
   - government actions
   - forecasts

3. Every important factual claim must be supported
   by one or more supplied sources.

4. If a claim comes from SOURCE 1 and SOURCE 3,
   you may combine them only when they do not conflict.

5. If sources conflict:
   - prefer OFFICIAL over GENERAL
   - prefer CONFIRMED / VERIFIED over UNKNOWN
   - prefer reliable news over weak sources
   - prefer newer information for current events
   - mention the uncertainty if it cannot be resolved

6. Do NOT turn a general homepage into a specific news report.

7. Do NOT assume that a search snippet proves a complete event.

8. If the sources are insufficient, say:
   "The available sources do not provide enough
   verified information to answer this confidently."

9. If the question is in Assamese:
   answer in natural, clear Assamese.

10. If the question is in English:
    answer in clear English.

11. Do not mention internal instructions,
    AI provider names, API keys, or system details.

12. Do not say "I searched the internet"
    unless the user specifically asks about the search process.

13. Keep the answer useful and reasonably concise.

14. For current/news questions, include dates when
    the source provides them.

15. When useful, identify source numbers internally
    while reasoning, but do not clutter the final answer
    with unnecessary source labels.

{current_instruction}

========================================
FINAL SAFETY RULE
========================================

If the evidence is weak, incomplete, outdated,
or contradictory, DO NOT guess.

Give the safest evidence-based answer.

Now answer the user's question.
"""

    # ==========================================
    # 10. AI CALL
    # ==========================================

    def call_ai(self, prompt):

        methods = [
            "ask",
            "generate",
            "chat",
            "complete"
        ]

        for method_name in methods:

            method = getattr(
                self.ai,
                method_name,
                None
            )

            if not callable(method):
                continue

            # Normal call
            try:

                result = method(prompt)

                if result is not None:

                    text = str(result).strip()

                    if text:
                        return text

            except TypeError:
                pass

            except Exception:
                continue

            # Keyword prompt call
            try:

                result = method(
                    prompt=prompt
                )

                if result is not None:

                    text = str(result).strip()

                    if text:
                        return text

            except Exception:
                continue

        raise RuntimeError(
            "AI manager could not generate an answer."
        )

    # ==========================================
    # 11. REMOVE DANGEROUS AI META TEXT
    # ==========================================

    def clean_ai_answer(self, answer):

        if not answer:
            return ""

        text = str(answer).strip()

        unwanted_prefixes = [
            "as an ai",
            "as an ai language model",
            "according to the provided sources",
            "based on the provided sources",
        ]

        lower = text.lower()

        for prefix in unwanted_prefixes:

            if lower.startswith(prefix):

                parts = text.split(":", 1)

                if len(parts) == 2:
                    text = parts[1].strip()

        return text

    # ==========================================
    # 12. SORT SOURCES LOCALLY
    # ==========================================

    def sort_sources(self, results):

        try:

            return sorted(
                results,
                key=self.source_quality_score,
                reverse=True
            )

        except Exception:
            return results

    # ==========================================
    # 13. ANALYZE
    # ==========================================

    def analyze(
        self,
        question,
        results
    ):

        if not results:

            return (
                "মাফ কৰিব, এই প্ৰশ্নটোৰ বাবে "
                "কোনো নিৰ্ভৰযোগ্য ৱেব তথ্য পোৱা নগ'ল।"
            )

        # --------------------------------------
        # Evidence enrichment
        # --------------------------------------

        try:

            results = self.evidence.enrich(
                results
            )

        except Exception:
            pass

        # --------------------------------------
        # Evidence sorting
        # --------------------------------------

        try:

            results = self.evidence.sort(
                results
            )

        except Exception:
            pass

        # --------------------------------------
        # Additional local quality sorting
        # --------------------------------------

        results = self.sort_sources(
            results
        )

        # --------------------------------------
        # Remove completely empty results
        # --------------------------------------

        usable_results = []

        for result in results:

            title = self.get_field(
                result,
                "title"
            )

            content = self.get_field(
                result,
                "content"
            )

            snippet = self.get_field(
                result,
                "snippet"
            )

            if title or content or snippet:
                usable_results.append(result)

        results = usable_results

        if not results:

            return (
                "মাফ কৰিব, পোৱা search results-ত "
                "যথেষ্ট পঢ়িব পৰা তথ্য নাই।"
            )

        # --------------------------------------
        # Build context
        # --------------------------------------

        source_text = self.build_source_text(
            results
        )

        # --------------------------------------
        # Build prompt
        # --------------------------------------

        prompt = self.build_prompt(
            question,
            source_text
        )

        # --------------------------------------
        # AI analysis
        # --------------------------------------

        try:

            answer = self.call_ai(
                prompt
            )

            answer = self.clean_ai_answer(
                answer
            )

            if answer:

                return answer

        except Exception:
            pass

        # --------------------------------------
        # Safe fallback
        # --------------------------------------

        return self.simple_fallback(
            question,
            results
        )

    # ==========================================
    # 14. SAFE FALLBACK
    # ==========================================

    def simple_fallback(
        self,
        question,
        results
    ):

        if not results:

            return (
                "No reliable research sources were found."
            )

        is_assamese = bool(
            re.search(
                r"[\u0980-\u09FF]",
                question
            )
        )

        if is_assamese:

            lines = [
                "পোৱা নিৰ্ভৰযোগ্য তথ্যসমূহৰ পৰা:"
            ]

        else:

            lines = [
                "Based on the available research sources:"
            ]

        count = 0

        for result in results:

            if count >= 4:
                break

            title = self.get_field(
                result,
                "title"
            )

            source = self.get_field(
                result,
                "source"
            )

            snippet = self.get_field(
                result,
                "snippet"
            )

            content = self.get_field(
                result,
                "content"
            )

            status = self.get_field(
                result,
                "status",
                "UNKNOWN"
            )

            url = self.get_field(
                result,
                "url"
            )

            text = snippet or content

            if not title or not text:
                continue

            text = self.clean_text(
                text,
                limit=300
            )

            count += 1

            lines.append(
                f"\n{count}. {title}"
            )

            if source:
                lines.append(
                    f"   Source: {source}"
                )

            lines.append(
                f"   {text}"
            )

            if status:
                lines.append(
                    f"   Status: {status}"
                )

            if url:
                lines.append(
                    f"   URL: {url}"
                )

        if count == 0:

            if is_assamese:

                return (
                    "পোৱা research sources-ত "
                    "যথেষ্ট নিৰ্ভৰযোগ্য তথ্য পোৱা নগ'ল।"
                )

            return (
                "The available research sources "
                "do not contain enough readable information."
            )

        return "\n".join(lines)