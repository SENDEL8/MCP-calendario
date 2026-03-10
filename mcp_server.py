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

mcp = FastMCP("Google Tasks Toolset")

def get_google_services():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError("Error: 'credentials.json' no encontrado.")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds), build('gmail', 'v1', credentials=creds)

@mcp.tool()
def read_tasks_from_csv() -> str:
    """Lee el archivo data/tareas.csv y devuelve el contenido como string."""
    try:
        df = pd.read_csv("data/tareas.csv")
        return df.to_string()
    except Exception as e:
        return f"Error leyendo CSV: {e}"

@mcp.tool()
def create_calendar_event(tarea: str, curso: str, fecha_iso: str):
    """Crea un evento en Google Calendar con un recordatorio de 60 minutos."""
    try:
        calendar, _ = get_google_services()
        fecha_dt = datetime.fromisoformat(fecha_iso.replace('Z', '+00:00'))
        
        event = {
            'summary': f"[Tarea] {tarea} - {curso}",
            'description': f"Curso: {curso}. Estado: Pendiente.",
            'start': {'dateTime': fecha_iso},
            'end': {'dateTime': (fecha_dt + timedelta(hours=1)).isoformat().replace('+00:00', 'Z')},
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 60},
                    {'method': 'email', 'minutes': 60},
                ],
            },
        }
        calendar.events().insert(calendarId='primary', body=event).execute()
        return f"✅ Evento creado para: {tarea}"
    except Exception as e:
        return f"❌ Error en Calendario: {e}"

@mcp.tool()
def send_critical_email(tarea: str, curso: str, fecha: str):
    """Envía un correo de alerta crítica vía Gmail."""
    try:
        _, gmail = get_google_services()
        destinatario = os.getenv("USER_EMAIL")
        if not destinatario: return "Error: USER_EMAIL no configurado."

        body = f"La tarea '{tarea}' del curso '{curso}' tiene fecha de entrega {fecha} y aún no ha sido entregada."
        message = MIMEText(body)
        message['to'] = destinatario
        message['subject'] = f"⚠️ ALERTA CRÍTICA: Tarea Vencida - {tarea}"
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        gmail.users().messages().send(userId='me', body={'raw': raw}).execute()
        return f"📧 Alerta enviada para: {tarea}"
    except Exception as e:
        return f"❌ Error en Gmail: {e}"

if __name__ == "__main__":
    mcp.run()
