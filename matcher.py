from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, MessageSegment

from nekro_agent.api import core

from .nodes import parse_forward_nodes

FORWARD_PRIORITY = 8
forward_interceptor = on_message(priority=FORWARD_PRIORITY, block=False)


@forward_interceptor.handle()
async def handle_forward_penetration(bot: Bot, event: MessageEvent) -> None:
    original_message = event.message
    if not any(segment.type == "forward" for segment in original_message):
        return

    core.logger.info("[Forward] 检测到合并转发消息，开始展开内容")
    expanded_message = Message()
    replaced = False
    for segment in original_message:
        if segment.type != "forward":
            expanded_message.append(segment)
            continue

        forward_id = segment.data.get("id")
        inline_content = segment.data.get("content")
        if not forward_id and not inline_content:
            expanded_message.append(segment)
            continue

        expanded_message.append(MessageSegment.text("\n【合并转发内容展开】"))
        expanded_message.extend(await parse_forward_nodes(bot, str(forward_id) if forward_id else None, inline_content))
        expanded_message.append(MessageSegment.text("\n【合并转发内容结束】\n"))
        replaced = True

    if replaced:
        event.message.clear()
        event.message.extend(expanded_message)
        core.logger.success("[Forward] 合并转发内容展开完成")
