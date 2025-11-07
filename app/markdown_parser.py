"""Parser de markdown para extraer tareas y convertir referencias a links de Taiga."""

import re
from typing import Dict, List, Optional


class MarkdownTaskParser:
    """Parser para extraer tareas de un documento markdown."""

    def __init__(self, taiga_base_url: Optional[str] = None):
        """
        Inicializa el parser.

        Args:
            taiga_base_url: URL base de Taiga (ej: https://taiga.example.com)
        """
        self.taiga_base_url = taiga_base_url or "https://taiga.vuce-sidom.gob.ar"

    def parse_tasks(self, markdown: str, project_slug: str) -> List[Dict]:
        """
        Extrae tareas del markdown.

        Formato esperado:
        ### N. Título de la tarea
        **Componente**: Backend - API
        **Estimación**: 5 puntos

        **Descripción**:
        Texto de descripción

        **Criterios de aceptación**:
        - Criterio 1
        - Criterio 2

        **Dependencias**: Tarea 1, HU #130
        """
        tasks = []
        # Dividir por tareas (títulos de nivel 3)
        # Agregar salto de línea al inicio si no existe para que el regex funcione
        if not markdown.startswith("\n"):
            markdown = "\n" + markdown
        task_sections = re.split(r"\n### \d+\.\s+", markdown)

        for section in task_sections[1:]:  # Saltar el preámbulo
            task = self._parse_task_section(section, project_slug)
            if task:
                tasks.append(task)

        return tasks

    def _parse_task_section(self, section: str, project_slug: str) -> Optional[Dict]:
        """Parsea una sección de tarea individual."""
        lines = section.split("\n")
        if not lines:
            return None

        # Título es la primera línea
        title = lines[0].strip()

        # Extraer metadatos
        component = self._extract_field(section, r"\*\*Componente\*\*:\s*(.+)")

        # Extraer descripción
        description = self._extract_description(section)

        # Extraer criterios de aceptación
        acceptance_criteria = self._extract_acceptance_criteria(section)

        # Extraer dependencias
        dependencies = self._extract_dependencies(section)

        # Construir descripción completa con formato markdown
        full_description = self._build_full_description(
            description, acceptance_criteria, dependencies, component, project_slug
        )

        # Extraer tags del componente
        tags = self._extract_tags(component)
        # Filtrar None y vacíos
        tags = [t for t in tags if t]

        return {
            "subject": title,
            "description": full_description,
            "tags": tags if tags else None,
        }

    def _extract_field(self, text: str, pattern: str) -> Optional[str]:
        """Extrae un campo usando regex."""
        match = re.search(pattern, text)
        return match.group(1).strip() if match else None

    def _extract_description(self, section: str) -> str:
        """Extrae la descripción de la tarea."""
        desc_match = re.search(r"\*\*Descripción\*\*:\s*\n(.+?)(?=\n\*\*|$)", section, re.DOTALL)
        if desc_match:
            return desc_match.group(1).strip()
        return ""

    def _extract_acceptance_criteria(self, section: str) -> List[str]:
        """Extrae los criterios de aceptación."""
        criteria = []
        criteria_match = re.search(
            r"\*\*Criterios de aceptación\*\*:\s*\n(.+?)(?=\n\*\*|$)", section, re.DOTALL
        )
        if criteria_match:
            criteria_text = criteria_match.group(1)
            # Extraer items de lista
            criteria = re.findall(r"^[-*]\s+(.+)$", criteria_text, re.MULTILINE)
        return criteria

    def _extract_dependencies(self, section: str) -> List[str]:
        """Extrae las dependencias."""
        deps = []
        deps_match = re.search(r"\*\*Dependencias\*\*:\s*(.+?)(?=\n\n|$)", section, re.DOTALL)
        if deps_match:
            deps_text = deps_match.group(1).strip()
            # Separar por comas
            deps = [d.strip() for d in deps_text.split(",")]
        return deps

    def _extract_tags(self, component: Optional[str]) -> List[str]:
        """Extrae tags del componente."""
        if not component:
            return []

        tags = []
        component_lower = component.lower()

        if "backend" in component_lower:
            tags.append("backend")
        if "frontend" in component_lower:
            tags.append("frontend")
        if "testing" in component_lower or "test" in component_lower:
            tags.append("testing")
        if "api" in component_lower:
            tags.append("api")
        if "ui" in component_lower:
            tags.append("ui")
        if "integración" in component_lower or "integration" in component_lower:
            tags.append("integration")

        return tags

    def _build_full_description(
        self,
        description: str,
        criteria: List[str],
        dependencies: List[str],
        component: Optional[str],
        project_slug: str,
    ) -> str:
        """Construye la descripción completa con formato markdown y links."""
        parts = []

        # Componente
        if component:
            parts.append(f"**Componente**: {component}")
            parts.append("")  # Línea en blanco

        # Descripción
        if description:
            parts.append("## Descripción")
            parts.append("")
            parts.append(description)
            parts.append("")

        # Criterios de aceptación
        if criteria:
            parts.append("## Criterios de Aceptación")
            parts.append("")
            for criterion in criteria:
                parts.append(f"- {criterion}")
            parts.append("")

        # Dependencias con links
        if dependencies:
            parts.append("## Dependencias")
            parts.append("")
            for dep in dependencies:
                linked_dep = self._convert_to_taiga_link(dep, project_slug)
                parts.append(f"- {linked_dep}")
            parts.append("")

        return "\n".join(parts)

    def _convert_to_taiga_link(self, text: str, project_slug: str) -> str:
        """
        Convierte referencias a links de Taiga.

        Formatos soportados:
        - "Tarea 1" -> Link a tarea #1
        - "HU #130" -> Link a historia #130
        - "US #88" -> Link a historia #88
        - "Sistema D3" -> Texto sin cambios
        """
        # Patrón para "Tarea N"
        text = re.sub(
            r"Tarea (\d+)",
            lambda m: (
                f"[Tarea #{m.group(1)}]"
                f"({self.taiga_base_url}/project/{project_slug}/task/{m.group(1)})"
            ),
            text,
        )

        # Patrón para "HU #N" o "US #N"
        text = re.sub(
            r"(HU|US) #(\d+)",
            lambda m: (
                f"[{m.group(1)} #{m.group(2)}]"
                f"({self.taiga_base_url}/project/{project_slug}/us/{m.group(2)})"
            ),
            text,
        )

        # Patrón para "#N" solo
        text = re.sub(
            r"(?<!\w)#(\d+)(?!\w)",
            lambda m: (
                f"[#{m.group(1)}]" f"({self.taiga_base_url}/project/{project_slug}/us/{m.group(1)})"
            ),
            text,
        )

        return text
