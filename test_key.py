import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=api_key)

print(f"Probando clave: {api_key[:10]}...")

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hola, responde con la palabra 'LISTO' si puedes leerme."
    )
    print(f"Respuesta de la IA: {response.text}")
except Exception as e:
    print(f"Error de diagnóstico: {e}")
