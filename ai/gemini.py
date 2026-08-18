import requests


class GeminiAI:

    def __init__(self, api_keys):
        self.api_keys = api_keys
        self.current_key = 0

        self.url = (
            "https://generativelanguage.googleapis.com/"
            "v1beta/models/gemini-3.6-flash:generateContent"
        )

    def ask(self, question):

        attempts = len(self.api_keys)

        for _ in range(attempts):

            api_key = self.api_keys[self.current_key]

            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": api_key
            }

            data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": question
                            }
                        ]
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

                # Success
                if response.status_code == 200:

                    result = response.json()

                    answer = (
                        result["candidates"][0]
                        ["content"]["parts"][0]["text"]
                    )

                    return answer

                # Rate limit / quota / auth / unavailable
                if response.status_code in [401, 403, 404, 429]:

                    print(
                        f"Gemini Key {self.current_key + 1} "
                        f"failed ({response.status_code})"
                    )

                    self.next_key()
                    continue

                return f"Gemini Error {response.status_code}: {response.text}"

            except requests.exceptions.RequestException as e:

                print(
                    f"Gemini Key {self.current_key + 1} "
                    "network error"
                )

                self.next_key()

        return "Gemini Error 429: All Gemini API keys failed."

    def next_key(self):

        self.current_key = (
            self.current_key + 1
        ) % len(self.api_keys)
