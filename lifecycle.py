from nonebot.matcher import matchers

from nekro_agent.api import core

from .matcher import forward_interceptor


async def cleanup() -> None:
    """卸载 OneBot 匹配器，避免插件重载后重复触发。"""
    for priority, registered_matchers in list(matchers.items()):
        matchers[priority] = [matcher for matcher in registered_matchers if matcher != forward_interceptor]
    core.logger.info("[Forward] 资源清理完成，Matcher 已卸载。")
