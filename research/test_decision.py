import re

class ResearchDecision:
    def __init__(self, ai_manager):
        self.ai = ai_manager

    def local_decision(self, question):
        q = question.lower().strip()
        
        # ==========================================
        # ১. সাধাৰণ কথা-বতৰা (DIRECT - চাৰ্চ নকৰে)
        # ==========================================
        direct_matches = [
            "hi", "hello", "hey", "how are you", "what is your name", 
            "who are you", "who made you", "thanks", "thank you", "ok", 
            "okay", "bye", "হাই", "হেল্ল", "তোমাৰ নাম কি", "আপোনাৰ নাম কি", 
            "তুমি কেনে আছা", "আপুনি কেনে আছে", "ধন্যবাদ", "নমস্কাৰ"
        ]
        
        if q in direct_matches:
            return "DIRECT"

        # ==========================================
        # ২. সৃষ্টিশীল কাম (DIRECT - চাৰ্চ নকৰে)
        # ==========================================
        creative_words = [
            "write", "translate", "poem", "story", "essay", "code",
            "লিখা", "অনুবাদ", "কবিতা", "গল্প", "ৰচনা", "ক'ড"
        ]
        for word in creative_words:
            if word in q:
                return "DIRECT"

        # ==========================================
        # ৩. প্ৰশ্ন আৰু তথ্য (RESEARCH - ইন্টাৰনেটত চাৰ্চ কৰিব)
        # ==========================================
        research_words = [
            # ইংৰাজী শব্দ
            "current", "latest", "recent", "today", "news", "present",
            "update", "situation", "status", "who", "what", "where",
            "when", "why", "how", "tell", "explain", "history",
            "price", "weather", "details", "info", "about",
            
            # অসমীয়া শব্দ
            "বৰ্তমান", "আজিৰ", "শেহতীয়া", "সাম্প্ৰতিক", "খবৰ", "অৱস্থা",
            "কি", "কোন", "ক'ত", "কেতিয়া", "কিয়", "কেনেকৈ", "কেনেদৰে",
            "বিষয়ে", "ইতিহাস", "দাম", "বতৰ", "কিমান", "কাৰ", "তথ্য",
            "জনাওক", "বিৱৰণ"
        ]
        
        for word in research_words:
            if word in q:
                return "RESEARCH"

        # যদি ওপৰৰ এটাও নিয়ম নাখাটে, তেন্তে ডিফল্ট হিচাপে চাৰ্চ কৰিবলৈ পঠিয়াব
        # যাতে কোনো নজনা প্ৰশ্ন সুধিলেও AI-য়ে ইন্টাৰনেটৰ পৰা বিচাৰি উলিয়াব পাৰে।
        return "RESEARCH"

    def needs_research(self, question):
        return self.local_decision(question) == "RESEARCH"
