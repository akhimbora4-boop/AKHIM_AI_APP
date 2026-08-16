import requests


class MistralAI:

    def __init__(self, api_keys):
        self.api_keys = api_keys
        self.current_key = 0

        self.url = "https://api.mistral.ai/v1/chat/completions"

    def ask(self, question):

        if not self.api_keys:
            return None, "No Mistral API keys configured."

        attempts = len(self.api_keys)

        for _ in range(attempts):

            api_key = self.api_keys[self.current_key]

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "mistral-small-latest",
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

                if response.status_code == 200:

                    result = response.json()

                    answer = (
                        result["choices"][0]
                        ["message"]["content"]
                    )

                    return answer, None

                print(
                    f"Mistral Key {self.current_key + 1} "
                    f"failed ({response.status_code})"
                )

                self.next_key()

            except requests.exceptions.RequestException:

                print("Mistral network error.")
                self.next_key()

            except Exception:

                print("Mistral response error.")
                self.next_key()

        return None, "Mistral Error 429: All Mistral API keys failed."

    def next_key(self):

        self.current_key = (
            self.current_key + 1
        ) % len(self.api_keys)