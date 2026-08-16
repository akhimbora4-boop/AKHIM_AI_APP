import re


class QuestionCorrector:

    def __init__(self, ai_manager):
        self.ai = ai_manager


    # =================================
    # LOCAL QUESTION CORRECTION
    # =================================

    def local_correction(self, question):

        text = question.strip()

        if not text:
            return text


        # ---------------------------------
        # Remove repeated letters
        # ---------------------------------

        text = re.sub(
            r'(.)\1{2,}',
            r'\1',
            text
        )


        # ---------------------------------
        # Common English typing mistakes
        # ---------------------------------

        replacements = {

            "whhat": "what",
            "wht": "what",

            "isn": "is",
            "iss": "is",

            "aer": "are",
            "ar": "are",

            "yur": "your",
            "ur": "your",

            "namme": "name",
            "namee": "name",
            "nmae": "name",

            "hw": "how",

            "hte": "the",
            "teh": "the",

            "yo": "you",
            "u": "you",

            "whts": "what",
            "whats": "what",

            "pleese": "please",
            "plese": "please",

            "thnks": "thanks",
            "thanx": "thanks",
        }


        words = text.split()

        corrected = []


        for word in words:

            punctuation = ""

            original_word = word

            # Separate punctuation
            if word and word[-1] in "?!.,":

                punctuation = word[-1]

                word = word[:-1]


            lower_word = word.lower()


            if lower_word in replacements:

                new_word = replacements[
                    lower_word
                ]

            else:

                new_word = word


            # Preserve first-letter capitalization
            if (
                original_word
                and original_word[0].isupper()
                and new_word
            ):

                new_word = (
                    new_word[0].upper()
                    + new_word[1:]
                )


            corrected.append(
                new_word + punctuation
            )


        text = " ".join(corrected)


        # ---------------------------------
        # Common phrase corrections
        # ---------------------------------

        phrase_corrections = {

            r"\bwhat is your name\b":
                "What is your name?",

            r"\bhow are your\b":
                "How are you?",

            r"\bhow are you\b":
                "How are you?",

            r"\bwhat are your name\b":
                "What is your name?",

        }


        for pattern, replacement in phrase_corrections.items():

            if re.fullmatch(
                pattern,
                text.strip(),
                flags=re.IGNORECASE
            ):

                text = replacement

                break


        # ---------------------------------
        # Fix repeated punctuation
        # ---------------------------------

        text = re.sub(
            r"\?+",
            "?",
            text
        )

        text = re.sub(
            r"!+",
            "!",
            text
        )

        text = re.sub(
            r"\.{2,}",
            ".",
            text
        )


        # ---------------------------------
        # Remove spaces before punctuation
        # ---------------------------------

        text = re.sub(
            r"\s+([?!.,])",
            r"\1",
            text
        )


        return text.strip()


    # =================================
    # CORRECT QUESTION
    # =================================

    def correct_question(self, question):

        if not question:
            return question

        corrected = self.local_correction(
            question
        )

        if not corrected:
            return question

        return corrected


    # =================================
    # DIRECT AI ANSWER
    # =================================

    def correct_and_answer(self, question):

        prompt = f"""
You are AKHIM AI, a helpful multilingual AI assistant.

LANGUAGE RULES:

1. If the user writes Assamese,
   answer in Assamese.

2. If the user writes English,
   answer in English.

3. If the user mixes Assamese and English,
   reply naturally in the same style.

The user's question may contain
spelling or typing mistakes.

Understand the intended meaning
and answer directly.

Do not criticize spelling mistakes.

Do not mention the correction.

Do not invent information.

USER QUESTION:

{question}

Give a clear and useful answer.
"""

        return self.ai.ask(prompt)