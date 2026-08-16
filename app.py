from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.metrics import dp
from threading import Thread


# ==========================================
# AKHIM AI CORE
# ==========================================

from ai.gemini import GeminiAI
from ai.groq import GroqAI
from ai.openrouter import OpenRouterAI
from ai.mistral import MistralAI

from ai.manager import AIManager

from config.settings import (
    GEMINI_API_KEYS,
    GROQ_API_KEYS,
    OPENROUTER_API_KEYS,
    MISTRAL_API_KEYS
)

from correction.question_corrector import QuestionCorrector
from memory import Memory

from research.web_search import WebSearch
from research.analyzer import ResearchAnalyzer
from research.decision import ResearchDecision
from research.verifier import ResearchVerifier
from research.freshness import ResearchFreshness
from research.ranker import ResearchRanker


# ==========================================
# CREATE AKHIM AI CORE
# ==========================================

gemini = GeminiAI(GEMINI_API_KEYS)
groq = GroqAI(GROQ_API_KEYS)
openrouter = OpenRouterAI(OPENROUTER_API_KEYS)
mistral = MistralAI(MISTRAL_API_KEYS)

ai = AIManager(
    gemini,
    groq,
    openrouter,
    mistral
)

corrector = QuestionCorrector(ai)

memory = Memory()

search = WebSearch()

analyzer = ResearchAnalyzer(ai)

decision = ResearchDecision(ai)

verifier = ResearchVerifier()

freshness = ResearchFreshness()

ranker = ResearchRanker()


# ==========================================
# AKHIM AI APPLICATION
# ==========================================

class AkhimAIApp(App):

    def build(self):

        root = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8)
        )

        # ==================================
        # HEADER
        # ==================================

        header = Label(
            text="AKHIM AI",
            font_size=dp(27),
            size_hint_y=None,
            height=dp(55)
        )

        root.add_widget(header)

        # ==================================
        # CHAT AREA
        # ==================================

        scroll = ScrollView()

        self.chat = Label(
            text=(
                "AKHIM AI\n\n"
                "Web Research + AI Analysis\n\n"
                "Ask me anything..."
            ),
            font_size=dp(16),
            halign="left",
            valign="top",
            size_hint_y=None,
            padding=(dp(8), dp(8))
        )

        self.chat.bind(
            texture_size=self.chat.setter("size")
        )

        scroll.add_widget(self.chat)

        root.add_widget(scroll)

        # ==================================
        # INPUT AREA
        # ==================================

        bottom = BoxLayout(
            size_hint_y=None,
            height=dp(55),
            spacing=dp(6)
        )

        self.input_box = TextInput(
            hint_text="Ask AKHIM AI...",
            multiline=False,
            font_size=dp(16)
        )

        self.input_box.bind(
            on_text_validate=self.send_message
        )

        send = Button(
            text="SEND",
            size_hint_x=None,
            width=dp(85)
        )

        send.bind(
            on_press=self.send_message
        )

        bottom.add_widget(self.input_box)
        bottom.add_widget(send)

        root.add_widget(bottom)

        return root

    # ==========================================
    # SEND MESSAGE
    # ==========================================

    def send_message(self, instance):

        question = self.input_box.text.strip()

        if not question:
            return

        self.input_box.text = ""

        self.chat.text += (
            "\n\nYou:\n"
            + question
            + "\n\nAKHIM AI:\n"
            + "Thinking..."
        )

        Thread(
            target=self.process_question,
            args=(question,),
            daemon=True
        ).start()

    # ==========================================
    # PROCESS QUESTION
    # ==========================================

    def process_question(self, question):

        try:

            # ==================================
            # QUESTION CORRECTION
            # ==================================

            try:

                corrected_question = (
                    corrector.correct_question(
                        question
                    )
                )

            except Exception:

                corrected_question = question

            if not corrected_question:
                corrected_question = question

            # ==================================
            # SAVE QUESTION
            # ==================================

            try:

                memory.save(
                    "user",
                    corrected_question
                )

            except Exception:
                pass

            # ==================================
            # HISTORY
            # ==================================

            try:

                history = memory.get_recent(20)

            except Exception:

                history = []

            context = ""

            for role, message in history:

                if role == "user":

                    context += (
                        "User: "
                        + message
                        + "\n"
                    )

                else:

                    context += (
                        "AKHIM AI: "
                        + message
                        + "\n"
                    )

            # ==================================
            # RESEARCH DECISION
            # ==================================

            try:

                needs_research = (
                    decision.needs_research(
                        corrected_question
                    )
                )

            except Exception:

                needs_research = False

            answer = ""

            # ==================================
            # WEB RESEARCH
            # ==================================

            if needs_research:

                try:

                    results = search.research(
                        corrected_question,
                        max_results=5
                    )

                except Exception:

                    results = []

                if results:

                    # Verification
                    try:

                        results = verifier.verify(
                            results
                        )

                    except Exception:

                        pass

                    # Freshness
                    try:

                        results = freshness.enrich(
                            results
                        )

                        results = (
                            freshness.filter_current(
                                results
                            )
                        )

                        results = freshness.sort(
                            results
                        )

                    except Exception:

                        pass

                    # Ranking
                    try:

                        results = ranker.process(
                            results
                        )

                    except Exception:

                        pass

                    results = results[:7]

                    # Analysis
                    try:

                        answer = analyzer.analyze(
                            corrected_question,
                            results
                        )

                    except Exception:

                        answer = ""

            # ==================================
            # DIRECT AI FALLBACK
            # ==================================

            if not answer:

                try:

                    answer = (
                        corrector.correct_and_answer(
                            context
                            + "\nCurrent question: "
                            + corrected_question
                        )
                    )

                except Exception:

                    answer = (
                        "I could not generate "
                        "an answer."
                    )

            # ==================================
            # SAVE ANSWER
            # ==================================

            try:

                memory.save(
                    "assistant",
                    answer
                )

            except Exception:

                pass

            # ==================================
            # UPDATE UI
            # ==================================

            Clock.schedule_once(
                lambda dt: self.show_answer(
                    answer
                )
            )

        except Exception as error:

            Clock.schedule_once(
                lambda dt: self.show_answer(
                    "Error: " + str(error)
                )
            )

    # ==========================================
    # SHOW ANSWER
    # ==========================================

    def show_answer(self, answer):

        current = self.chat.text

        if current.endswith("Thinking..."):

            current = current[:-10]

        self.chat.text = (
            current
            + answer
        )

        self.chat.texture_update()


# ==========================================
# START APP
# ==========================================

if __name__ == "__main__":

    AkhimAIApp().run()
