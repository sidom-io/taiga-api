"""
AI-powered Taiga project reorganization.

Analyzes current epics, user stories and tasks, and proposes reorganization
based on DAI architecture (modules D3-D8).
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

# DAI Architecture Epic Definitions (granular epics from architecture docs)
MODULE_DEFINITIONS = {
    "D3-authenticar": {
        "name": "D3 - Autenticación",
        "description": "Login, SSO, tokens de sesión, integración con ARCA/CF4",
        "keywords": ["auth", "login", "sso", "token", "sesión", "arca", "cf4", "credencial"],
        "color": "#e74c3c"
    },
    "D3-user": {
        "name": "D3 - Gestión de Usuarios",
        "description": "Perfil de usuario, datos personales, preferencias",
        "keywords": ["usuario", "perfil", "user", "datos personales", "preferencia", "config"],
        "color": "#c0392b"
    },
    "D3-organizacion": {
        "name": "D3 - Organizaciones",
        "description": "Gestión de empresas, CUIT, datos fiscales",
        "keywords": ["organiz", "empresa", "cuit", "fiscal", "compañía", "razón social"],
        "color": "#e74c3c"
    },
    "D3-delegaciones": {
        "name": "D3 - Delegaciones",
        "description": "Delegaciones de representación, permisos por CF4",
        "keywords": ["delegac", "represent", "cf4", "permiso empresa", "autorización"],
        "color": "#c0392b"
    },
    "D3-roles-permisos": {
        "name": "D3 - Roles y Permisos",
        "description": "RBAC, roles, permisos, control de acceso",
        "keywords": ["rol", "permiso", "rbac", "acceso", "autorización", "privilegio"],
        "color": "#e74c3c"
    },
    "D4-dashboard": {
        "name": "D4 - Dashboard de Operaciones",
        "description": "Vista general, estados, métricas, notificaciones",
        "keywords": ["dashboard", "panel", "resumen", "métrica", "estado", "vista general"],
        "color": "#3498db"
    },
    "D4-operaciones": {
        "name": "D4 - Gestión de Operaciones DAI",
        "description": "CRUD de operaciones, carátula, items, oficialización, tributos",
        "keywords": ["operaci", "declarac", "dai", "carátula", "item", "oficial", "tributo", "vep", "paso", "step"],
        "color": "#2980b9"
    },
    "D4-notificacion": {
        "name": "D4 - Notificaciones",
        "description": "Alertas, notificaciones de cambios de estado, mensajes del sistema",
        "keywords": ["notificac", "alerta", "mensaje", "aviso", "cambio estado"],
        "color": "#3498db"
    },
    "D5-catalogo": {
        "name": "D5 - Catálogo de Mercaderías",
        "description": "NCM, productos, atributos, catálogo personal, nomenclador VUCE",
        "keywords": ["catálogo", "mercader", "ncm", "producto", "nomenclador", "vuce", "atributo", "favorito"],
        "color": "#f39c12"
    },
    "D6-busqueda": {
        "name": "D6 - Búsqueda de Operaciones",
        "description": "Búsqueda básica y avanzada, filtros, exportación",
        "keywords": ["búsqueda", "buscar", "filtro", "search", "export", "query", "result"],
        "color": "#9b59b6"
    },
    "D7-LPCOs": {
        "name": "D7 - LPCO (Licencias, Permisos, Certificados)",
        "description": "Gestión de LPCOs, validación, vigencia, integración con organismos",
        "keywords": ["lpco", "licencia", "permiso", "certificado", "vigencia", "organism"],
        "color": "#1abc9c"
    },
    "D8-sobre": {
        "name": "D8 - Sobre Digital",
        "description": "Documentación, adjuntos, firma digital, envío",
        "keywords": ["sobre", "document", "adjunt", "firma", "digital", "envío", "pdf"],
        "color": "#34495e"
    }
}


@dataclass
class ProposedChange:
    """Represents a proposed change to a user story or task."""
    item_type: str  # "userstory" or "task"
    item_id: int
    item_ref: int
    item_subject: str
    current_epic_ref: Optional[int]
    current_epic_name: Optional[str]
    proposed_epic: str  # Module key (D3, D4, etc.)
    proposed_tags: List[str]
    confidence: float  # 0.0 to 1.0
    reason: str


class AIReorganizer:
    """AI-powered reorganizer for Taiga projects."""

    def __init__(self):
        self.modules = MODULE_DEFINITIONS

    def _calculate_module_score(self, text: str, module_key: str) -> float:
        """Calculate how well a text matches a module based on keywords."""
        if not text:
            return 0.0

        text_lower = text.lower()
        module = self.modules[module_key]
        keywords = module["keywords"]

        # Count keyword matches
        matches = sum(1 for keyword in keywords if keyword in text_lower)

        # Normalize by number of keywords
        score = matches / len(keywords) if keywords else 0.0

        # Boost score if module name appears in text
        if module_key.lower() in text_lower:
            score += 0.3

        return min(score, 1.0)

    def _infer_module(self, subject: str, description: Optional[str] = None) -> tuple[str, float]:
        """Infer the best module for a user story or task."""
        combined_text = subject
        if description:
            combined_text += " " + description

        scores = {}
        for module_key in self.modules:
            scores[module_key] = self._calculate_module_score(combined_text, module_key)

        # Get best match
        best_module = max(scores, key=scores.get)
        confidence = scores[best_module]

        return best_module, confidence

    def _generate_tags(self, subject: str, module_key: str) -> List[str]:
        """Generate suggested tags based on subject and module."""
        tags = []
        subject_lower = subject.lower()

        # Priority tags
        if any(word in subject_lower for word in ["p0", "crítico", "bloqueante"]):
            tags.append("prioridad:alta")
        elif any(word in subject_lower for word in ["p1"]):
            tags.append("prioridad:media")
        elif any(word in subject_lower for word in ["p2", "nice"]):
            tags.append("prioridad:baja")

        # Status tags
        if any(word in subject_lower for word in ["mvp", "kickoff", "minimo"]):
            tags.append("mvp")

        if any(word in subject_lower for word in ["testing", "test", "e2e"]):
            tags.append("testing")

        if any(word in subject_lower for word in ["integ", "integración"]):
            tags.append("integración")

        # Module-specific tags
        if module_key.startswith("D3"):
            if "delegac" in subject_lower:
                tags.append("delegaciones")
            if "rol" in subject_lower or "permiso" in subject_lower:
                tags.append("rbac")
            if "auth" in subject_lower or "login" in subject_lower:
                tags.append("autenticación")
        elif module_key.startswith("D4"):
            if "dashboard" in subject_lower:
                tags.append("dashboard")
            if "notif" in subject_lower:
                tags.append("notificaciones")
            if "oficial" in subject_lower:
                tags.append("oficialización")
            if "operaci" in subject_lower:
                tags.append("operaciones")
        elif module_key.startswith("D5"):
            if "ncm" in subject_lower:
                tags.append("ncm")
            if "catálogo" in subject_lower or "catalogo" in subject_lower:
                tags.append("catálogo")
        elif module_key.startswith("D7"):
            if "lpco" in subject_lower:
                tags.append("lpco")
        elif module_key.startswith("D8"):
            if "sobre" in subject_lower:
                tags.append("sobre-digital")

        # Tech stack tags
        if any(word in subject_lower for word in ["frontend", "ui", "pantalla", "component"]):
            tags.append("frontend")
        if any(word in subject_lower for word in ["backend", "endpoint", "api"]):
            tags.append("backend")

        return tags

    def analyze_project(self, epics: List, orphan_user_stories: List) -> Dict:
        """
        Analyze current project structure and generate reorganization proposals.

        Args:
            epics: List of Epic ORM objects with user_stories and tasks
            orphan_user_stories: List of UserStory ORM objects without epic

        Returns:
            Dict with analysis and proposals
        """
        proposals = []
        statistics = {
            "total_items": 0,
            "items_needing_change": 0,
            "modules_proposed": {},
            "confidence_avg": 0.0
        }

        # Épicas de gestión que no se deben reorganizar
        MANAGEMENT_EPICS = [
            "requerimientos vuce",
            "gestión técnica y operativa interna",
            "gestion tecnica y operativa interna"
        ]

        # Analyze user stories in epics
        for epic in epics:
            # Skip management epics
            epic_name_lower = epic.subject.lower() if epic.subject else ""
            if any(mgmt_epic in epic_name_lower for mgmt_epic in MANAGEMENT_EPICS):
                continue
            for us in epic.user_stories:
                statistics["total_items"] += 1

                # Infer best module for this US
                proposed_module, confidence = self._infer_module(
                    us.subject,
                    us.description
                )

                # Generate tags
                proposed_tags = self._generate_tags(us.subject, proposed_module)

                # Check if change is needed
                epic_matches_module = (
                    proposed_module in epic.subject if epic.subject else False
                )

                if not epic_matches_module or confidence > 0.5:
                    statistics["items_needing_change"] += 1
                    statistics["modules_proposed"][proposed_module] = \
                        statistics["modules_proposed"].get(proposed_module, 0) + 1

                    proposals.append(ProposedChange(
                        item_type="userstory",
                        item_id=us.id,
                        item_ref=us.ref,
                        item_subject=us.subject,
                        current_epic_ref=epic.ref,
                        current_epic_name=epic.subject,
                        proposed_epic=proposed_module,
                        proposed_tags=proposed_tags,
                        confidence=confidence,
                        reason=f"Detectado contenido relacionado con {self.modules[proposed_module]['name']}"
                    ))

        # Analyze orphan user stories
        for us in orphan_user_stories:
            statistics["total_items"] += 1
            statistics["items_needing_change"] += 1

            proposed_module, confidence = self._infer_module(us.subject, us.description)
            proposed_tags = self._generate_tags(us.subject, proposed_module)

            statistics["modules_proposed"][proposed_module] = \
                statistics["modules_proposed"].get(proposed_module, 0) + 1

            proposals.append(ProposedChange(
                item_type="userstory",
                item_id=us.id,
                item_ref=us.ref,
                item_subject=us.subject,
                current_epic_ref=None,
                current_epic_name="(Sin épica)",
                proposed_epic=proposed_module,
                proposed_tags=proposed_tags,
                confidence=confidence,
                reason=f"US huérfana - asignar a {self.modules[proposed_module]['name']}"
            ))

        # Calculate average confidence
        if proposals:
            statistics["confidence_avg"] = sum(p.confidence for p in proposals) / len(proposals)

        return {
            "proposals": proposals,
            "statistics": statistics,
            "modules": self.modules
        }
