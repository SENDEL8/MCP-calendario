import os
import pandas as pd
import pickle
import base64
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from mcp.server.fastmcp import FastMCP

# Cargar variables de entorno
load_dotenv()

# Configuración de Google API
SCOPES = [
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/gmail.send'
]

mcp = FastMCP("Google Tasks Agent")

def get_google_services():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds), build('gmail', 'v1', credentials=creds)

def send_gmail_alert(service, tarea, curso, fecha):
    destinatario = os.getenv("USER_EMAIL")
    if not destinatario:
        print("❌ Error: No se ha configurado USER_EMAIL en el archivo .env")
        return False

    mensaje_texto = f"La tarea '{tarea}' del curso '{curso}' venció el {fecha}. Revisa el estado de entrega."
    
    message = MIMEText(mensaje_texto, 'plain', 'utf-8')
    message['to'] = destinatario
    message['from'] = 'me'
    message['subject'] = f"⚠️ ALERTA CRÍTICA: Tarea Vencida - {tarea}"
    
    # Codificación correcta para la API de Gmail
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    try:
        service.users().messages().send(userId='me', body={'raw': raw}).execute()
        return True
    except Exception as e:
        print(f"❌ Error enviando Gmail para '{tarea}': {e}")
        return False

@mcp.tool()
def sync_tasks_to_google():
    """Sincroniza tareas del CSV con Google Calendar y Gmail."""
    print("🔄 Iniciando sincronización real...")
    calendar, gmail = get_google_services()
    df = pd.read_csv("data/tareas.csv")
    ahora = datetime.now(timezone.utc)
    log = []

    for _, row in df.iterrows():
        tarea = row['Tarea']
        fecha_str = row['Fecha_Entrega']
        fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        estado = str(row['Estado']).strip().lower()

        if estado == "pendiente":
            # Calcular la diferencia de tiempo
            tiempo_restante = fecha_dt - ahora
            minutos_restantes = tiempo_restante.total_seconds() / 60

            # 1. Procesar SOLO tareas que están por venir
            if minutos_restantes > 0:
                print(f"🔍 Analizando '{tarea}': Faltan {minutos_restantes:.1f} minutos.")

                # Alerta Crítica Gmail: Solo si faltan 60 minutos o menos para la entrega
                if minutos_restantes <= 60:
                    print(f"🚨 ¡ALERTA CRÍTICA! Faltan menos de 60 min. Enviando Gmail...")
                    if send_gmail_alert(gmail, tarea, row['Curso'], fecha_str):
                        log.append(f"📧 Gmail: Alerta enviada para '{tarea}'")
                    else:
                        log.append(f"❌ Gmail: Error al enviar para '{tarea}'")

                # Google Calendar: Crear evento con recordatorio de 30 min
                print(f"📅 Programando en Calendario (Recordatorio 30m)...")
                event = {
                    'summary': f"📌 {tarea} ({row['Curso']})",
                    'description': f"Tarea del curso {row['Curso']}. Estado: Pendiente.",
                    'start': {'dateTime': fecha_str},
                    'end': {'dateTime': (fecha_dt + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")},
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'popup', 'minutes': 30},
                        ],
                    },
                }
                calendar.events().insert(calendarId='primary', body=event).execute()
                log.append(f"📅 Calendario: Evento creado para '{tarea}'")
            else:
                print(f"⏩ Omitiendo '{tarea}': Ya pasó la hora de entrega.")

    return "\n".join(log) if log else "Nada que sincronizar."

if __name__ == "__main__":
    import sys
    import time
    
    if len(sys.argv) > 1 and sys.argv[1] == "--sync":
        print(sync_tasks_to_google())
    elif len(sys.argv) > 1 and sys.argv[1] == "--watch":
        print("🕵️ Modo Vigilancia Activado. Presiona Ctrl+C para detener.")
        print("El agente revisará el CSV cada 10 minutos...")
        try:
            while True:
                resultado = sync_tasks_to_google()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {resultado}")
                time.sleep(600) # Esperar 10 minutos (600 segundos)
        except KeyboardInterrupt:
            print("\n🛑 Vigilancia detenida.")
    else:
        mcp.run()
