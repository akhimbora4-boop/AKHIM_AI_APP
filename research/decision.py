class ResearchDecision:

    def __init__(self, ai_manager):
        self.ai = ai_manager

    def local_decision(self, question):

        q = question.lower().strip()

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

        if q in direct_words:
            return "DIRECT"

        direct_assamese = [
            "তোমাৰ নাম কি",
            "আপোনাৰ নাম কি",
            "তুমি কেনে আছা",
            "আপুনি কেনে আছে",
            "ধন্যবাদ",
            "নমস্কাৰ"
        ]

        if q in direct_assamese:
            return "DIRECT"

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

        return "DIRECT"

    def needs_research(self, question):

        decision = self.local_decision(
            question
        )

        return decision == "RESEARCH"
