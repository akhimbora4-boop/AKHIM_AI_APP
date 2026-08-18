import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window

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

# =================================
# AI PROVIDERS & SETUP
# =================================

gemini = GeminiAI(GEMINI_API_KEYS)
groq = GroqAI(GROQ_API_KEYS)
openrouter = OpenRouterAI(OPENROUTER_API_KEYS)
mistral = MistralAI(MISTRAL_API_KEYS)

ai = AIManager(gemini, groq, openrouter, mistral)
corrector = QuestionCorrector(ai)
memory = Memory()
search = WebSearch()
analyzer = ResearchAnalyzer(ai)
decision = ResearchDecision(ai)
verifier = ResearchVerifier()
freshness = ResearchFreshness()
ranker = ResearchRanker()


# =================================
# KIVY APP CLASS
# =================================

class AkhimAIApp(App):
    def build(self):
        # কীবৰ্ড ওলালে স্ক্ৰীণখন ওপৰলৈ উঠিবলৈ
        Window.softinput_mode = "below_target"
        
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Chat History Screen
        self.scroll = ScrollView(size_hint=(1, 0.88))
        welcome_text = (
            "[b]================================[/b]\n"
            "[b]        AKHIM AI[/b]\n"
            "[b]================================[/b]\n"
            "Gemini + Groq + OpenRouter + Mistral\n"
            "Web Research + AI Analysis\n"
            "Type 'exit' to stop.\n"
            "Type 'clear' to delete memory.\n\n"
        )
        self.chat_label = Label(
            text=welcome_text,
            size_hint_y=None, 
            markup=True,
            halign="left",
            valign="top"
        )
        self.chat_label.bind(width=lambda *x: self.chat_label.setter('text_size')(self.chat_label, (self.chat_label.width, None)))
        self.chat_label.bind(texture_size=self.chat_label.setter('size'))
        self.scroll.add_widget(self.chat_label)
        self.layout.add_widget(self.scroll)

        # Input Area (Text Box & Send Button)
        self.input_layout = BoxLayout(size_hint=(1, 0.12), spacing=10)
        self.text_input = TextInput(hint_text="Ask AKHIM...", multiline=False)
        self.text_input.bind(on_text_validate=self.send_message) # Enter টিপিলেও মেছেজ যাব
        
        self.send_button = Button(text="Send", size_hint=(0.25, 1))
        self.send_button.bind(on_press=self.send_message)

        self.input_layout.add_widget(self.text_input)
        self.input_layout.add_widget(self.send_button)
        self.layout.add_widget(self.input_layout)

        return self.layout

    def send_message(self, instance):
        question = self.text_input.text.strip()
        if not question:
            return

        self.update_chat(f"\n[b]You:[/b] {question}")
        self.text_input.text = ""

        # AI-য়ে চিন্তা কৰি থাকোঁতে বুটাম আৰু বক্সটো বন্ধ কৰি ৰাখিব
        self.text_input.disabled = True
        self.send_button.disabled = True

        # AI প্ৰক্ৰিয়াটো Background Thread ত চলাব
        threading.Thread(target=self.process_ai, args=(question,)).start()

    def update_chat(self, text):
        self.chat_label.text += text
        self.scroll.scroll_y = 0

    def log_status(self, text):
        # AI-ৰ Status বোৰ (যেনে Search, Verify) সৰুকৈ দেখুৱাব
        Clock.schedule_once(lambda dt: self.update_chat(f"\n[i][color=aaaaaa]{text}[/color][/i]"))

    def enable_input(self):
        def _enable(dt):
            self.text_input.disabled = False
            self.send_button.disabled = False
        Clock.schedule_once(_enable)

    def process_ai(self, question):
        # =================================
        # EXIT
        # =================================
        if question.lower() in ["exit", "quit"]:
            Clock.schedule_once(lambda dt: self.update_chat("\n[b]AKHIM AI:[/b] Goodbye!\n"))
            Clock.schedule_once(lambda dt: App.get_running_app().stop(), 2)
            return

        # =================================
        # CLEAR MEMORY
        # =================================
        if question.lower() == "clear":
            try:
                memory.clear()
                Clock.schedule_once(lambda dt: self.update_chat("\n[b]AKHIM AI:[/b] Memory cleared.\n"))
            except Exception as error:
                self.log_status(f"[Memory clear failed: {error}]")
            self.enable_input()
            return

        # =================================
        # QUESTION CORRECTION
        # =================================
        try:
            corrected_question = corrector.correct_question(question)
        except Exception as error:
            self.log_status(f"[Question correction failed: {error}]")
            corrected_question = question

        if not corrected_question:
            corrected_question = question

        if corrected_question.strip().lower() != question.strip().lower():
            self.log_status(f"[Corrected: {corrected_question}]")

        # =================================
        # SAVE QUESTION
        # =================================
        try:
            memory.save("user", corrected_question)
        except Exception as error:
            self.log_status(f"[Memory save failed: {error}]")

        # =================================
        # HISTORY
        # =================================
        try:
            history = memory.get_recent(20)
        except Exception:
            history = []

        context = ""
        for role, message in history:
            if role == "user":
                context += "User: " + message + "\n"
            else:
                context += "AKHIM AI: " + message + "\n"

        # =================================
        # RESEARCH DECISION
        # =================================
        try:
            needs_research = decision.needs_research(corrected_question)
        except Exception as error:
            self.log_status(f"[Research decision failed: {error}]")
            needs_research = False

        answer = ""

        # =================================
        # WEB RESEARCH
        # =================================
        if needs_research:
            self.log_status("[Research required]")
            self.log_status("[Searching web...]")

            try:
                results = search.research(corrected_question, max_results=5)
            except Exception as error:
                self.log_status(f"[Search failed: {error}]")
                results = []

            if results:
                self.log_status(f"[Found {len(results)} sources]")
                self.log_status("[Verifying sources...]")

                try:
                    results = verifier.verify(results)
                    confirmed = 0
                    reported = 0
                    uncertain = 0
                    for result in results:
                        status = str(result.get("status", "UNCERTAIN")).upper()
                        if status == "CONFIRMED":
                            confirmed += 1
                        elif status == "REPORTED":
                            reported += 1
                        else:
                            uncertain += 1
                    self.log_status(f"[Verification: Confirmed={confirmed}, Reported={reported}, Uncertain={uncertain}]")
                except Exception as error:
                    self.log_status(f"[Verification failed: {error}]")

                self.log_status("[Checking freshness...]")
                try:
                    results = freshness.enrich(results)
                    results = freshness.filter_current(results)
                    results = freshness.sort(results)
                    today_count = 0
                    recent_count = 0
                    unknown_count = 0
                    for result in results:
                        fresh_status = str(result.get("freshness", "UNKNOWN")).upper()
                        if fresh_status == "TODAY":
                            today_count += 1
                        elif fresh_status == "RECENT":
                            recent_count += 1
                        else:
                            unknown_count += 1
                    self.log_status(f"[Freshness: Today={today_count}, Recent={recent_count}, Unknown={unknown_count}]")
                except Exception as error:
                    self.log_status(f"[Freshness check failed: {error}]")

                self.log_status("[Ranking sources...]")
                try:
                    results = ranker.process(results)
                    self.log_status(f"[Ranking complete: {len(results)} sources]")
                except Exception as error:
                    self.log_status(f"[Ranking failed: {error}]")

                results = results[:7]

                self.log_status("[Analyzing sources...]")
                try:
                    answer = analyzer.analyze(corrected_question, results)
                except Exception as error:
                    self.log_status(f"[Research analysis failed: {error}]")
                    answer = ""
            else:
                self.log_status("[No web sources found]")

        # =================================
        # DIRECT AI FALLBACK
        # =================================
        if not answer:
            try:
                answer = corrector.correct_and_answer(context + "\nCurrent question: " + corrected_question)
            except Exception as error:
                self.log_status(f"[AI answer failed: {error}]")
                answer = "I could not generate an answer."

        # =================================
        # SAVE ANSWER
        # =================================
        try:
            memory.save("assistant", answer)
        except Exception as error:
            self.log_status(f"[Memory save failed: {error}]")

        # =================================
        # FINAL ANSWER DISPLAY
        # =================================
        Clock.schedule_once(lambda dt: self.update_chat(f"\n\n[b]AKHIM AI:[/b]\n{answer}\n"))
        self.enable_input()


if __name__ == '__main__':
    AkhimAIApp().run()
