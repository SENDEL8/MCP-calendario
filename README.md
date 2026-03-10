# Agente MCP: Gestor de Tareas Autónomo (Google AI + MCP) 🚀

Este proyecto es un agente inteligente basado en el **Google AI SDK** y el protocolo **MCP (Model Context Protocol)**. Su función es monitorear continuamente un archivo de tareas, sincronizarlas con **Google Calendar** y emitir alertas críticas vía **Gmail** de forma totalmente autónoma.

## ✨ Características Principales

- **🧠 Cerebro IA (Gemini 2.0 Flash):** Utiliza el SDK más reciente de Google Generative AI para analizar el estado de las tareas y decidir las acciones necesarias basándose en los mandatos de `GEMINI.md`.
- **🔄 Monitoreo Continuo:** El agente revisa automáticamente el archivo de tareas cada **10 minutos** utilizando la librería `schedule`.
- **📅 Sincronización de Calendario:** 
  - Identifica tareas "Pendientes" con fecha de entrega futura.
  - Crea eventos automáticamente con títulos descriptivos y detalles del curso.
  - Configura **recordatorios (Pop-up)** 60 minutos antes de cada entrega.
- **⚠️ Alertas Críticas (Gmail):** 
  - Detecta tareas no entregadas que ya vencieron o que vencen en menos de 60 minutos.
  - Envía correos de advertencia inmediatos al usuario configurado.
- **🛠️ Arquitectura MCP:** Separa la lógica de decisión (IA) de la ejecución de herramientas (Google APIs) mediante el servidor `mcp_server.py`.

## 🛠️ Requisitos Previos

1.  **Google AI Studio:** Obtén una `GOOGLE_API_KEY` en [aistudio.google.com](https://aistudio.google.com/).
2.  **Google Cloud Console:**
    - Habilita las APIs de **Google Calendar** y **Gmail**.
    - Crea credenciales de tipo **OAuth 2.0 Client ID (Desktop App)**.
    - Descarga el archivo JSON y renombralo como `credentials.json` en la raíz del proyecto.
3.  **Python 3.10+**

## 🚀 Instalación y Configuración

1.  **Clonar y preparar entorno:**
    ```bash
    # Crear entorno virtual
    python -m venv .venv
    # Activar (Windows)
    .venv\Scripts\activate
    # Instalar dependencias
    pip install -r requirements.txt
    ```

2.  **Configurar Variables de Entorno (`.env`):**
    Crea un archivo `.env` basado en `.env.example`:
    ```env
    GOOGLE_API_KEY=tu_api_key_aquí
    USER_EMAIL=tu_correo@gmail.com
    ```

## 📋 Cómo Usar

1.  **Preparar Tareas (`data/tareas.csv`):**
    Asegúrate de que tus tareas tengan el formato correcto (Fechas en ISO-8601):
    ```csv
    Tarea,Curso,Fecha_Entrega,Estado
    Proyecto Final,Sistemas AI,2026-03-13T18:00:00Z,Pendiente
    Revisión Tesis,Investigación,2026-03-10T15:00:00Z,Pendiente
    ```

2.  **Ejecutar el Agente Autónomo:**
    Inicia el script principal. La primera vez se abrirá el navegador para autorizar el acceso a Google:
    ```bash
    python main.py
    ```
    *El agente quedará activo revisando cada 10 minutos.*

## 📂 Estructura del Proyecto

-   **`main.py`**: El cerebro autónomo. Orquestador que usa la IA y el planificador.
-   **`mcp_server.py`**: El ejecutor de herramientas. Contiene las funciones para Google Calendar y Gmail.
-   **`GEMINI.md`**: Los mandatos y reglas de negocio que sigue la IA.
-   **`data/tareas.csv`**: Tu base de datos local de tareas.
-   **`token.pickle`**: (Generado) Credenciales de sesión de Google persistentes.

---
*Desarrollado como una solución autónoma para la gestión inteligente de plazos y entregas.*
