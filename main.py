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


print("================================")
print("        AKHIM AI")
print("================================")
print("Gemini + Groq + OpenRouter + Mistral")
print("Web Research + AI Analysis")
print("Type 'exit' to stop.")
print("Type 'clear' to delete memory.")
print()


# =================================
# AI PROVIDERS
# =================================

gemini = GeminiAI(
    GEMINI_API_KEYS
)

groq = GroqAI(
    GROQ_API_KEYS
)

openrouter = OpenRouterAI(
    OPENROUTER_API_KEYS
)

mistral = MistralAI(
    MISTRAL_API_KEYS
)


# =================================
# AI MANAGER
# =================================

ai = AIManager(
    gemini,
    groq,
    openrouter,
    mistral
)


# =================================
# QUESTION CORRECTOR
# =================================

corrector = QuestionCorrector(
    ai
)


# =================================
# MEMORY
# =================================

memory = Memory()


# =================================
# RESEARCH COMPONENTS
# =================================

search = WebSearch()

analyzer = ResearchAnalyzer(
    ai
)

decision = ResearchDecision(
    ai
)

verifier = ResearchVerifier()

freshness = ResearchFreshness()

ranker = ResearchRanker()


# =================================
# MAIN LOOP
# =================================

first_question = True


while True:

    if first_question:

        question = input(
            "Ask AKHIM: "
        ).strip()

        first_question = False

    else:

        question = input(
            "Reply AKHIM AI: "
        ).strip()


    if not question:
        continue


    # =================================
    # EXIT
    # =================================

    if question.lower() in [
        "exit",
        "quit"
    ]:

        print()
        print(
            "AKHIM AI: Goodbye!"
        )

        break


    # =================================
    # CLEAR MEMORY
    # =================================

    if question.lower() == "clear":

        try:

            memory.clear()

            print()
            print(
                "AKHIM AI: Memory cleared."
            )
            print()

        except Exception as error:

            print(
                "[Memory clear failed:",
                error,
                "]"
            )

        first_question = True

        continue


    # =================================
    # QUESTION CORRECTION
    # =================================

    try:

        corrected_question = (
            corrector.correct_question(
                question
            )
        )

    except Exception as error:

        print(
            "[Question correction failed:",
            error,
            "]"
        )

        corrected_question = question


    if not corrected_question:

        corrected_question = question


    if (
        corrected_question.strip().lower()
        != question.strip().lower()
    ):

        print()

        print(
            "[Corrected:",
            corrected_question,
            "]"
        )


    # =================================
    # SAVE QUESTION
    # =================================

    try:

        memory.save(
            "user",
            corrected_question
        )

    except Exception as error:

        print(
            "[Memory save failed:",
            error,
            "]"
        )


    # =================================
    # HISTORY
    # =================================

    try:

        history = memory.get_recent(
            20
        )

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


    # =================================
    # RESEARCH DECISION
    # =================================

    print()

    try:

        needs_research = (
            decision.needs_research(
                corrected_question
            )
        )

    except Exception as error:

        print(
            "[Research decision failed:",
            error,
            "]"
        )

        needs_research = False


    answer = ""


    # =================================
    # WEB RESEARCH
    # =================================

    if needs_research:

        print(
            "[Research required]"
        )

        print(
            "[Searching web...]"
        )


        # =================================
        # SEARCH
        # =================================

        try:

            results = search.research(
                corrected_question,
                max_results=5
            )

        except Exception as error:

            print(
                "[Search failed:",
                error,
                "]"
            )

            results = []


        # =================================
        # SOURCES FOUND
        # =================================

        if results:

            print(
                f"[Found {len(results)} sources]"
            )


            # =================================
            # VERIFICATION
            # =================================

            print(
                "[Verifying sources...]"
            )

            try:

                results = verifier.verify(
                    results
                )

                confirmed = 0
                reported = 0
                uncertain = 0

                for result in results:

                    status = str(
                        result.get(
                            "status",
                            "UNCERTAIN"
                        )
                    ).upper()

                    if status == "CONFIRMED":

                        confirmed += 1

                    elif status == "REPORTED":

                        reported += 1

                    else:

                        uncertain += 1


                print(
                    "[Verification:",
                    f"Confirmed={confirmed},",
                    f"Reported={reported},",
                    f"Uncertain={uncertain}",
                    "]"
                )

            except Exception as error:

                print(
                    "[Verification failed:",
                    error,
                    "]"
                )


            # =================================
            # FRESHNESS
            # =================================

            print(
                "[Checking freshness...]"
            )

            try:

                results = freshness.enrich(
                    results
                )

                results = freshness.filter_current(
                    results
                )

                results = freshness.sort(
                    results
                )

                today_count = 0
                recent_count = 0
                unknown_count = 0

                for result in results:

                    fresh_status = str(
                        result.get(
                            "freshness",
                            "UNKNOWN"
                        )
                    ).upper()

                    if fresh_status == "TODAY":

                        today_count += 1

                    elif fresh_status == "RECENT":

                        recent_count += 1

                    else:

                        unknown_count += 1


                print(
                    "[Freshness:",
                    f"Today={today_count},",
                    f"Recent={recent_count},",
                    f"Unknown={unknown_count}",
                    "]"
                )

            except Exception as error:

                print(
                    "[Freshness check failed:",
                    error,
                    "]"
                )


            # =================================
            # RANKING
            # =================================

            print(
                "[Ranking sources...]"
            )

            try:

                results = ranker.process(
                    results
                )

                print(
                    "[Ranking complete:",
                    len(results),
                    "sources]"
                )

            except Exception as error:

                print(
                    "[Ranking failed:",
                    error,
                    "]"
                )


            # =================================
            # LIMIT
            # =================================

            results = results[:7]


            # =================================
            # ANALYSIS
            # =================================

            print(
                "[Analyzing sources...]"
            )

            try:

                answer = analyzer.analyze(
                    corrected_question,
                    results
                )

            except Exception as error:

                print(
                    "[Research analysis failed:",
                    error,
                    "]"
                )

                answer = ""


        else:

            print(
                "[No web sources found]"
            )


    # =================================
    # DIRECT AI FALLBACK
    # =================================

    if not answer:

        try:

            answer = (
                corrector.correct_and_answer(
                    context
                    + "\nCurrent question: "
                    + corrected_question
                )
            )

        except Exception as error:

            print(
                "[AI answer failed:",
                error,
                "]"
            )

            answer = (
                "I could not generate an answer."
            )


    # =================================
    # FINAL ANSWER
    # =================================

    print()

    print(
        "AKHIM AI:"
    )

    print(
        answer
    )

    print()


    # =================================
    # SAVE ANSWER
    # =================================

    try:

        memory.save(
            "assistant",
            answer
        )

    except Exception as error:

        print(
            "[Memory save failed:",
            error,
            "]"
        )

    print()