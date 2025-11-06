import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union

import httpx


class TaigaClientError(Exception):
    """Error genérico al interactuar con la API de Taiga."""


class TaigaClient:
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        token_ttl: int,
        token_refresh_margin: int = 60,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.token_ttl = max(token_ttl, 0)
        self.token_refresh_margin = max(token_refresh_margin, 0)
        self._client: Optional[httpx.AsyncClient] = None
        self._token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._auth_lock = asyncio.Lock()

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

    async def _authenticate(self) -> str:
        """Obtiene un nuevo token desde Taiga."""
        client = await self._ensure_client()
        payload = {
            "type": "normal",
            "username": self.username,
            "password": self.password,
        }
        try:
            response = await client.post("/auth", json=payload)
        except httpx.RequestError as exc:
            raise TaigaClientError(f"No se pudo conectar a Taiga: {exc}") from exc

        if response.status_code != 200:
            raise TaigaClientError(self._parse_error(response))

        data = self._json_or_error(response)
        token = data.get("auth_token")
        if not token:
            raise TaigaClientError("Taiga no devolvió un auth_token válido")

        now = datetime.now(timezone.utc)
        refresh_margin = min(self.token_refresh_margin, self.token_ttl)
        valid_duration = max(self.token_ttl - refresh_margin, 0)
        self._token = token
        self._token_expires_at = now + timedelta(seconds=valid_duration)
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

        slug = project.strip()
        if not slug:
            raise TaigaClientError("El slug del proyecto no puede estar vacío")

        client = await self._ensure_client()
        try:
            response = await client.get("/projects/by_slug", params={"slug": slug})
        except httpx.RequestError as exc:
            raise TaigaClientError(f"No se pudo resolver el slug del proyecto: {exc}") from exc

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
    ) -> Dict[str, Any]:
        client = await self._ensure_client()
        project_id = await self._resolve_project(project)
        token = await self._get_token()

        payload: Dict[str, Any] = {"project": project_id, "subject": subject}
        if user_story is not None:
            payload["user_story"] = user_story
        if description:
            payload["description"] = description

        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = await client.post("/tasks", json=payload, headers=headers)
        except httpx.RequestError as exc:
            raise TaigaClientError(f"No se pudo crear la tarea: {exc}") from exc

        if response.status_code not in (200, 201):
            raise TaigaClientError(self._parse_error(response))

        return self._json_or_error(response)

    async def list_user_stories(
        self, project: Union[int, str], titles_only: bool = False
    ) -> List[Dict[str, Any]]:
        client = await self._ensure_client()
        project_id = await self._resolve_project(project)
        token = await self._get_token()
        headers = {"Authorization": f"Bearer {token}"}
        params: Dict[str, Any] = {"project": project_id}
        if titles_only:
            params["only_fields"] = "id,subject"

        try:
            response = await client.get("/userstories", params=params, headers=headers)
        except httpx.RequestError as exc:
            raise TaigaClientError(f"No se pudieron obtener las historias: {exc}") from exc

        if response.status_code != 200:
            raise TaigaClientError(self._parse_error(response))

        return self._json_list_or_error(response)

    async def get_user_story(self, user_story_id: int) -> Dict[str, Any]:
        client = await self._ensure_client()
        token = await self._get_token()
        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = await client.get(f"/userstories/{user_story_id}", headers=headers)
        except httpx.RequestError as exc:
            raise TaigaClientError(f"No se pudo obtener la historia {user_story_id}: {exc}") from exc

        if response.status_code != 200:
            raise TaigaClientError(self._parse_error(response))

        return self._json_or_error(response)

    async def list_tasks_for_user_story(self, user_story_id: int) -> List[Dict[str, Any]]:
        client = await self._ensure_client()
        token = await self._get_token()
        headers = {"Authorization": f"Bearer {token}"}
        params = {"user_story": user_story_id}

        try:
            response = await client.get("/tasks", params=params, headers=headers)
        except httpx.RequestError as exc:
            raise TaigaClientError(
                f"No se pudieron obtener las tareas de la historia {user_story_id}: {exc}"
            ) from exc

        if response.status_code != 200:
            raise TaigaClientError(self._parse_error(response))

        return self._json_list_or_error(response)

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
