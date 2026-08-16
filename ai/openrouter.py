import requests


class OpenRouterAI:

    def __init__(self, api_keys):

        self.api_keys = api_keys
        self.current_key = 0

        self.url = (
            "https://openrouter.ai/api/v1/"
            "chat/completions"
        )


    def ask(self, question):

        if not self.api_keys:

            return None, (
                "No OpenRouter API keys configured."
            )


        attempts = len(self.api_keys)


        for _ in range(attempts):

            api_key = self.api_keys[
                self.current_key
            ]


            headers = {
                "Authorization": (
                    f"Bearer {api_key}"
                ),
                "Content-Type": (
                    "application/json"
                ),
                "X-Title": "AKHIM AI"
            }


            data = {

                "model": "openrouter/free",

                "messages": [
                    {
                        "role": "user",
                        "content": question
                    }
                ]

            }


            try:

                response = requests.post(
                    self.url,
                    headers=headers,
                    json=data,
                    timeout=60
                )


                # =========================
                # SUCCESS
                # =========================

                if response.status_code == 200:

                    result = response.json()


                    # Check response structure

                    if "choices" not in result:

                        return None, (
                            "OpenRouter Error: "
                            "No choices in response."
                        )


                    if not result["choices"]:

                        return None, (
                            "OpenRouter Error: "
                            "Empty choices."
                        )


                    message = (
                        result["choices"][0]
                        .get("message", {})
                    )


                    answer = message.get(
                        "content"
                    )


                    if not answer:

                        return None, (
                            "OpenRouter Error: "
                            "Empty response content."
                        )


                    return answer, None


                # =========================
                # KEY / QUOTA / RATE LIMIT
                # =========================

                if response.status_code in [
                    401,
                    403,
                    429
                ]:

                    print(
                        f"OpenRouter Key "
                        f"{self.current_key + 1} "
                        f"failed "
                        f"({response.status_code})"
                    )

                    self.next_key()

                    continue


                # =========================
                # OTHER ERROR
                # =========================

                return None, (
                    "OpenRouter Error "
                    f"{response.status_code}: "
                    f"{response.text}"
                )


            except requests.exceptions.RequestException as e:

                print(
                    f"OpenRouter Key "
                    f"{self.current_key + 1} "
                    "network error"
                )

                self.next_key()

                continue


            except Exception as e:

                print(
                    f"OpenRouter Key "
                    f"{self.current_key + 1} "
                    f"response error: {e}"
                )

                self.next_key()

                continue


        return None, (
            "OpenRouter Error 429: "
            "All OpenRouter API keys failed."
        )


    def next_key(self):

        self.current_key = (
            self.current_key + 1
        ) % len(self.api_keys)