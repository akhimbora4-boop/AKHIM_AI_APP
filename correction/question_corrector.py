import re
import unicodedata


class QuestionCorrector:

    """
    AKHIM AI Question Corrector

    Responsibilities:
    - Clean user input
    - Fix common typing mistakes
    - Preserve Assamese text
    - Preserve English/Assamese mixed questions
    - Avoid aggressive/wrong corrections
    - Provide direct AI fallback answer
    """

    def __init__(self, ai_manager):

        self.ai = ai_manager

        # ==================================================
        # COMMON ENGLISH TYPING CORRECTIONS
        # ==================================================

        self.replacements = {

            # what
            "whhat": "what",
            "wht": "what",
            "whta": "what",
            "waht": "what",
            "whts": "what",
            "whats": "what",

            # how
            "hw": "how",
            "hwo": "how",
            "hwoa": "how",

            # where
            "wher": "where",
            "wheer": "where",

            # when
            "whn": "when",
            "wehn": "when",

            # why
            "wyh": "why",
            "whay": "why",

            # who
            "whho": "who",
            "wjo": "who",

            # is
            "iss": "is",
            "i s": "is",

            # are
            "aer": "are",
            "ar": "are",
            "rae": "are",

            # your
            "yur": "your",
            "yuo": "you",
            "yuor": "your",

            # you
            "yoou": "you",
            "yuo": "you",

            # the
            "hte": "the",
            "teh": "the",
            "tge": "the",

            # name
            "namme": "name",
            "namee": "name",
            "nmae": "name",

            # please
            "pleese": "please",
            "plese": "please",
            "pleas": "please",

            # thanks
            "thnks": "thanks",
            "thanx": "thanks",
            "thaks": "thanks",

            # because
            "becaus": "because",
            "becuse": "because",
            "becouse": "because",

            # about
            "abuot": "about",
            "abot": "about",

            # which
            "whcih": "which",
            "wich": "which",

            # with
            "wiht": "with",
            "wth": "with",

            # from
            "form": "from",

            # can
            "cna": "can",

            # have
            "haev": "have",
            "hvae": "have",

            # explain
            "explainn": "explain",
            "expalin": "explain",

            # information
            "infromation": "information",
            "informtion": "information",

            # current
            "curent": "current",
            "currnt": "current",

            # latest
            "latset": "latest",
            "lates": "latest",

            # search
            "seach": "search",
            "serach": "search",

            # answer
            "anwser": "answer",
            "anser": "answer",

            # help
            "hepl": "help",
            "hlep": "help",
        }


        # ==================================================
        # COMMON PHRASE CORRECTIONS
        # ==================================================

        self.phrase_corrections = [

            (
                r"\bwhat\s+are\s+your\s+name\b",
                "What is your name?"
            ),

            (
                r"\bwhat\s+is\s+your\s+name\b",
                "What is your name?"
            ),

            (
                r"\bhow\s+are\s+your\b",
                "How are you?"
            ),

            (
                r"\bhow\s+are\s+u\b",
                "How are you?"
            ),

            (
                r"\bwhat\s+is\s+u\b",
                "What is your name?"
            ),

        ]


        # ==================================================
        # WORDS THAT SHOULD NEVER BE AUTOMATICALLY CHANGED
        # ==================================================

        self.protected_words = {
            "ai",
            "api",
            "gemini",
            "groq",
            "mistral",
            "openrouter",
            "python",
            "kivy",
            "android",
            "buildozer",
            "github",
            "google",
            "openai",
            "assam",
            "assamese",
        }


    # ==================================================
    # NORMALIZE TEXT
    # ==================================================

    def normalize_text(self, text):

        if text is None:
            return ""

        text = str(text)

        # Unicode normalization
        text = unicodedata.normalize(
            "NFC",
            text
        )

        # Remove invisible control characters
        text = "".join(
            char
            for char in text
            if unicodedata.category(char) != "Cf"
            or char in "\n\t"
        )

        # Normalize spaces
        text = re.sub(
            r"[ \t]+",
            " ",
            text
        )

        # Remove excessive newlines
        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text
        )

        return text.strip()


    # ==================================================
    # REMOVE EXCESSIVE REPEATED CHARACTERS
    # ==================================================

    def fix_repeated_characters(self, text):

        if not text:
            return text

        # Only reduce 3+ repeated English characters.
        #
        # Example:
        # heyyy -> hey
        # whaaat -> what
        #
        # Assamese characters are intentionally
        # not aggressively modified.

        def replace(match):

            char = match.group(1)

            if char.isascii() and char.isalpha():

                return char

            return match.group(0)

        text = re.sub(
            r"([A-Za-z])\1{2,}",
            replace,
            text
        )

        return text


    # ==================================================
    # TOKENIZE ENGLISH WORDS SAFELY
    # ==================================================

    def correct_words(self, text):

        if not text:
            return text

        words = text.split()

        corrected = []

        for token in words:

            # Separate punctuation
            match = re.match(
                r"^([^\w]*)(.*?)([^\w]*)$",
                token,
                flags=re.UNICODE
            )

            if not match:

                corrected.append(token)

                continue

            prefix = match.group(1)
            word = match.group(2)
            suffix = match.group(3)

            if not word:

                corrected.append(token)

                continue

            lower_word = word.lower()

            # Never modify protected technical words
            if lower_word in self.protected_words:

                new_word = word

            elif lower_word in self.replacements:

                new_word = self.replacements[
                    lower_word
                ]

            else:

                new_word = word

            # Preserve capitalization
            if (
                word[:1].isupper()
                and new_word
            ):

                new_word = (
                    new_word[:1].upper()
                    + new_word[1:]
                )

            corrected.append(
                prefix
                + new_word
                + suffix
            )

        return " ".join(corrected)


    # ==================================================
    # PHRASE CORRECTION
    # ==================================================

    def correct_phrases(self, text):

        if not text:
            return text

        cleaned = text.strip()

        for pattern, replacement in self.phrase_corrections:

            if re.fullmatch(
                pattern,
                cleaned,
                flags=re.IGNORECASE
            ):

                return replacement

        return text


    # ==================================================
    # PUNCTUATION CLEANUP
    # ==================================================

    def fix_punctuation(self, text):

        if not text:
            return text

        # Remove spaces before punctuation
        text = re.sub(
            r"\s+([?!,.;:])",
            r"\1",
            text
        )

        # Keep question marks under control
        text = re.sub(
            r"\?{2,}",
            "?",
            text
        )

        # Keep exclamation marks under control
        text = re.sub(
            r"!{2,}",
            "!",
            text
        )

        # Keep dots under control
        text = re.sub(
            r"\.{3,}",
            "...",
            text
        )

        # Multiple spaces
        text = re.sub(
            r"[ \t]{2,}",
            " ",
            text
        )

        return text.strip()


    # ==================================================
    # LOCAL CORRECTION
    # ==================================================

    def local_correction(self, question):

        if question is None:
            return ""

        text = self.normalize_text(
            question
        )

        if not text:
            return ""

        # Maximum safety limit
        if len(text) > 10000:

            text = text[:10000].rstrip()

        # Character cleanup
        text = self.fix_repeated_characters(
            text
        )

        # Word correction
        text = self.correct_words(
            text
        )

        # Phrase correction
        text = self.correct_phrases(
            text
        )

        # Punctuation
        text = self.fix_punctuation(
            text
        )

        return text.strip()


    # ==================================================
    # CORRECT QUESTION
    # ==================================================

    def correct_question(self, question):

        if question is None:
            return ""

        original = self.normalize_text(
            question
        )

        if not original:
            return ""

        corrected = self.local_correction(
            original
        )

        if not corrected:
            return original

        return corrected


    # ==================================================
    # CHECK WHETHER CORRECTION WAS MADE
    # ==================================================

    def correction_changed(
        self,
        original,
        corrected
    ):

        if original is None:
            return False

        if corrected is None:
            return False

        return (
            self.normalize_text(original)
            != self.normalize_text(corrected)
        )


    # ==================================================
    # DIRECT AI ANSWER
    # ==================================================

    def correct_and_answer(self, question):

        if not question:

            return (
                "Please provide a question."
            )

        prompt = f"""
You are AKHIM AI, a reliable multilingual
AI assistant.

IMPORTANT LANGUAGE RULES:

1. If the user writes mainly Assamese,
   answer in Assamese.

2. If the user writes mainly English,
   answer in English.

3. If the user mixes Assamese and English,
   naturally use the same mixed style when appropriate.

4. Never criticize the user's spelling,
   grammar, typing or language.

5. Understand the user's intended meaning
   even when there are typing mistakes.

6. Do not mention that you corrected
   the user's question.

7. Do not invent facts.

8. If you are uncertain about a factual
   claim, clearly say that you are uncertain.

9. If the question requires current,
   recent, live or changing information,
   do not pretend that old knowledge is current.

10. Answer the user's actual question
    directly and clearly.

11. Do not unnecessarily repeat the question.

12. For technical questions, provide
    practical and accurate steps.

USER QUESTION:

{question}

Now answer the user.
"""

        try:

            result = self.ai.ask(
                prompt
            )

            if result is None:
                return ""

            return str(result).strip()

        except Exception as error:

            return (
                "I could not generate an answer "
                "right now."
            )