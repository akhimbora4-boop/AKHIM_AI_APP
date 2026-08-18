import requests


class GroqAI:

    def __init__(self, api_keys):

        self.api_keys = api_keys
        self.current_key = 0

        self.url = (
            "https://api.groq.com/openai/v1/"
            "chat/completions"
        )

    def ask(self, question):

        if not self.api_keys:
            return None, "No Groq API keys configured."

        attempts = len(self.api_keys)

        for _ in range(attempts):

            api_key = self.api_keys[self.current_key]

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                "temperature": 0.7
            }

            try:

                response = requests.post(
                    self.url,
                    headers=headers,
                    json=data,
                    timeout=60
                )

                # Success
                if response.status_code == 200:

                    result = response.json()

                    answer = (
                        result["choices"][0]
                        ["message"]["content"]
                    )

                    return answer, None

                # Key/quota/rate-limit related errors
                if response.status_code in [
                    401,
                    403,
                    429
                ]:

                    print(
                        f"Groq Key {self.current_key + 1} "
                        f"failed ({response.status_code})"
                    )

                    self.next_key()
                    continue

                return None, (
                    f"Groq Error {response.status_code}: "
                    f"{response.text}"
                )

            except requests.exceptions.RequestException as e:

                print(
                    f"Groq Key {self.current_key + 1} "
                    "network error"
                )

                self.next_key()

            except Exception as e:

                print(
                    f"Groq Key {self.current_key + 1} "
                    f"response error: {e}"
                )

                self.next_key()

        return None, "Groq Error 429: All Groq API keys failed."

    def next_key(self):

        self.current_key = (
            self.current_key + 1
        ) % len(self.api_keys)
