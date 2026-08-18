import time


class AIManager:

    def __init__(
        self,
        gemini,
        groq,
        openrouter,
        mistral
    ):

        self.providers = [
            ("Gemini", gemini),
            ("Groq", groq),
            ("OpenRouter", openrouter),
            ("Mistral", mistral)
        ]

        # Provider cooldown time
        self.cooldown = {
            "Gemini": 0,
            "Groq": 0,
            "OpenRouter": 0,
            "Mistral": 0
        }

        # How long to skip a provider after
        # quota / rate-limit failure
        self.cooldown_seconds = 300


    # =================================
    # ASK AI
    # =================================

    def ask(self, question):

        for name, provider in self.providers:

            # ---------------------------------
            # CHECK COOLDOWN
            # ---------------------------------

            if time.time() < self.cooldown[name]:

                print(
                    f"[{name} temporarily skipped]"
                )

                continue


            print(
                f"[Trying {name}...]"
            )


            try:

                result = provider.ask(
                    question
                )


                # =================================
                # PROVIDERS RETURNING (answer, error)
                # =================================

                if isinstance(result, tuple):

                    answer, error = result

                    if answer:

                        print(
                            f"[Using {name}]"
                        )

                        return answer


                    error_text = (
                        str(error)
                        if error
                        else ""
                    )

                    print(
                        f"[{name} failed]"
                    )


                    # Rate limit / quota
                    if self.is_rate_limit(
                        error_text
                    ):

                        self.set_cooldown(
                            name
                        )

                    continue


                # =================================
                # PROVIDERS RETURNING STRING
                # =================================

                if isinstance(result, str):

                    if self.is_error(result):

                        print(
                            f"[{name} failed]"
                        )


                        if self.is_rate_limit(
                            result
                        ):

                            self.set_cooldown(
                                name
                            )

                        continue


                    print(
                        f"[Using {name}]"
                    )

                    return result


            except Exception as error:

                error_text = str(error)

                print(
                    f"[{name} failed: {error}]"
                )


                if self.is_rate_limit(
                    error_text
                ):

                    self.set_cooldown(
                        name
                    )

                continue


        return (
            "Sorry, all AI providers are "
            "currently unavailable."
        )


    # =================================
    # SET COOLDOWN
    # =================================

    def set_cooldown(self, name):

        self.cooldown[name] = (
            time.time()
            + self.cooldown_seconds
        )

        print(
            f"[{name} cooldown: "
            f"{self.cooldown_seconds // 60} minutes]"
        )


    # =================================
    # RATE LIMIT DETECTION
    # =================================

    def is_rate_limit(self, text):

        if not text:
            return False

        text = str(text).lower()

        rate_words = [
            "429",
            "rate limit",
            "rate_limit",
            "quota",
            "too many requests",
            "resource exhausted",
            "exceeded"
        ]

        for word in rate_words:

            if word in text:

                return True

        return False


    # =================================
    # GENERAL ERROR DETECTION
    # =================================

    def is_error(self, text):

        if not text:
            return True

        error_words = [

            "Gemini Error",
            "Groq Error",
            "OpenRouter Error",
            "Mistral Error",

            "Network Error",
            "Network error",

            "Response Error",
            "Response error",

            "API key not valid",
            "INVALID_ARGUMENT",
            "API_KEY_INVALID",

            "429",
            "rate limit",
            "rate_limit",
            "quota",
            "Too Many Requests",
            "RESOURCE_EXHAUSTED"
        ]

        for word in error_words:

            if word.lower() in text.lower():

                return True

        return False
