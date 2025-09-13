# models/chat_model.py
import requests
import json
import os

class ChatModel:
    @staticmethod
    def send_message(user_message):
        api_key = os.getenv("OPENROUTER_API_KEY", "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")
        if not api_key or api_key.startswith("<"):
            return {"error": "Falta API Key. Configura OPENROUTER_API_KEY en variables de entorno."}

        url = "https://openrouter.ai/api/v1/chat/completions"  # Sin espacios al final
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",  # Cambia si es necesario
            "X-Title": "Mi Chat Flask"
        }
        data = {
            "model": "deepseek/deepseek-r1:free",
            "messages": [
                {"role": "user", "content": user_message}
            ]
        }

        try:
            response = requests.post(
                url=url,
                headers=headers,
                data=json.dumps(data)
            )
            response.raise_for_status()
            result = response.json()
            return {
                "response": result["choices"][0]["message"]["content"]
            }
        except requests.exceptions.RequestException as e:
            return {"error": f"Error en la API: {str(e)}"}
        except KeyError:
            return {"error": "Respuesta inesperada de la API."}