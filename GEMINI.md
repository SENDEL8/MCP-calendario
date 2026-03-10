# Agente MCP: Gestor de Tareas AI

Este archivo define la lógica central para el agente autónomo encargado de sincronizar tareas con Google Calendar y emitir alertas críticas vía Gmail.

## 📋 Mandatos del Agente

1. **Lectura de Datos:**
   - Utilizar el servidor MCP **Filesystem** para leer periódicamente `data/tareas.csv`.
   - Parsear el contenido asegurando que las fechas en formato ISO-8601 sean interpretadas correctamente.

2. **Sincronización de Calendario:**
   - Identificar tareas con `Estado == "Pendiente"`.
   - Si la fecha de entrega es **futura** (falta más de 60 minutos), crear un evento en **Google Calendar** con:
     - Título: `[Tarea] {Tarea} - {Curso}`
     - Descripción: `Curso: {Curso}. Estado: Pendiente.`
     - Fecha/Hora de inicio: `{Fecha_Entrega}`
     - Recordatorio: Configurar una alerta de notificación 60 minutos antes del evento.

3. **Gestión de Alertas Críticas (Gmail):**
   - **Condición de Alerta Gmail:** Si `{Estado} != "Entregado"` Y se cumple cualquiera de estos:
     - La tarea ya venció (`{Fecha_Entrega} < Ahora`).
     - Faltan **60 minutos o menos** para la entrega (`Ahora <= {Fecha_Entrega} <= Ahora + 60min`).
   - **Acción:** Enviar un correo electrónico vía **Gmail** con el siguiente formato:
     - Destinatario: (Configurar correo del usuario)
     - Asunto: `⚠️ ALERTA CRÍTICA: Tarea Próxima o Vencida - {Tarea}`
     - Cuerpo: `La tarea "{Tarea}" del curso "{Curso}" tiene fecha de entrega {Fecha_Entrega} y aún no ha sido entregada. Por favor, revisa el estado de entrega inmediatamente.`

## 🛠️ Herramientas MCP Requeridas

- `filesystem`: Para leer y escribir en el directorio `data/`.
- `google-calendar`: Para gestionar los eventos y recordatorios.
- `gmail`: Para el envío de notificaciones de advertencia.

## 🚀 Ciclo de Ejecución

1. Leer `data/tareas.csv`.
2. Para cada fila:
   - Validar estado y tiempo restante.
   - Si falta <= 60 min o ya venció: **Priorizar Gmail**.
   - Si falta > 60 min: **Crear Calendario**.
