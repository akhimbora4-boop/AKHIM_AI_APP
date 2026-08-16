class ResearchDecision:

    def __init__(self, ai_manager):
        self.ai = ai_manager


    # =================================
    # LOCAL DECISION
    # =================================

    def local_decision(self, question):

        q = question.lower().strip()

        # ---------------------------------
        # Simple conversation
        # ---------------------------------

        direct_words = [
            "hi",
            "hello",
            "hey",
            "how are you",
            "what is your name",
            "who are you",
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
            "good night"
        ]

        for word in direct_words:

            if q == word:
                return "DIRECT"


        # ---------------------------------
        # Assamese simple conversation
        # ---------------------------------

        direct_assamese = [
            "তোমাৰ নাম কি",
            "আপোনাৰ নাম কি",
            "তুমি কেনে আছা",
            "আপুনি কেনে আছে",
            "ধন্যবাদ",
            "নমস্কাৰ"
        ]

        for word in direct_assamese:

            if q == word:
                return "DIRECT"


        # ---------------------------------
        # Current information
        # ---------------------------------

        research_words = [
            "current",
            "latest",
            "recent",
            "today",
            "now",
            "news",
            "2026",
            "currently",
            "বৰ্তমান",
            "আজিৰ",
            "শেহতীয়া",
            "সাম্প্ৰতিক",
            "খবৰ"
        ]

        for word in research_words:

            if word in q:
                return "RESEARCH"


        return None


    # =================================
    # AI DECISION
    # =================================

    def ai_decision(self, question):

        prompt = f"""
You are the research decision system of AKHIM AI.

Decide whether this question requires web research.

Return ONLY one word:

DIRECT

or

RESEARCH

Use RESEARCH when the answer depends on:

- current information
- latest information
- today's information
- recent news
- current public figures
- current events
- changing prices
- weather
- live information
- information that may have changed recently

Use DIRECT for:

- greetings
- casual conversation
- general knowledge
- simple explanations
- stable facts
- basic definitions
- personal conversation

QUESTION:

{question}
"""

        try:

            result = self.ai.ask(
                prompt
            )

            if not result:
                return "DIRECT"

            result = result.strip().upper()

            if "RESEARCH" in result:
                return "RESEARCH"

            return "DIRECT"

        except Exception:

            return "DIRECT"


    # =================================
    # FINAL DECISION
    # =================================

    def needs_research(self, question):

        local = self.local_decision(
            question
        )

        # Local decision first

        if local:

            return local == "RESEARCH"


        # AI decision for uncertain questions

        decision = self.ai_decision(
            question
        )

        return decision == "RESEARCH"