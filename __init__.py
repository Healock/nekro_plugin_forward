from nekro_agent.api import core
from nekro_agent.api.plugin import ConfigBase, NekroPlugin


plugin = NekroPlugin(
    name="合并转发阅读器",
    module_name="nekro_plugin_forward",
    description="展开 OneBot 合并转发消息，保留媒体与文件节点供后续插件处理。",
    version="1.0.2",
    author="Healock",
    url="https://github.com/Healock/nekro_plugin_forward",
    support_adapter=["onebot_v11"],
)


@plugin.mount_config()
class ForwardConfig(ConfigBase):
    pass


config = plugin.get_config(ForwardConfig)

core.logger.info("[Forward] 插件已加载，消息拦截优先级：8")

from .nodes import parse_forward_nodes

__all__ = [
    "ForwardConfig",
    "cleanup",
    "config",
    "forward_interceptor",
    "handle_forward_penetration",
    "parse_forward_nodes",
    "plugin",
]

from . import registration as _registration  # noqa: E402, F401

_registration.register(plugin)
from .registration import cleanup, forward_interceptor, handle_forward_penetration  # noqa: E402, F401
