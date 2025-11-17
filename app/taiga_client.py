import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union

import httpx

logger = logging.getLogger(__name__)


class TaigaClientError(Exception):
    """Error genérico al interactuar con la API de Taiga."""


class TaigaClient:
    def __init__(
        self,
        base_url: str,
        username: str = None,
        password: str = None,
        auth_token: str = None,
        token_ttl: int = 82800,
        token_refresh_margin: int = 60,
    ) -> None:
        normalized_base = base_url.rstrip("/")
        self.base_url = f"{normalized_base}/"
        self.username = username
        self.password = password
        self.auth_token = auth_token
        self.token_ttl = max(token_ttl, 0)
        self.token_refresh_margin = max(token_refresh_margin, 0)
        self._client: Optional[httpx.AsyncClient] = None
        self._token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._auth_lock = asyncio.Lock()
        self._last_response_meta: Dict[str, Any] = {}

        # Validación de credenciales ahora es opcional
        # Si no hay credenciales al iniciar, se pueden setear después con set_auth_token()
        # if not auth_token and not (username and password):
        #     raise ValueError("Se requiere auth_token o username/password")

    async def start(self) -> None:
        """Inicializa el cliente HTTP asíncrono."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(10.0, read=30.0),
            )

    async def close(self) -> None:
        """Cierra el cliente HTTP."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        self._token = None
        self._token_expires_at = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("Taiga client was not started")
        return self._client

    def _build_headers(self, token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Auth-Token": token,
        }

    def _record_response(self, response: httpx.Response) -> None:
        logger.debug(
            "Taiga %s %s -> %s",
            response.request.method,
            response.request.url,
            response.status_code,
        )
        self._last_response_meta = {
            "url": str(response.request.url),
            "method": response.request.method,
            "status_code": response.status_code,
            "body": self._safe_body(response),
        }

    def _cache_token(self, token: str) -> None:
        now = datetime.now(timezone.utc)
        refresh_margin = min(self.token_refresh_margin, self.token_ttl)
        valid_duration = max(self.token_ttl - refresh_margin, 0)
        self._token = token
        self._token_expires_at = now + timedelta(seconds=valid_duration)

    @staticmethod
    def _mask_token(value: str) -> str:
        if len(value) <= 8:
            return "***"
        return f"{value[:4]}...{value[-4:]}"

    @staticmethod
    def _sanitize_sensitive(payload: Any) -> Any:
        if isinstance(payload, dict):
            data = dict(payload)
            token = data.get("auth_token")
            if isinstance(token, str):
                data["auth_token"] = TaigaClient._mask_token(token)
            return data
        return payload

    @staticmethod
    def _safe_body(response: httpx.Response) -> Any:
        try:
            data = response.json()
        except ValueError:
            return response.text
        return TaigaClient._sanitize_sensitive(data)

    def debug_state(self) -> Dict[str, Any]:
        return {
            "base_url": self.base_url,
            "username": self.username,
            "token_cached": self._token is not None,
            "token_expires_at": (
                self._token_expires_at.isoformat() if self._token_expires_at else None
            ),
            "last_response": self._last_response_meta or None,
        }

    async def _authenticate(self) -> str:
        """Obtiene un nuevo token desde Taiga."""
        # Si ya tenemos un token de API, usarlo directamente
        if self.auth_token:
            self._cache_token(self.auth_token)
            return self.auth_token

        # Si no, autenticar con usuario/contraseña
        if not (self.username and self.password):
            raise TaigaClientError("No hay credenciales disponibles para autenticación")

        client = await self._ensure_client()
        payload = {
            "type": "normal",
            "username": self.username,
            "password": self.password,
        }
        try:
            response = await client.post("auth", json=payload)
        except httpx.RequestError as exc:
            raise TaigaClientError(f"No se pudo conectar a Taiga: {exc}") from exc
        self._record_response(response)

        if response.status_code != 200:
            raise TaigaClientError(self._parse_error(response))

        data = self._json_or_error(response)
        token = data.get("auth_token")
        if not token:
            raise TaigaClientError("Taiga no devolvió un auth_token válido")

        self._cache_token(token)
        return token

    async def _get_token(self) -> str:
        """Entrega un token válido, renueva si es necesario."""
        async with self._auth_lock:
            if self._token and self._token_expires_at:
                now = datetime.now(timezone.utc)
                if now < self._token_expires_at:
                    return self._token

            return await self._authenticate()

    async def _resolve_project(self, project: Union[int, str]) -> int:
        if isinstance(project, int):
            return project

        # Si es un string, verificar si es un número
        slug = project.strip()
        if not slug:
            raise TaigaClientError("El slug del proyecto no puede estar vacío")

        # Intentar convertir a int si es un string numérico
        if slug.isdigit():
            return int(slug)

        # Si no es numérico, buscar por slug
        client = await self._ensure_client()
        token = await self._get_token()
        headers = self._build_headers(token)
        try:
            response = await client.get("projects/by_slug", params={"slug": slug}, headers=headers)
        except httpx.RequestError as exc:
            raise TaigaClientError(f"No se pudo resolver el slug del proyecto: {exc}") from exc
        self._record_response(response)

        if response.status_code != 200:
            raise TaigaClientError(self._parse_error(response))

        data = self._json_or_error(response)
        project_id = data.get("id")
        if not isinstance(project_id, int):
            raise TaigaClientError("La respuesta de Taiga no contiene un ID de proyecto válido")
        return project_id

    async def create_task(
        self,
        project: Union[int, str],
        subject: str,
        user_story: Optional[int] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        client = await self._ensure_client()
        project_id = await self._resolve_project(project)
        token = await self._get_token()

        payload: Dict[str, Any] = {"project": project_id, "subject": subject}
        if user_story is not None:
            payload["user_story"] = user_story
        if description:
            payload["description"] = description
        if tags:
            payload["tags"] = tags

        headers = self._build_headers(token)

        try:
            response = await client.post("tasks", json=payload, headers=headers)
        except httpx.RequestError as exc:
            raise TaigaClientError(f"No se pudo crear la tarea: {exc}") from exc
        self._record_response(response)

        if response.status_code not in (200, 201):
            raise TaigaClientError(self._parse_error(response))

        return self._json_or_error(response)

    async def list_user_stories(
        self,
        project: Union[int, str],
        titles_only: bool = False,
        epic: Union[int, None] = None,
    ) -> List[Dict[str, Any]]:
        client = await self._ensure_client()
        project_id = await self._resolve_project(project)
        token = await self._get_token()
        headers = self._build_headers(token)
        params: Dict[str, Any] = {"project": project_id}
        if titles_only:
            params["only_fields"] = "id,subject,epic"
        if epic is not None:
            params["epic"] = epic

        # Iterar todas las páginas
        all_stories = []
        page = 1
        while True:
            params_with_page = {**params, "page": page}
            try:
                response = await client.get("userstories", params=params_with_page, headers=headers)
            except httpx.RequestError as exc:
                raise TaigaClientError(f"No se pudieron obtener las historias: {exc}") from exc
            self._record_response(response)

            if response.status_code != 200:
                raise TaigaClientError(self._parse_error(response))

            stories = self._json_list_or_error(response)
            if not stories:
                break

            all_stories.extend(stories)

            # Verificar si hay más páginas
            x_pagination_next = response.headers.get("x-pagination-next")
            if not x_pagination_next:
                break

            page += 1

        return all_stories

    async def list_epics(self, project: Union[int, str]) -> List[Dict[str, Any]]:
        """Lista todas las épicas de un proyecto."""
        client = await self._ensure_client()
        project_id = await self._resolve_project(project)
        token = await self._get_token()
        headers = self._build_headers(token)

        params = {"project": project_id}
        try:
            response = await client.get("epics", params=params, headers=headers)
        except httpx.RequestError as exc:
            raise TaigaClientError(f"No se pudieron obtener las épicas: {exc}") from exc
        self._record_response(response)

        if response.status_code != 200:
            raise TaigaClientError(self._parse_error(response))

        return self._json_list_or_error(response)

    async def get_epic(self, epic_id: int) -> Dict[str, Any]:
        """Obtiene el detalle de una épica por su ID."""
        client = await self._ensure_client()
        token = await self._get_token()
        headers = self._build_headers(token)

        try:
            response = await client.get(f"epics/{epic_id}", headers=headers)
        except httpx.RequestError as exc:
            raise TaigaClientError(f"No se pudo obtener la épica {epic_id}: {exc}") from exc
        self._record_response(response)

        if response.status_code != 200:
            raise TaigaClientError(self._parse_error(response))

        return self._json_or_error(response)

    async def update_epic(
        self,
        epic_id: int,
        description: Optional[str] = None,
        version: int = 1,
    ) -> Dict[str, Any]:
        """Actualiza una épica."""
        client = await self._ensure_client()
        token = await self._get_token()
        headers = self._build_headers(token)

        payload: Dict[str, Any] = {"version": version}
        if description is not None:
            payload["description"] = description

        try:
            response = await client.patch(
                f"epics/{epic_id}", json=payload, headers=headers
            )
        except httpx.RequestError as exc:
            raise TaigaClientError(
                f"No se pudo actualizar la épica {epic_id}: {exc}"
            ) from exc
        self._record_response(response)

        if response.status_code != 200:
            raise TaigaClientError(self._parse_error(response))

        return self._json_or_error(response)

    async def create_user_story(
        self,
        project: Union[int, str],
        subject: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Crea una nueva historia de usuario."""
        client = await self._ensure_client()
        project_id = await self._resolve_project(project)
        token = await self._get_token()
        headers = self._build_headers(token)

        payload: Dict[str, Any] = {"project": project_id, "subject": subject}
        if description:
            payload["description"] = description
        if tags:
            payload["tags"] = tags

        try:
            response = await client.post("userstories", json=payload, headers=headers)
        except httpx.RequestError as exc:
            raise TaigaClientError(f"No se pudo crear la historia: {exc}") from exc
        self._record_response(response)

        if response.status_code not in (200, 201):
            raise TaigaClientError(self._parse_error(response))

        return self._json_or_error(response)

    async def update_user_story(
        self,
        user_story_id: int,
        description: Optional[str] = None,
        version: int = 1,
    ) -> Dict[str, Any]:
        """Actualiza una historia de usuario."""
        client = await self._ensure_client()
        token = await self._get_token()
        headers = self._build_headers(token)

        payload: Dict[str, Any] = {"version": version}
        if description is not None:
            payload["description"] = description

        try:
            response = await client.patch(
                f"userstories/{user_story_id}", json=payload, headers=headers
            )
        except httpx.RequestError as exc:
            raise TaigaClientError(
                f"No se pudo actualizar la historia {user_story_id}: {exc}"
            ) from exc
        self._record_response(response)

        if response.status_code != 200:
            raise TaigaClientError(self._parse_error(response))

        return self._json_or_error(response)

    async def get_user_story(self, user_story_id: int) -> Dict[str, Any]:
        client = await self._ensure_client()
        token = await self._get_token()
        headers = self._build_headers(token)

        try:
            response = await client.get(f"userstories/{user_story_id}", headers=headers)
        except httpx.RequestError as exc:
            raise TaigaClientError(
                f"No se pudo obtener la historia {user_story_id}: {exc}"
            ) from exc
        self._record_response(response)

        if response.status_code != 200:
            raise TaigaClientError(self._parse_error(response))

        return self._json_or_error(response)

    async def list_tasks_for_user_story(self, user_story_id: int) -> List[Dict[str, Any]]:
        client = await self._ensure_client()
        token = await self._get_token()
        headers = self._build_headers(token)
        params = {"user_story": user_story_id}

        try:
            response = await client.get("tasks", params=params, headers=headers)
        except httpx.RequestError as exc:
            raise TaigaClientError(
                f"No se pudieron obtener las tareas de la historia {user_story_id}: {exc}"
            ) from exc
        self._record_response(response)

        if response.status_code != 200:
            raise TaigaClientError(self._parse_error(response))

        return self._json_list_or_error(response)

    async def reset_token_cache(self) -> None:
        async with self._auth_lock:
            self._token = None
            self._token_expires_at = None

    async def set_auth_token(self, token: str) -> None:
        """Establece un bearer token de forma dinámica.

        Útil para actualizar el token en runtime sin reiniciar el cliente.
        """
        async with self._auth_lock:
            self.auth_token = token
            self._cache_token(token)
            logger.info("Bearer token actualizado dinámicamente")

    async def check_connection(self) -> Dict[str, Any]:
        token = await self._get_token()
        client = await self._ensure_client()
        headers = self._build_headers(token)

        try:
            response = await client.get("users/me", headers=headers)
        except httpx.RequestError as exc:
            raise TaigaClientError(f"No se pudo verificar la conexión: {exc}") from exc
        self._record_response(response)

        if response.status_code != 200:
            raise TaigaClientError(self._parse_error(response))

        data = self._json_or_error(response)
        return {
            "authenticated": True,
            "user": data.get("username"),
            "full_name": data.get("full_name"),
            "token_expires_at": (
                self._token_expires_at.isoformat() if self._token_expires_at else None
            ),
        }

    async def auth_diagnostics(self) -> Dict[str, Any]:
        # Si tenemos un token de API, probarlo directamente
        if self.auth_token:
            try:
                client = await self._ensure_client()
                headers = self._build_headers(self.auth_token)
                response = await client.get("users/me", headers=headers)
                self._record_response(response)

                if response.status_code == 200:
                    self._cache_token(self.auth_token)
                    return {
                        "ok": True,
                        "status_code": response.status_code,
                        "url": str(response.request.url),
                        "response": self._safe_body(response),
                        "token_cached": True,
                        "token_preview": self._mask_token(self.auth_token),
                        "token_expires_at": (
                            self._token_expires_at.isoformat() if self._token_expires_at else None
                        ),
                        "auth_method": "api_token",
                    }
                else:
                    return {
                        "ok": False,
                        "status_code": response.status_code,
                        "url": str(response.request.url),
                        "response": self._safe_body(response),
                        "token_cached": False,
                        "token_preview": None,
                        "token_expires_at": None,
                        "auth_method": "api_token",
                        "error": "Token de API inválido",
                    }
            except httpx.RequestError as exc:
                return {
                    "ok": False,
                    "error": f"No se pudo conectar a Taiga: {exc}",
                    "url": f"{self.base_url}users/me",
                    "auth_method": "api_token",
                }

        # Si no tenemos token de API, probar con usuario/contraseña
        if not (self.username and self.password):
            return {"ok": False, "error": "No hay credenciales disponibles", "auth_method": "none"}

        client = await self._ensure_client()
        payload = {
            "type": "normal",
            "username": self.username,
            "password": self.password,
        }
        url = f"{self.base_url}auth"

        try:
            response = await client.post("auth", json=payload)
        except httpx.RequestError as exc:
            return {
                "ok": False,
                "error": f"No se pudo conectar a Taiga: {exc}",
                "url": url,
                "auth_method": "username_password",
            }

        self._record_response(response)
        body = self._safe_body(response)
        ok = response.status_code == 200

        if ok and isinstance(body, dict):
            token = body.get("auth_token")
            if isinstance(token, str):
                self._cache_token(token)
                masked = self._mask_token(token)
            else:
                masked = None
        else:
            masked = None

        return {
            "ok": ok,
            "status_code": response.status_code,
            "url": str(response.request.url),
            "response": body,
            "token_cached": self._token is not None,
            "token_preview": masked,
            "token_expires_at": (
                self._token_expires_at.isoformat() if self._token_expires_at else None
            ),
            "auth_method": "username_password",
        }

    @staticmethod
    def _json_or_error(response: httpx.Response) -> Dict[str, Any]:
        try:
            data = response.json()
        except ValueError as exc:
            raise TaigaClientError("La respuesta de Taiga no es JSON válido") from exc
        if not isinstance(data, dict):
            raise TaigaClientError("La respuesta de Taiga no contiene un objeto JSON")
        return data

    @staticmethod
    def _json_list_or_error(response: httpx.Response) -> List[Dict[str, Any]]:
        try:
            data = response.json()
        except ValueError as exc:
            raise TaigaClientError("La respuesta de Taiga no es JSON válido") from exc
        if not isinstance(data, list):
            raise TaigaClientError("La respuesta de Taiga no contiene una lista JSON")
        return data

    async def list_projects(self) -> List[Dict[str, Any]]:
        """Lista todos los proyectos accesibles por el usuario."""
        client = await self._ensure_client()
        token = await self._get_token()
        headers = self._build_headers(token)

        try:
            response = await client.get("projects", headers=headers)
        except httpx.RequestError as exc:
            raise TaigaClientError(f"No se pudo listar proyectos: {exc}") from exc

        self._record_response(response)

        if response.status_code != 200:
            raise TaigaClientError(self._parse_error(response))

        return self._json_list_or_error(response)

    async def get_project(self, project: Union[int, str]) -> Dict[str, Any]:
        """Obtiene detalle de un proyecto por ID o slug."""
        project_id = await self._resolve_project(project)
        client = await self._ensure_client()
        token = await self._get_token()
        headers = self._build_headers(token)

        try:
            response = await client.get(f"projects/{project_id}", headers=headers)
        except httpx.RequestError as exc:
            raise TaigaClientError(f"No se pudo obtener proyecto: {exc}") from exc

        self._record_response(response)

        if response.status_code != 200:
            raise TaigaClientError(self._parse_error(response))

        return self._json_or_error(response)

    async def get_task(self, task_id: int) -> Dict[str, Any]:
        """Obtiene detalle de una tarea específica."""
        client = await self._ensure_client()
        token = await self._get_token()
        headers = self._build_headers(token)

        try:
            response = await client.get(f"tasks/{task_id}", headers=headers)
        except httpx.RequestError as exc:
            raise TaigaClientError(f"No se pudo obtener tarea: {exc}") from exc

        self._record_response(response)

        if response.status_code != 200:
            raise TaigaClientError(self._parse_error(response))

        return self._json_or_error(response)

    async def list_tasks(
        self,
        project: Union[int, str] = None,
        user_story: int = None,
        status: int = None,
        assigned_to: int = None,
    ) -> List[Dict[str, Any]]:
        """Lista tareas con filtros opcionales."""
        client = await self._ensure_client()
        token = await self._get_token()
        headers = self._build_headers(token)

        params = {}
        if project is not None:
            params["project"] = await self._resolve_project(project)
        if user_story is not None:
            params["user_story"] = user_story
        if status is not None:
            params["status"] = status
        if assigned_to is not None:
            params["assigned_to"] = assigned_to

        try:
            response = await client.get("tasks", headers=headers, params=params)
        except httpx.RequestError as exc:
            raise TaigaClientError(f"No se pudo listar tareas: {exc}") from exc

        self._record_response(response)

        if response.status_code != 200:
            raise TaigaClientError(self._parse_error(response))

        return self._json_list_or_error(response)

    async def delete_task(self, task_id: int) -> bool:
        """Elimina una tarea."""
        client = await self._ensure_client()
        token = await self._get_token()
        headers = self._build_headers(token)

        try:
            response = await client.delete(f"tasks/{task_id}", headers=headers)
        except httpx.RequestError as exc:
            raise TaigaClientError(f"No se pudo eliminar tarea: {exc}") from exc

        self._record_response(response)

        if response.status_code not in (200, 204):
            raise TaigaClientError(self._parse_error(response))

        return True

    async def update_task(
        self,
        task_id: int,
        subject: str = None,
        description: str = None,
        status: int = None,
        assigned_to: int = None,
        tags: List[str] = None,
        version: int = None,
    ) -> Dict[str, Any]:
        """Actualiza una tarea existente."""
        client = await self._ensure_client()
        token = await self._get_token()
        headers = self._build_headers(token)

        # Construir payload solo con campos proporcionados
        payload = {}
        if subject is not None:
            payload["subject"] = subject
        if description is not None:
            payload["description"] = description
        if status is not None:
            payload["status"] = status
        if assigned_to is not None:
            payload["assigned_to"] = assigned_to
        if tags is not None:
            payload["tags"] = tags
        if version is not None:
            payload["version"] = version

        if not payload:
            raise TaigaClientError("Se requiere al menos un campo para actualizar")

        try:
            response = await client.patch(f"tasks/{task_id}", headers=headers, json=payload)
        except httpx.RequestError as exc:
            raise TaigaClientError(f"No se pudo actualizar tarea: {exc}") from exc

        self._record_response(response)

        if response.status_code != 200:
            raise TaigaClientError(self._parse_error(response))

        return self._json_or_error(response)

    async def get_task_statuses(self, project: Union[int, str]) -> List[Dict[str, Any]]:
        """Obtiene los estados de tareas disponibles en un proyecto."""
        project_id = await self._resolve_project(project)
        client = await self._ensure_client()
        token = await self._get_token()
        headers = self._build_headers(token)

        try:
            response = await client.get(
                "task-statuses", headers=headers, params={"project": project_id}
            )
        except httpx.RequestError as exc:
            raise TaigaClientError(f"No se pudo obtener estados de tareas: {exc}") from exc

        self._record_response(response)

        if response.status_code != 200:
            raise TaigaClientError(self._parse_error(response))

        return self._json_list_or_error(response)

    async def get_userstory_statuses(self, project: Union[int, str]) -> List[Dict[str, Any]]:
        """Obtiene los estados de historias de usuario disponibles en un proyecto."""
        project_id = await self._resolve_project(project)
        client = await self._ensure_client()
        token = await self._get_token()
        headers = self._build_headers(token)

        try:
            response = await client.get(
                "userstory-statuses", headers=headers, params={"project": project_id}
            )
        except httpx.RequestError as exc:
            raise TaigaClientError(f"No se pudo obtener estados de historias: {exc}") from exc

        self._record_response(response)

        if response.status_code != 200:
            raise TaigaClientError(self._parse_error(response))

        return self._json_list_or_error(response)

    async def list_milestones(self, project: Union[int, str]) -> List[Dict[str, Any]]:
        """Lista todos los sprints/milestones de un proyecto."""
        client = await self._ensure_client()
        project_id = await self._resolve_project(project)
        token = await self._get_token()
        headers = self._build_headers(token)

        params = {"project": project_id}
        try:
            response = await client.get("milestones", params=params, headers=headers)
        except httpx.RequestError as exc:
            raise TaigaClientError(f"No se pudieron obtener los milestones: {exc}") from exc
        self._record_response(response)

        if response.status_code != 200:
            raise TaigaClientError(self._parse_error(response))

        return self._json_list_or_error(response)

    async def get_project_tags(self, project: Union[int, str]) -> Dict[str, Any]:
        """Obtiene las etiquetas y sus colores de un proyecto."""
        client = await self._ensure_client()
        project_id = await self._resolve_project(project)
        token = await self._get_token()
        headers = self._build_headers(token)

        try:
            response = await client.get(f"projects/{project_id}/tags_colors", headers=headers)
        except httpx.RequestError as exc:
            raise TaigaClientError(f"No se pudieron obtener las etiquetas: {exc}") from exc
        self._record_response(response)

        if response.status_code != 200:
            raise TaigaClientError(self._parse_error(response))

        return self._json_or_error(response)

    @staticmethod
    def _parse_error(response: httpx.Response) -> str:
        base_message = f"Error de Taiga ({response.status_code})"
        try:
            payload = response.json()
        except ValueError:
            return base_message

        if isinstance(payload, dict):
            for key in ("error", "message", "msg", "detail"):
                if payload.get(key):
                    return str(payload[key])
            return f"{base_message}: {payload}"
        return base_message
