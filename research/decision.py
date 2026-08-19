# ==========================================
# AKHIM AI - RESEARCH DECISION ENGINE
# ==========================================

import re


class ResearchDecision:

    def __init__(self, ai_manager):
        self.ai = ai_manager

    # ==========================================
    # 1. NORMAL / CASUAL CONVERSATION
    # ==========================================

    DIRECT_EXACT = {
        # English
        "hi",
        "hello",
        "hey",
        "how are you",
        "how are you?",
        "what is your name",
        "who are you",
        "who made you",
        "thanks",
        "thank you",
        "ok",
        "okay",
        "yes",
        "no",
        "bye",
        "good morning",
        "good afternoon",
        "good evening",
        "good night",

        # Assamese
        "হাই",
        "হেল্লো",
        "নমস্কাৰ",
        "ধন্যবাদ",
        "আপুনি কেনে আছে",
        "তুমি কেনে আছা",
        "আপোনাৰ নাম কি",
        "তোমাৰ নাম কি",
    }

    # ==========================================
    # 2. CREATIVE / NON-RESEARCH TASKS
    # ==========================================

    CREATIVE_WORDS = [
        # English
        "write",
        "rewrite",
        "poem",
        "poetry",
        "story",
        "song",
        "essay",
        "letter",
        "translate",
        "translation",
        "summarize",
        "summary",
        "code",
        "program",
        "script",
        "debug",
        "fix this code",
        "make a",
        "create a",

        # Assamese
        "লিখা",
        "লিখি দিয়া",
        "কবিতা",
        "গল্প",
        "গান",
        "ৰচনা",
        "চিঠি",
        "অনুবাদ",
        "সাৰাংশ",
        "কোড",
        "প্ৰগ্ৰাম",
    ]

    # ==========================================
    # 3. CURRENT / LIVE INFORMATION
    # ==========================================

    CURRENT_WORDS = [
        # English
        "current",
        "currently",
        "latest",
        "recent",
        "today",
        "tonight",
        "yesterday",
        "tomorrow",
        "now",
        "right now",
        "this week",
        "this month",
        "this year",
        "news",
        "update",
        "updates",
        "latest update",
        "recent update",
        "live",
        "real time",
        "present situation",
        "current situation",
        "current status",
        "latest status",
        "status",

        # Assamese
        "বৰ্তমান",
        "বৰ্তমানৰ",
        "আজিৰ",
        "আজি",
        "শেহতীয়া",
        "শেহতীয়া",
        "সাম্প্ৰতিক",
        "এতিয়া",
        "এতিয়া",
        "বৰ্তমান অৱস্থা",
        "শেহতীয়া খবৰ",
        "শেহতীয়া খবৰ",
        "খবৰ",
        "আপডেট",
        "সাম্প্ৰতিক অৱস্থা",
    ]

    # ==========================================
    # 4. RESEARCH / FACTUAL QUESTION WORDS
    # ==========================================

    QUESTION_WORDS = [
        # English
        "what",
        "who",
        "where",
        "when",
        "why",
        "how",
        "which",
        "whose",
        "tell me",
        "tell",
        "explain",
        "about",
        "information",
        "info",
        "details",
        "detail",
        "history",
        "reason",
        "meaning",
        "difference",
        "compare",
        "comparison",
        "example",
        "list",
        "facts",
        "fact",
        "price",
        "cost",
        "weather",
        "population",
        "distance",
        "location",

        # Assamese
        "কি",
        "কোন",
        "কোনে",
        "ক'ত",
        "কেতিয়া",
        "কেতিয়া",
        "কিয়",
        "কিয়",
        "কেনেকৈ",
        "কেনেদৰে",
        "কিমান",
        "কাৰ",
        "কোনটো",
        "কোনজন",
        "বিষয়ে",
        "বিষয়ে",
        "তথ্য",
        "বিৱৰণ",
        "ব্যাখ্যা",
        "ইতিহাস",
        "কাৰণ",
        "দাম",
        "মূল্য",
        "বতৰ",
        "অৱস্থা",
        "পাৰ্থক্য",
        "তুলনা",
    ]

    # ==========================================
    # 5. TOPICS THAT SHOULD STRONGLY PREFER SEARCH
    # ==========================================

    RESEARCH_TOPICS = [
        # Natural disasters
        "flood",
        "floods",
        "flood situation",
        "earthquake",
        "cyclone",
        "storm",
        "landslide",
        "disaster",

        # Weather
        "weather",
        "rain",
        "temperature",
        "rainfall",
        "forecast",

        # News / politics
        "election",
        "government",
        "minister",
        "president",
        "prime minister",
        "politics",
        "political",
        "news",

        # Technology
        "technology",
        "technology news",
        "ai news",
        "artificial intelligence",
        "software update",
        "android update",
        "iphone",
        "google",
        "openai",

        # Money / market
        "price",
        "petrol price",
        "diesel price",
        "gold price",
        "stock",
        "share price",
        "market",
        "exchange rate",

        # Sports
        "cricket",
        "football",
        "soccer",
        "match",
        "score",
        "ipl",
        "world cup",

        # Assam / India
        "assam",
        "guwahati",
        "india",
        "northeast",
        "brahmaputra",
        "barak",
        "bhutan",
        "arunachal",
    ]

    # ==========================================
    # 6. SPELLING VARIANTS / COMMON TYPOS
    # ==========================================

    TYPO_HINTS = [
        "resent",       # recent
        "recnt",
        "sisuation",    # situation
        "situaton",
        "situation",
        "assam flod",   # Assam flood
        "flod",         # flood
        "flood sisuation",
        "wheather",     # weather
        "weater",
        "informtion",   # information
        "detials",      # details
        "abaut",        # about
        "curent",       # current
        "lates",        # latest
    ]

    # ==========================================
    # TEXT NORMALIZATION
    # ==========================================

    def normalize(self, question):

        if not isinstance(question, str):
            return ""

        q = question.lower().strip()

        # Multiple spaces -> one space
        q = re.sub(r"\s+", " ", q)

        return q

    # ==========================================
    # WORD / PHRASE MATCH
    # ==========================================

    def contains_any(self, text, words):

        for word in words:

            word = word.lower().strip()

            if not word:
                continue

            # Phrase
            if " " in word:
                if word in text:
                    return True

            # Single word
            else:
                pattern = r"(?<!\w)" + re.escape(word) + r"(?!\w)"

                if re.search(pattern, text):
                    return True

        return False

    # ==========================================
    # MAIN LOCAL DECISION
    # ==========================================

    def local_decision(self, question):

        q = self.normalize(question)

        # Empty question
        if not q:
            return "DIRECT"

        # ======================================
        # STEP 1
        # Exact casual conversation
        # ======================================

        if q in self.DIRECT_EXACT:
            return "DIRECT"

        # ======================================
        # STEP 2
        # Creative work
        # ======================================

        if self.contains_any(q, self.CREATIVE_WORDS):
            return "DIRECT"

        # ======================================
        # STEP 3
        # Current / latest information
        # ALWAYS RESEARCH
        # ======================================

        if self.contains_any(q, self.CURRENT_WORDS):
            return "RESEARCH"

        # ======================================
        # STEP 4
        # Strong research topics
        # ALWAYS RESEARCH
        # ======================================

        if self.contains_any(q, self.RESEARCH_TOPICS):
            return "RESEARCH"

        # ======================================
        # STEP 5
        # Question / factual language
        # ======================================

        if self.contains_any(q, self.QUESTION_WORDS):
            return "RESEARCH"

        # ======================================
        # STEP 6
        # Common spelling mistakes
        # ======================================

        if self.contains_any(q, self.TYPO_HINTS):
            return "RESEARCH"

        # ======================================
        # STEP 7
        # Question mark
        # ======================================

        if "?" in q or "？" in q:
            return "RESEARCH"

        # ======================================
        # STEP 8
        # UNKNOWN INPUT
        #
        # Important:
        # Unknown factual questions should
        # prefer SEARCH instead of hallucination.
        # ======================================

        return "RESEARCH"

    # ==========================================
    # PUBLIC FUNCTION
    # ==========================================

    def needs_research(self, question):

        return self.local_decision(question) == "RESEARCH"