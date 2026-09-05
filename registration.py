from nekro_agent.api.plugin import NekroPlugin

from .lifecycle import cleanup
from .matcher import forward_interceptor, handle_forward_penetration


def register(plugin: NekroPlugin) -> None:
    plugin.mount_cleanup_method()(cleanup)


__all__ = ["cleanup", "forward_interceptor", "handle_forward_penetration", "register"]
