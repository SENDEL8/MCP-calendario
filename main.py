import os
import json
import pandas as pd
import schedule
import time
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Importar herramientas locales
import mcp_server

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=api_key)
# Forzamos 1.5-flash para evitar errores de cuota y mayor estabilidad en JSON
MODEL_ID = "gemini-2.5-flash"

def run_agent():
    print(f"\n--- REVISIÓN INICIADA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    print(f"🤖 Agente Maestro ({MODEL_ID}) - Procesando...")
    ahora_dt = datetime.now(timezone.utc)
    ahora_iso = ahora_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    limite_60m_iso = (ahora_dt + timedelta(minutes=60)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    print(f"🕒 Fecha Actual: {ahora_iso}")
    print(f"🔔 Ventana Gmail (hasta): {limite_60m_iso}")

    try:
        df = pd.read_csv("data/tareas.csv")
        with open("GEMINI.md", "r", encoding="utf-8") as f:
            instrucciones = f.read()
    except Exception as e:
        print(f"❌ Error archivos: {e}")
        return

    # Prompt ULTRA-ESTRICTO para el formato JSON
    prompt = f"""
    INSTRUCCIONES:
    {instrucciones}

    DATOS (CSV):
    {df.to_csv(index=False)}

    CONTEXTO TEMPORAL:
    - Ahora: {ahora_iso}
    - Límite Alerta (60 min): {limite_60m_iso}

    TAREA DE LA IA:
    Genera un plan de acciones siguiendo estas reglas:
    1. **Calendario:** Si `Estado == 'Pendiente'` Y `Fecha_Entrega > '{ahora_iso}'` -> herramienta: 'create_calendar_event'.
    2. **Gmail:** Si `Estado != 'Entregado'` Y `Fecha_Entrega <= '{limite_60m_iso}'` -> herramienta: 'send_critical_email'.

    *Nota: Una misma tarea puede disparar ambas herramientas si es futura y falta menos de 60 minutos.*

    RESPUESTA REQUERIDA (JSON ESTRICTO):
    {{
        "acciones": [
            {{
                "herramienta": "nombre_de_la_herramienta",
                "parametros": {{ "tarea": "...", "curso": "...", "fecha_iso": "..." }}
            }}
        ]
    }}
    * IMPORTANTE: En 'send_critical_email', el parámetro de fecha debe llamarse 'fecha'.
    """

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        datos = json.loads(response.text)
        acciones = datos.get("acciones", [])

        if not acciones:
            print("✅ No se detectaron acciones necesarias.")
            return

        for accion in acciones:
            nombre = accion.get("herramienta")
            params = accion.get("parametros", {})
            tarea = params.get("tarea", "Tarea")

            if nombre == "create_calendar_event":
                print(f"📅 Programando Calendario: {tarea}...")
                print(f"   👉 {mcp_server.create_calendar_event(**params)}")
            
            elif nombre == "send_critical_email":
                print(f"📧 ENVIANDO ALERTA GMAIL: {tarea}...")
                # Ajustar nombre de parámetro si la IA se equivoca entre 'fecha' y 'fecha_iso'
                if "fecha_iso" in params and "fecha" not in params:
                    params["fecha"] = params.pop("fecha_iso")
                print(f"   👉 {mcp_server.send_critical_email(**params)}")

    except Exception as e:
        print(f"❌ Error en ejecución: {e}")
    
    print(f"--- REVISIÓN FINALIZADA ---")
    print("💤 Esperando 10 minutos para la próxima revisión...\n")

if __name__ == "__main__":
    # Programar la revisión cada 10 minutos
    schedule.every(10).minutes.do(run_agent)
    
    print("🚀 Agente de Monitoreo Activo (Cada 10 minutos)")
    # Ejecutar una vez al inicio para no esperar 10 min la primera vez
    run_agent()
    
    # Bucle infinito para mantener el script corriendo
    while True:
        schedule.run_pending()
        time.sleep(1)
