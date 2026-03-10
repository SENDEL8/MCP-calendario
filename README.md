# MCP Google Calendar & Gmail Task Manager 🚀

Este proyecto es un agente autónomo basado en el protocolo MCP (Model Context Protocol) que sincroniza tareas desde un archivo CSV con Google Calendar y envía alertas críticas por Gmail para tareas vencidas.

## ✨ Características

- **Sincronización Inteligente:** Clasifica tareas según su fecha de entrega y estado.
- **Google Calendar:** Crea eventos para tareas pendientes con recordatorios automáticos (Pop-up y Email) **60 minutos** antes de la entrega.
- **Alertas Críticas (Gmail):** Detecta tareas vencidas (`Fecha_Entrega < Hoy`) que no han sido entregadas y envía un correo de advertencia inmediato.
- **Formato Estándar:** Compatible con fechas ISO-8601 (`YYYY-MM-DDTHH:MM:SSZ`).
- **Servidor MCP:** Implementado con `FastMCP` para una integración sencilla con clientes como Claude Desktop, Cursor o Windsurf.

## 🛠️ Requisitos Previos

1. **Google Cloud Console:** 
Para que el script tenga permiso de escribir en tu calendario, debes:
   1. Ir a Google Cloud Console (https://console.cloud.google.com/).
   2. Crear un proyecto nuevo.
   3. Habilitar Google Calendar API y Gmail API.
   4. En "Credentials", crear un OAuth 2.0 Client ID (tipo "Desktop App").
   5. Descargar el archivo JSON de credenciales y guardarlo en la carpeta del proyecto como credentials.json.
2. **Python 3.10+** e instalación de dependencias:

# Crear entorno virtual
python -m venv .venv
# Activar entorno (Windows)
.venv\Scripts\activate  
# Instalar dependencias
   ```bash
   pip install -r requirements.txt
   ```
3. **Archivo `.env`:** Configura tu correo para recibir las alertas:
   ```env
   GOOGLE_API_KEY=tu_api_key_de_google_ai_studio
   USER_EMAIL=tu_correo@gmail.com
   ```

## 🚀 Uso

### 1. Preparar los datos (`data/tareas.csv`)
Edita el archivo CSV con tus tareas siguiendo este formato:
```csv
Tarea,Curso,Fecha_Entrega,Estado
Proyecto Final,Sistemas AI,2026-03-15T10:00:00Z,Pendiente
Examen Parcial,Bases de Datos,2026-03-01T09:00:00Z,Pendiente
```

### 2. Autenticación Inicial y Sincronización Directa
La primera vez que ejecutes el script, se abrirá el navegador para autorizar el acceso a tu cuenta de Google:
```bash
python mcp_server.py --sync
```
Esto generará un archivo `token.pickle` para sesiones futuras.

### 3. Ejecutar como Servidor MCP
Para usarlo como herramienta dentro de un cliente MCP:
```bash
python mcp_server.py
```

## 📂 Estructura del Proyecto

- `mcp_server.py`: El núcleo del agente (Servidor MCP + Lógica de Google APIs).
- `data/tareas.csv`: Base de datos local de tareas.
- `GEMINI.md`: Instrucciones lógicas del agente para el modelo de IA.
- `main.py`: Script de simulación y análisis de tareas vía IA.
- `credentials.json`: (Tuyo) Credenciales de Google Cloud.
- `token.pickle`: (Generado) Token de acceso a tu cuenta de Google.

---
*Desarrollado como un prototipo funcional para la gestión autónoma de tareas académicas y profesionales.*
