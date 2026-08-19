from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from threading import Thread
import os
import re

# ==========================================
# AKHIM AI CORE IMPORTS
# ==========================================
from ai.gemini import GeminiAI
from ai.groq import GroqAI
from ai.openrouter import OpenRouterAI
from ai.mistral import MistralAI
from ai.manager import AIManager
from correction.question_corrector import QuestionCorrector
from memory import Memory
from research.web_search import WebSearch
from research.analyzer import ResearchAnalyzer
from research.decision import ResearchDecision
from research.verifier import ResearchVerifier
from research.freshness import ResearchFreshness
from research.ranker import ResearchRanker
from config.settings import (
    GEMINI_API_KEYS, GROQ_API_KEYS, OPENROUTER_API_KEYS, MISTRAL_API_KEYS
)

# Initialize AI Providers
gemini = GeminiAI(GEMINI_API_KEYS)
groq = GroqAI(GROQ_API_KEYS)
openrouter = OpenRouterAI(OPENROUTER_API_KEYS)
mistral = MistralAI(MISTRAL_API_KEYS)

# Initialize Managers & Tools
ai = AIManager(gemini, groq, openrouter, mistral)
corrector = QuestionCorrector(ai)
memory = Memory()
search = WebSearch()
analyzer = ResearchAnalyzer(ai)
decision = ResearchDecision(ai)
verifier = ResearchVerifier()
freshness = ResearchFreshness()
ranker = ResearchRanker()

# ফণ্ট ফাইলৰ নাম
FONT_PATH = "assamese.ttf"

# AI য়ে দিয়া **text** আৰু ### Heading বোৰ সলনি কৰা ফাংচন
def convert_markdown_to_kivy(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'[b]\1[/b]', text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'[i]\1[/i]', text)
    text = re.sub(r'###\s*(.*)', r'[b][color=3498db]\1[/color][/b]', text)
    text = re.sub(r'##\s*(.*)', r'[b][color=3498db]\1[/color][/b]', text)
    text = re.sub(r'#\s*(.*)', r'[b][color=3498db]\1[/color][/b]', text)
    return text

# ==========================================
# CUSTOM CHAT INPUT (For Assamese Keyboard)
# ==========================================
class ChatInput(TextInput):
    def insert_text(self, substring, from_undo=False):
        # 'Enter' বুটাম টিপিলে মেছেজটো ছেণ্ড হ'ব
        if '\n' in substring:
            app = App.get_running_app()
            app.send_message(None)
            return
        super().insert_text(substring, from_undo=from_undo)


class AkhimAIApp(App):
    def build(self):
        Window.softinput_mode = "below_target"
        Window.clearcolor = (0.05, 0.05, 0.08, 1) 

        root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))

        header = Label(
            text="[b][color=3498db]⚡[/color] AKHIM AI[/b]", 
            markup=True, 
            font_size=dp(22), 
            size_hint_y=None, 
            height=dp(50),
            font_name=FONT_PATH
        )
        root.add_widget(header)

        self.scroll = ScrollView(size_hint=(1, 0.83))
        self.chat = Label(
            text="[b]নমস্কাৰ! মই AKHIM AI।[/b]\nআপোনাক কি সহায় কৰিব পাৰোঁ?\n\n",
            font_size=dp(16), markup=True, halign="left", valign="top",
            size_hint_y=None, padding=(dp(10), dp(10)),
            font_name=FONT_PATH
        )
        self.chat.bind(width=lambda *x: self.chat.setter('text_size')(self.chat, (self.chat.width - dp(20), None)))
        self.chat.bind(texture_size=self.chat.setter("size"))
        self.scroll.add_widget(self.chat)
        root.add_widget(self.scroll)

        bottom = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(8))
        
        # ইয়াত সাধাৰণ TextInput ৰ সলনি আমি বনোৱা ChatInput ব্যৱহাৰ কৰা হৈছে
        self.input_box = ChatInput(
            hint_text="Ask anything...", 
            multiline=True,  # multiline True থকাৰ বাবে কীবৰ্ডত অসমীয়া switch ওলাব
            font_size=dp(16),
            font_name=FONT_PATH,
            background_color=(0.15, 0.15, 0.18, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            padding=(dp(15), dp(15))
        )
        
        self.send_btn = Button(
            text="SEND", size_hint_x=None, width=dp(85), bold=True,
            background_color=(0.18, 0.8, 0.44, 1),
            color=(1, 1, 1, 1),
            font_name=FONT_PATH
        )
        self.send_btn.bind(on_press=self.send_message)

        bottom.add_widget(self.input_box)
        bottom.add_widget(self.send_btn)
        root.add_widget(bottom)

        return root

    def send_message(self, instance):
        question = self.input_box.text.strip()
        if not question: return

        self.input_box.text = ""
        self.input_box.disabled = True
        self.send_btn.disabled = True

        self.chat.text += f"\n[b][color=3498db]You:[/color][/b] {question}\n\n[i][color=e67e22]AKHIM AI is processing...[/color][/i]\n"
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.1)

        Thread(target=self.process_question, args=(question,), daemon=True).start()

    def process_question(self, question):
        try:
            if question.lower() in ["exit", "quit", "clear"]:
                if question.lower() == "clear":
                    memory.clear()
                    Clock.schedule_once(lambda dt: self.update_chat_final("History cleared."))
                else:
                    Clock.schedule_once(lambda dt: App.get_running_app().stop(), 1)
                return

            corrected_question = corrector.correct_question(question)
            memory.save("user", corrected_question)
            needs_research = decision.needs_research(corrected_question)
            answer = ""

            if needs_research:
                results = search.research(corrected_question, max_results=3)
                if results:
                    results = verifier.verify(results)
                    results = ranker.process(results)
                    answer = analyzer.analyze(corrected_question, results)

            if not answer:
                answer = corrector.correct_and_answer(f"Current question: {corrected_question}")

            memory.save("assistant", answer)
            
            formatted_answer = convert_markdown_to_kivy(answer)
            Clock.schedule_once(lambda dt: self.update_chat_final(formatted_answer))

        except Exception as error:
            Clock.schedule_once(lambda dt: self.update_chat_final(f"Error: {str(error)}"))

    def update_chat_final(self, answer):
        current = self.chat.text
        loading_text = "\n[i][color=e67e22]AKHIM AI is processing...[/color][/i]\n"
        if loading_text in current: 
            current = current.replace(loading_text, "")

        self.chat.text = current + f"\n[b][color=2ecc71]AKHIM AI:[/color][/b]\n{answer}\n\n"
        
        self.input_box.disabled = False
        self.send_btn.disabled = False
        self.input_box.focus = True
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.1)


if __name__ == "__main__":
    AkhimAIApp().run()
