import os
import re
from threading import Thread, Lock

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.resources import resource_find

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput


# ============================================================
# AKHIM AI CORE
# ============================================================

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
from research.evidence import ResearchEvidence
from research.analyzer import ResearchAnalyzer
from research.decision import ResearchDecision
from research.verifier import ResearchVerifier
from research.freshness import ResearchFreshness
from research.ranker import ResearchRanker


# ============================================================
# INITIALIZE AI PROVIDERS
# ============================================================

gemini = GeminiAI(GEMINI_API_KEYS)
groq = GroqAI(GROQ_API_KEYS)
openrouter = OpenRouterAI(OPENROUTER_API_KEYS)
mistral = MistralAI(MISTRAL_API_KEYS)


# ============================================================
# INITIALIZE AI MANAGER
# ============================================================

ai = AIManager(
    gemini,
    groq,
    openrouter,
    mistral
)


# ============================================================
# INITIALIZE CORE COMPONENTS
# ============================================================

corrector = QuestionCorrector(ai)

memory = Memory()

search = WebSearch()

evidence = ResearchEvidence()

verifier = ResearchVerifier()

freshness = ResearchFreshness()

ranker = ResearchRanker()

analyzer = ResearchAnalyzer(ai)

decision = ResearchDecision(ai)


# ============================================================
# MOBILE FONT
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

FONT_PATH = os.path.join(
    BASE_DIR,
    "assamese.ttf"
)

if not os.path.isfile(FONT_PATH):
    found_font = resource_find("assamese.ttf")

    if found_font:
        FONT_PATH = found_font
    else:
        FONT_PATH = "Roboto"


# ============================================================
# TEXT HELPERS
# ============================================================

def safe_text(value):
    """
    Convert any value safely to string.
    """
    if value is None:
        return ""

    try:
        return str(value)
    except Exception:
        return ""


def escape_kivy_markup(text):
    """
    Escape characters that may accidentally break
    Kivy markup.

    We preserve our own generated markup separately.
    """

    text = safe_text(text)

    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")

    return text


def convert_markdown_to_kivy(text):
    """
    Convert common Markdown returned by AI
    into Kivy markup.

    Supports:
        **bold**
        *italic*
        # headings
        ## headings
        ### headings
        bullet points
        numbered lists
    """

    if not text:
        return ""

    text = safe_text(text)

    # --------------------------------------------------------
    # Normalize line endings
    # --------------------------------------------------------

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # --------------------------------------------------------
    # Escape HTML-like characters
    # --------------------------------------------------------

    text = escape_kivy_markup(text)

    # --------------------------------------------------------
    # Headings
    # --------------------------------------------------------

    text = re.sub(
        r"(?m)^###\s+(.+)$",
        r"[b][color=3498db]\1[/color][/b]",
        text
    )

    text = re.sub(
        r"(?m)^##\s+(.+)$",
        r"[b][color=3498db]\1[/color][/b]",
        text
    )

    text = re.sub(
        r"(?m)^#\s+(.+)$",
        r"[b][color=3498db]\1[/color][/b]",
        text
    )

    # --------------------------------------------------------
    # Bold
    # --------------------------------------------------------

    text = re.sub(
        r"\*\*(.+?)\*\*",
        r"[b]\1[/b]",
        text
    )

    # --------------------------------------------------------
    # Italic
    # --------------------------------------------------------

    text = re.sub(
        r"(?<!\*)\*([^*\n]+?)\*(?!\*)",
        r"[i]\1[/i]",
        text
    )

    # --------------------------------------------------------
    # Bullet points
    # --------------------------------------------------------

    text = re.sub(
        r"(?m)^\s*[-•]\s+",
        "• ",
        text
    )

    # --------------------------------------------------------
    # Horizontal rule
    # --------------------------------------------------------

    text = re.sub(
        r"(?m)^\s*[-_]{3,}\s*$",
        "────────────",
        text
    )

    return text.strip()


# ============================================================
# CUSTOM MOBILE CHAT INPUT
# ============================================================

class ChatInput(TextInput):

    def insert_text(
        self,
        substring,
        from_undo=False
    ):
        """
        Android keyboard Enter key:
        send message instead of inserting newline.
        """

        if "\n" in substring:

            app = App.get_running_app()

            if app is not None:
                app.send_message(None)

            return

        super().insert_text(
            substring,
            from_undo=from_undo
        )


# ============================================================
# AKHIM AI APPLICATION
# ============================================================

class AkhimAIApp(App):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        # ----------------------------------------------------
        # Prevent multiple simultaneous processing threads
        # ----------------------------------------------------

        self.processing_lock = Lock()

        self.is_processing = False

        self.message_counter = 0

    # ========================================================
    # BUILD UI
    # ========================================================

    def build(self):

        # ----------------------------------------------------
        # Android keyboard behavior
        # ----------------------------------------------------

        Window.softinput_mode = "below_target"

        # ----------------------------------------------------
        # Dark mobile background
        # ----------------------------------------------------

        Window.clearcolor = (
            0.05,
            0.05,
            0.08,
            1
        )

        # ----------------------------------------------------
        # ROOT
        # ----------------------------------------------------

        root = BoxLayout(
            orientation="vertical",
            padding=dp(8),
            spacing=dp(6)
        )

        # ====================================================
        # HEADER
        # ====================================================

        header = Label(
            text=(
                "[b]"
                "[color=3498db]⚡[/color] "
                "AKHIM AI"
                "[/b]"
            ),
            markup=True,
            font_name=FONT_PATH,
            font_size=dp(22),
            size_hint_y=None,
            height=dp(48),
            halign="center",
            valign="middle"
        )

        root.add_widget(header)

        # ====================================================
        # CHAT SCROLL
        # ====================================================

        self.scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True
        )

        # ----------------------------------------------------
        # Chat label
        # ----------------------------------------------------

        self.chat = Label(
            text=(
                "[b][color=3498db]"
                "নমস্কাৰ! মই AKHIM AI।"
                "[/color][/b]\n\n"
                "Web Research + AI Analysis\n"
                "আপোনাৰ প্ৰশ্ন সোধক।\n\n"
            ),
            markup=True,
            font_name=FONT_PATH,
            font_size=dp(16),
            halign="left",
            valign="top",
            size_hint_y=None,
            padding=(
                dp(10),
                dp(10)
            )
        )

        # ----------------------------------------------------
        # Responsive text width
        # ----------------------------------------------------

        self.chat.bind(
            width=self.update_chat_width
        )

        self.chat.bind(
            texture_size=self.chat.setter(
                "size"
            )
        )

        self.scroll.add_widget(
            self.chat
        )

        root.add_widget(
            self.scroll
        )

        # ====================================================
        # BOTTOM INPUT AREA
        # ====================================================

        bottom = BoxLayout(
            size_hint_y=None,
            height=dp(58),
            spacing=dp(7)
        )

        # ----------------------------------------------------
        # Input
        # ----------------------------------------------------

        self.input_box = ChatInput(
            hint_text="Ask anything...",
            multiline=True,
            font_name=FONT_PATH,
            font_size=dp(16),

            background_color=(
                0.14,
                0.14,
                0.18,
                1
            ),

            foreground_color=(
                1,
                1,
                1,
                1
            ),

            cursor_color=(
                1,
                1,
                1,
                1
            ),

            padding=(
                dp(12),
                dp(12)
            ),

            write_tab=False
        )

        # ----------------------------------------------------
        # Send button
        # ----------------------------------------------------

        self.send_btn = Button(
            text="SEND",
            size_hint_x=None,
            width=dp(82),

            bold=True,

            font_name=FONT_PATH,

            background_color=(
                0.18,
                0.80,
                0.44,
                1
            ),

            color=(
                1,
                1,
                1,
                1
            )
        )

        self.send_btn.bind(
            on_press=self.send_message
        )

        bottom.add_widget(
            self.input_box
        )

        bottom.add_widget(
            self.send_btn
        )

        root.add_widget(
            bottom
        )

        # ----------------------------------------------------
        # Focus input
        # ----------------------------------------------------

        Clock.schedule_once(
            lambda dt: self.focus_input(),
            0.3
        )

        return root

    # ========================================================
    # RESPONSIVE CHAT WIDTH
    # ========================================================

    def update_chat_width(
        self,
        instance,
        width
    ):

        instance.text_size = (
            max(
                0,
                width - dp(20)
            ),
            None
        )

    # ========================================================
    # FOCUS INPUT
    # ========================================================

    def focus_input(self):

        try:
            self.input_box.focus = True
        except Exception:
            pass

    # ========================================================
    # SCROLL TO BOTTOM
    # ========================================================

    def scroll_to_bottom(self):

        try:

            Clock.schedule_once(
                lambda dt: setattr(
                    self.scroll,
                    "scroll_y",
                    0
                ),
                0.05
            )

        except Exception:
            pass

    # ========================================================
    # SEND MESSAGE
    # ========================================================

    def send_message(self, instance):

        # ----------------------------------------------------
        # Prevent duplicate send
        # ----------------------------------------------------

        if self.is_processing:
            return

        question = safe_text(
            self.input_box.text
        ).strip()

        if not question:
            return

        # ----------------------------------------------------
        # Commands
        # ----------------------------------------------------

        command = question.lower().strip()

        if command == "clear":

            self.input_box.text = ""

            self.clear_history()

            return

        if command in (
            "exit",
            "quit"
        ):

            self.stop()

            return

        # ----------------------------------------------------
        # Lock processing
        # ----------------------------------------------------

        self.is_processing = True

        self.input_box.disabled = True
        self.send_btn.disabled = True

        # ----------------------------------------------------
        # Clear input
        # ----------------------------------------------------

        self.input_box.text = ""

        # ----------------------------------------------------
        # User message
        # ----------------------------------------------------

        user_text = escape_kivy_markup(
            question
        )

        self.chat.text += (
            "\n"
            "[b][color=3498db]"
            "You:"
            "[/color][/b]\n"
            + user_text
            + "\n\n"
        )

        # ----------------------------------------------------
        # Processing status
        # ----------------------------------------------------

        self.chat.text += (
            "[i][color=e67e22]"
            "AKHIM AI is processing..."
            "[/color][/i]\n"
        )

        self.scroll_to_bottom()

        # ----------------------------------------------------
        # Background thread
        # ----------------------------------------------------

        Thread(
            target=self.process_question,
            args=(question,),
            daemon=True
        ).start()

    # ========================================================
    # CLEAR HISTORY
    # ========================================================

    def clear_history(self):

        try:
            memory.clear()
        except Exception:
            pass

        self.chat.text = (
            "[b][color=3498db]"
            "AKHIM AI"
            "[/color][/b]\n\n"
            "History cleared.\n\n"
        )

        self.is_processing = False

        self.input_box.disabled = False
        self.send_btn.disabled = False

        self.focus_input()

    # ========================================================
    # GET MEMORY CONTEXT
    # ========================================================

    def get_memory_context(self):

        try:

            history = memory.get_recent(
                20
            )

        except Exception:

            history = []

        if not history:
            return ""

        context_parts = []

        for item in history:

            try:

                if isinstance(
                    item,
                    (tuple, list)
                ):

                    if len(item) >= 2:

                        role = safe_text(
                            item[0]
                        )

                        message = safe_text(
                            item[1]
                        )

                    else:
                        continue

                elif isinstance(
                    item,
                    dict
                ):

                    role = safe_text(
                        item.get("role", "")
                    )

                    message = safe_text(
                        item.get("message", "")
                    )

                else:

                    continue

                if not message:
                    continue

                if role == "user":

                    context_parts.append(
                        "User: "
                        + message
                    )

                else:

                    context_parts.append(
                        "AKHIM AI: "
                        + message
                    )

            except Exception:
                continue

        return "\n".join(
            context_parts
        )

    # ========================================================
    # SAFE CORRECTION
    # ========================================================

    def correct_question_safe(
        self,
        question
    ):

        try:

            corrected = (
                corrector.correct_question(
                    question
                )
            )

            if corrected:

                return safe_text(
                    corrected
                ).strip()

        except Exception:
            pass

        return question

    # ========================================================
    # RESEARCH PIPELINE
    # ========================================================

    def run_research(
        self,
        question
    ):

        try:

            results = search.research(
                question,
                max_results=7
            )

        except Exception:

            return []

        if not results:
            return []

        # ====================================================
        # EVIDENCE
        # ====================================================

        try:

            results = evidence.process(
                results
            )

        except Exception:
            pass

        if not results:
            return []

        # ====================================================
        # VERIFICATION
        # ====================================================

        try:

            results = verifier.verify(
                results
            )

        except Exception:
            pass

        # ====================================================
        # FRESHNESS
        # ====================================================

        try:

            results = freshness.process(
                results
            )

        except Exception:
            pass

        # ====================================================
        # RANKING
        # ====================================================

        try:

            results = ranker.process(
                results,
                max_results=7
            )

        except Exception:
            pass

        return results

    # ========================================================
    # DIRECT AI FALLBACK
    # ========================================================

    def direct_ai_answer(
        self,
        question,
        context
    ):

        prompt = ""

        if context:

            prompt += (
                "Conversation history:\n"
                + context
                + "\n\n"
            )

        prompt += (
            "Current question:\n"
            + question
        )

        try:

            answer = (
                corrector.correct_and_answer(
                    prompt
                )
            )

            if answer:

                return safe_text(
                    answer
                ).strip()

        except Exception:
            pass

        return ""

    # ========================================================
    # PROCESS QUESTION
    # ========================================================

    def process_question(
        self,
        question
    ):

        answer = ""

        try:

            # =================================================
            # CORRECT QUESTION
            # =================================================

            corrected_question = (
                self.correct_question_safe(
                    question
                )
            )

            # =================================================
            # MEMORY
            # =================================================

            try:

                memory.save(
                    "user",
                    corrected_question
                )

            except Exception:
                pass

            # =================================================
            # CONTEXT
            # =================================================

            context = (
                self.get_memory_context()
            )

            # =================================================
            # DECISION
            # =================================================

            try:

                needs_research = (
                    decision.needs_research(
                        corrected_question
                    )
                )

            except Exception:

                # Conservative fallback:
                # unknown questions should research
                needs_research = True

            # =================================================
            # RESEARCH
            # =================================================

            if needs_research:

                results = (
                    self.run_research(
                        corrected_question
                    )
                )

                # ---------------------------------------------
                # ANALYZER
                # ---------------------------------------------

                if results:

                    try:

                        answer = (
                            analyzer.analyze(
                                corrected_question,
                                results
                            )
                        )

                    except Exception:

                        answer = ""

            # =================================================
            # DIRECT AI FALLBACK
            # =================================================

            if not answer:

                answer = (
                    self.direct_ai_answer(
                        corrected_question,
                        context
                    )
                )

            # =================================================
            # FINAL FALLBACK
            # =================================================

            if not answer:

                answer = (
                    "Sorry, AKHIM AI could not "
                    "generate an answer right now."
                )

            # =================================================
            # SAVE ANSWER
            # =================================================

            try:

                memory.save(
                    "assistant",
                    answer
                )

            except Exception:
                pass

            # =================================================
            # FORMAT
            # =================================================

            formatted_answer = (
                convert_markdown_to_kivy(
                    answer
                )
            )

            # =================================================
            # UI UPDATE
            # =================================================

            Clock.schedule_once(
                lambda dt: self.update_chat_final(
                    formatted_answer
                )
            )

        except Exception as error:

            error_text = (
                "AKHIM AI error: "
                + safe_text(error)
            )

            formatted_error = (
                convert_markdown_to_kivy(
                    error_text
                )
            )

            Clock.schedule_once(
                lambda dt: self.update_chat_final(
                    formatted_error
                )
            )

    # ========================================================
    # UPDATE FINAL ANSWER
    # ========================================================

    def update_chat_final(
        self,
        answer
    ):

        try:

            current = safe_text(
                self.chat.text
            )

            loading_text = (
                "[i][color=e67e22]"
                "AKHIM AI is processing..."
                "[/color][/i]\n"
            )

            # ------------------------------------------------
            # Remove loading status
            # ------------------------------------------------

            if loading_text in current:

                current = current.replace(
                    loading_text,
                    ""
                )

            # ------------------------------------------------
            # Add answer
            # ------------------------------------------------

            self.chat.text = (
                current
                + "\n"
                + "[b][color=2ecc71]"
                "AKHIM AI:"
                "[/color][/b]\n"
                + safe_text(answer)
                + "\n\n"
            )

            self.chat.texture_update()

            # ------------------------------------------------
            # Unlock UI
            # ------------------------------------------------

            self.is_processing = False

            self.input_box.disabled = False
            self.send_btn.disabled = False

            self.input_box.focus = True

            self.scroll_to_bottom()

        except Exception:

            self.is_processing = False

            try:
                self.input_box.disabled = False
                self.send_btn.disabled = False
                self.input_box.focus = True
            except Exception:
                pass


# ============================================================
# START AKHIM AI
# ============================================================

if __name__ == "__main__":

    AkhimAIApp().run()