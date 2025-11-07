# Ejemplo de Herramientas de Desarrollador

Esta carpeta contiene recursos útiles para la configuración y uso del proyecto.

## Cómo obtener el token de autenticación

Para obtener el token de autenticación desde el navegador, sigue estos pasos:

1. Abre Taiga en tu navegador
2. Presiona F12 para abrir las herramientas de desarrollador
3. Ve a la pestaña "Network" (Red)
4. Recarga la página o navega por Taiga
5. Busca requests a `/api/v1/`
6. Click en cualquier request
7. Ve a "Headers" y busca "Authorization: Bearer <token>"
8. Copia el token y agrégalo al .env

![Ejemplo de herramientas de desarrollador](taiga-interface-example.png)

La imagen muestra la interfaz de Taiga donde puedes ver las tareas del proyecto DAI.
