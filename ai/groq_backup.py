import requests


class GroqAI:

    def __init__(self, api_key):
        self.api_key = api_key

        self.url = "https://api.groq.com/openai/v1/chat/completions"

    def ask(self, question):

        headers = {
            "Authorization": f"Bearer {self.api_key}",
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

            if response.status_code != 200:
                return None, (
                    f"Groq Error {response.status_code}: "
                    f"{response.text}"
                )

            result = response.json()

            answer = result["choices"][0]["message"]["content"]

            return answer, None

        except requests.exceptions.RequestException as e:
            return None, f"Groq Network Error: {e}"

        except Exception as e:
            return None, f"Groq Response Error: {e}"