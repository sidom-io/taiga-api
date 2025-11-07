# Taiga FastAPI UV

Servicio FastAPI asíncrono que se autentica contra Taiga y permite crear tareas mediante un endpoint REST.

## Requisitos previos

- Python 3.11 o superior
- [uv](https://github.com/astral-sh/uv) instalado globalmente

## Configuración

1. Copia `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```

2. **Configura la autenticación** (elige una opción):

### Opción 1: Token de Sesión del Navegador (Recomendado)

1. Ve a tu instancia de Taiga: https://tu-instancia-taiga.com
2. Inicia sesión con tu usuario y contraseña
3. Ve a tu perfil (click en tu avatar)
4. Ve a "Settings" o "Configuración"
5. Busca la sección "API" o "Application Tokens"
6. Genera un nuevo token de aplicación
7. Agrega el token al archivo `.env`:

```bash
TAIGA_AUTH_TOKEN=tu_token_de_sesion_aqui
```

### Opción 2: Usuario y Contraseña

Si no puedes obtener un token de sesión:

```bash
TAIGA_USERNAME=tu_usuario
TAIGA_PASSWORD=tu_contraseña
```

## Solución de Problemas de Autenticación

### Problema Común: Credenciales no funcionan para la API

Si ves el error `"No active account found with the given credentials"`, significa que aunque puedas acceder a la interfaz web de Taiga, las credenciales de usuario/contraseña no funcionan para la API.

### Solución: Obtener Token de Sesión del Navegador

Sigue estos pasos para obtener un token válido:

#### 1. Abre las Herramientas de Desarrollador

- En Chrome/Edge: Presiona `F12` o `Ctrl+Shift+I`
- En Firefox: Presiona `F12` o `Ctrl+Shift+I`

#### 2. Configura la Captura de Red

1. Ve a la pestaña **"Network"** (Red)
2. Asegúrate de que esté grabando (botón rojo activo)
3. Filtra por **"XHR"** o **"Fetch"**

#### 3. Genera Tráfico de Red

- Recarga la página de Taiga (`F5`)
- O navega a cualquier sección del proyecto

#### 4. Encuentra el Token

1. Busca requests que vayan a `/api/v1/`
2. Click en cualquier request de la API
3. Ve a la pestaña **"Headers"** (Cabeceras)
4. En **"Request Headers"** busca:
   ```
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
   ```

#### 5. Copia y Configura el Token

1. **Copia solo el token** (la parte después de "Bearer ")
2. **Agrega el token al `.env`**:
   ```bash
   TAIGA_AUTH_TOKEN=tu_token_copiado_aqui
   ```
3. **Comenta las credenciales de usuario**:
   ```bash
   # TAIGA_USERNAME=tu_usuario
   # TAIGA_PASSWORD=tu_contraseña
   ```

![Ejemplo de interfaz de Taiga](util/taiga_token_example.jpg)

*La imagen muestra la interfaz de Taiga donde puedes acceder a las herramientas de desarrollador*

#### 6. Verifica que Funciona

```bash
# Inicia el servidor
uv run uvicorn app.main:app --reload

# En otra terminal, prueba la autenticación
curl -X POST "http://localhost:8001/debug/auth"
```

Deberías ver:
```json
{
  "ok": true,
  "status_code": 200,
  "auth_method": "api_token",
  "token_cached": true
}
```

### Comandos de Diagnóstico

Si sigues teniendo problemas:

1. **Ejecuta el diagnóstico de autenticación**:
   ```bash
   curl -X POST "http://localhost:8001/debug/auth"
   ```

2. **Verifica el estado del cliente**:
   ```bash
   curl -X GET "http://localhost:8001/debug/state"
   ```

3. **Prueba la conexión**:
   ```bash
   curl -X GET "http://localhost:8001/debug/connection"
   ```

### Errores Comunes

- **"No active account found with the given credentials"**: Las credenciales de usuario/contraseña no funcionan para la API → Usa token de sesión
- **"invalid_credentials"**: Usuario o contraseña incorrectos → Verifica credenciales web
- **"Se requiere autenticación"**: Token inválido o expirado → Obtén un nuevo token del navegador
- **Error 404 en API**: URL incorrecta → Asegúrate de que `TAIGA_BASE_URL` termine con `/`

## Recursos Adicionales

- **Carpeta `util/`**: Contiene capturas de pantalla y guías adicionales para la configuración
- **Herramientas de diagnóstico**: Usa los endpoints `/debug/*` para troubleshooting
- **Documentación de API**: Disponible en `http://localhost:8001/docs` cuando el servidor esté ejecutándose

## Instalación de dependencias

Ejecutá:

```bash
uv sync
```

## Ejecución en desarrollo

```bash
uv run uvicorn app.main:app --reload
```

El servicio quedará disponible en `http://0.0.0.0:8000/`.

Para usar la api se recomienda ver la documentación `http://0.0.0.0:8000/docs`.

## Endpoint disponible

### Crear tarea

`POST /tasks`

```bash
curl -X POST http://0.0.0.0:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "project": "sample-project-slug",
    "subject": "Nueva tarea",
    "user_story": 42,
    "description": "Descripción opcional"
  }'
```

```bash
curl -X POST http://0.0.0.0:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "project": 123,
    "subject": "Nueva tarea por ID"
  }'
```

La respuesta exitosa incluye `id`, `subject`, `project`, `user_story` y `ref`.

### Listar historias de usuario

`GET /user-stories?project=<id_o_slug>&titles_only=<true|false>`

```bash
curl "http://0.0.0.0:8000/user-stories?project=sample-project-slug&titles_only=true"
```

### Obtener detalle de historia de usuario

`GET /user-stories/{user_story_id}`

```bash
curl "http://0.0.0.0:8000/user-stories/42"
```

### Listar tareas de una historia

`GET /user-stories/{user_story_id}/tasks`

```bash
curl "http://0.0.0.0:8000/user-stories/42/tasks"
```

### Depuración

- `POST /debug/cache/clear` limpia el token cacheado (fuerza nueva autenticación en el próximo request).
- `GET /debug/connection` verifica la conexión contra Taiga y devuelve el usuario autenticado y la expiración del token.
- `GET /debug/state` expone el estado actual del cliente (base URL normalizada, si hay token cacheado y el último response recibido).
- `POST /debug/auth` ejecuta el login y devuelve el status y payload exactamente como responde Taiga (ideal para diagnosticar credenciales).
