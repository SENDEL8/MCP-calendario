import os
import time
import pandas as pd
from datetime import datetime, timezone
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Importar las herramientas locales del servidor MCP
import mcp_server

# Cargar configuración
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# 1. Configurar el Cliente de Gemini
client = genai.Client(api_key=api_key)
# Usaremos 2.0-flash-lite que tiene mejores límites de cuota
MODEL_ID = "gemini-2.5-flash" 

# Herramientas para la IA
tools_list = [
    mcp_server.create_calendar_event,
    mcp_server.send_critical_email
]

def run_agent():
    print(f"🤖 Iniciando Agente Regulado ({MODEL_ID})...")
    ahora = datetime.now(timezone.utc)
    print(f"🕒 Fecha Actual: {ahora.isoformat()}")

    # Cargar instrucciones de GEMINI.md
    try:
        with open("GEMINI.md", "r", encoding="utf-8") as f:
            system_instruction = f.read()
    except:
        system_instruction = "Eres un gestor de tareas. Decide si crear evento en Calendar o enviar Gmail."

    # Leer el CSV localmente
    try:
        df = pd.read_csv("data/tareas.csv")
    except Exception as e:
        print(f"❌ Error leyendo CSV: {e}")
        return

    print(f"📋 Encontradas {len(df)} tareas. Procesando con pausas de seguridad...")

    for index, row in df.iterrows():
        tarea = row['Tarea']
        print(f"\n👉 Procesando [{index+1}/{len(df)}]: {tarea}...")

        prompt = f"""
        Tarea: {tarea}
        Curso: {row['Curso']}
        Fecha de Entrega: {row['Fecha_Entrega']}
        Estado Actual: {row['Estado']}
        Fecha Actual: {ahora.isoformat()}

        Sigue tus mandatos de GEMINI.md. Si la tarea está 'Pendiente' y es a futuro, usa 'create_calendar_event'.
        Si la fecha ya pasó y no está 'Entregado', usa 'send_critical_email'.
        Si ya está 'Entregado', no hagas nada.
        """

        try:
            # Enviar tarea a la IA
            response = client.models.generate_content(
                model=MODEL_ID,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    tools=tools_list,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
                ),
                contents=prompt
            )
            
            # Verificar si hubo llamadas a funciones
            executed_any = False
            if response.candidates:
                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        print(f"🛠️ IA llamó a la herramienta: {part.function_call.name}")
                        executed_any = True
            
            if response.text:
                print(f"🤖 IA responde: {response.text.strip()}")
            elif not executed_any:
                print("ℹ️ IA decidió no realizar ninguna acción para esta tarea.")

            # PAUSA DE SEGURIDAD EXTENDIDA
            if index < len(df) - 1:
                print("⏳ Esperando 20 segundos para liberar cuota API...")
                time.sleep(20)

        except Exception as e:
            if "429" in str(e):
                print(f"⚠️ Error 429: Cuota excedida para '{tarea}'. Saltando a la siguiente...")
                time.sleep(30) # Pausa larga si hay error
            else:
                print(f"❌ Error inesperado: {e}")

    print("\n--- ✅ Proceso de tareas finalizado ---")

if __name__ == "__main__":
    run_agent()
