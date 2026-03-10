# Agente MCP: Gestor de Tareas AI

Este archivo define la lógica central para el agente autónomo encargado de sincronizar tareas con Google Calendar y emitir alertas críticas vía Gmail.

## 📋 Mandatos del Agente

1. **Lectura de Datos:**
   - Utilizar el servidor MCP **Filesystem** para leer periódicamente `data/tareas.csv`.
   - Parsear el contenido asegurando que las fechas en formato ISO-8601 sean interpretadas correctamente.

2. **Sincronización de Calendario:**
   - Identificar tareas con `Estado == "Pendiente"`.
   - Para cada tarea pendiente, verificar si ya existe un evento en **Google Calendar**.
   - Si no existe, crear un evento con:
     - Título: `[Tarea] {Tarea} - {Curso}`
     - Descripción: `Curso: {Curso}. Estado: Pendiente.`
     - Fecha/Hora de inicio: `{Fecha_Entrega}`
     - Recordatorio: Configurar una alerta de notificación 60 minutos antes del evento.

3. **Gestión de Alertas Críticas (Gmail):**
   - Comparar `{Fecha_Entrega}` con la fecha/hora actual (Hoy: 2026-03-09).
   - **Condición de Alerta:** Si `{Fecha_Entrega} < Ahora` Y `{Estado} != "Entregado"`.
   - **Acción:** Enviar un correo electrónico vía **Gmail** con el siguiente formato:
     - Destinatario: (Configurar correo del usuario)
     - Asunto: `⚠️ ALERTA CRÍTICA: Tarea Vencida - {Tarea}`
     - Cuerpo: `La tarea "{Tarea}" del curso "{Curso}" tiene fecha de entrega {Fecha_Entrega} y aún no ha sido entregada. Por favor, revisa el estado de entrega inmediatamente.`

## 🛠️ Herramientas MCP Requeridas

- `filesystem`: Para leer y escribir en el directorio `data/`.
- `google-calendar`: Para gestionar los eventos y recordatorios.
- `gmail`: Para el envío de notificaciones de advertencia.

## 🚀 Ciclo de Ejecución

1. Leer `data/tareas.csv`.
2. Para cada fila:
   - Validar estado y fecha.
   - Ejecutar lógica de Calendario o Gmail según corresponda.
3. (Opcional) Actualizar el CSV si se detectan cambios que deban persistir.
