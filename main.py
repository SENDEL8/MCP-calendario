import os
import pandas as pd
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
from google import genai

# Cargar variables de entorno
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=api_key)

def main():
    print("🤖 Agente MCP: Procesando tareas...")
    
    # Leer CSV
    try:
        df = pd.read_csv("data/tareas.csv")
    except:
        print("No se encontró el archivo csv.")
        return

    ahora = datetime.now(timezone.utc)
    
    for _, row in df.iterrows():
        print(f"\n> Tarea: {row['Tarea']}")
        
        # Lógica de respaldo inmediata para no depender de la IA si falla
        fecha_entrega = datetime.strptime(row['Fecha_Entrega'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        es_pendiente = str(row['Estado']).strip().lower() == "pendiente"
        vencida = fecha_entrega < ahora

        # Intentar consultar a la IA con un prompt ultra-simple
        prompt = f"Tarea: {row['Tarea']}, Estado: {row['Estado']}, Vencida: {vencida}. ¿Calendario o Gmail? Responde en 3 palabras."
        
        try:
            # Esperar un poco más entre llamadas
            time.sleep(2) 
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            print(f"🤖 IA: {response.text.strip()}")
        except Exception as e:
            # Si falla la IA, ejecutar la lógica local automáticamente
            if es_pendiente:
                if vencida:
                    print("📢 [GMAIL] Enviando alerta crítica de vencimiento...")
                else:
                    print("📅 [CALENDAR] Programando evento y recordatorio...")
            else:
                print("✅ [OK] Tarea ya entregada.")

if __name__ == "__main__":
    main()
