from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment
from nonebot.exception import AdapterException

from nekro_agent.api import core

MAX_FORWARD_DEPTH = 3
MEDIA_SEGMENT_TYPES = frozenset({"image", "video", "record", "file"})


def _as_segment(value: Any) -> MessageSegment | None:
    if isinstance(value, MessageSegment):
        return value
    if not isinstance(value, Mapping):
        return None

    segment_type = value.get("type")
    if not isinstance(segment_type, str) or not segment_type:
        return None
    data = value.get("data", {})
    if not isinstance(data, Mapping):
        data = {}
    try:
        return MessageSegment(segment_type, dict(data))
    except (TypeError, ValueError) as exc:
        core.logger.warning("[Forward] 消息段重建失败：类型=%s，原因=%s", segment_type, exc)
        return None


def _normalize_content(content: Any) -> list[MessageSegment]:
    if isinstance(content, Message):
        return list(content)
    if isinstance(content, str):
        try:
            return list(Message(content))
        except (TypeError, ValueError):
            return [MessageSegment.text(content)]
    if isinstance(content, Mapping):
        content = [content]
    if not isinstance(content, Iterable):
        return []

    normalized: list[MessageSegment] = []
    for item in content:
        segment = _as_segment(item)
        if segment is not None:
            normalized.append(segment)
        elif isinstance(item, str):
            normalized.extend(_normalize_content(item))
    return normalized


def _node_sender(node: Mapping[str, Any]) -> str:
    if node.get("type") == "node" and isinstance(node.get("data"), Mapping):
        data = node["data"]
        sender = data.get("name") or data.get("uin")
    else:
        sender_data = node.get("sender")
        if isinstance(sender_data, Mapping):
            sender = sender_data.get("card") or sender_data.get("nickname")
        else:
            sender = node.get("name") or node.get("uin")
    return str(sender) if sender else "未知用户"


def _node_content(node: Mapping[str, Any]) -> Any:
    if node.get("type") == "node" and isinstance(node.get("data"), Mapping):
        return node["data"].get("content", [])
    return node.get("content") or node.get("message") or []


async def _fetch_nodes(bot: Bot, forward_id: str | None, inline_content: Any) -> list[Any]:
    if isinstance(inline_content, Sequence) and not isinstance(inline_content, (str, bytes)) and inline_content:
        return list(inline_content)
    if not forward_id:
        return []

    try:
        forward_data = await bot.call_api("get_forward_msg", id=forward_id)
    except AdapterException as exc:
        core.logger.warning("[Forward] 获取转发详情失败：ID=%s，原因=%s", forward_id, exc)
        raise

    if isinstance(forward_data, Mapping):
        nodes = forward_data.get("messages") or forward_data.get("message") or []
    elif isinstance(forward_data, list):
        nodes = forward_data
    else:
        nodes = []
    return list(nodes) if isinstance(nodes, Iterable) and not isinstance(nodes, (str, bytes)) else []


def _unknown_segment_text(segment: MessageSegment) -> MessageSegment:
    return MessageSegment.text(f"【消息段：{segment.type}】")


async def _parse_forward_nodes(
    bot: Bot,
    forward_id: str | None = None,
    inline_content: Any = None,
    current_depth: int = 1,
    max_depth: int = MAX_FORWARD_DEPTH,
) -> Message:
    result = Message()
    if current_depth > max_depth:
        result.append(MessageSegment.text("\n【嵌套转发已截断】已达到最大展开层级。\n"))
        return result

    nodes = await _fetch_nodes(bot, forward_id, inline_content)
    if not nodes:
        result.append(MessageSegment.text("\n【转发详情为空】记录可能已过期。\n"))
        return result

    for raw_node in nodes:
        if not isinstance(raw_node, Mapping):
            continue
        result.append(MessageSegment.text(f"\n{_node_sender(raw_node)}："))
        for segment in _normalize_content(_node_content(raw_node)):
            if segment.type == "forward":
                nested_id = segment.data.get("id")
                nested_content = segment.data.get("content")
                if nested_id or nested_content:
                    result.append(MessageSegment.text("\n【嵌套转发展开】\n"))
                    result.extend(
                        await parse_forward_nodes(
                            bot,
                            str(nested_id) if nested_id else None,
                            nested_content,
                            current_depth + 1,
                            max_depth,
                        )
                    )
                    result.append(MessageSegment.text("\n【嵌套转发结束】\n"))
            elif segment.type == "text" or segment.type in MEDIA_SEGMENT_TYPES:
                result.append(segment)
            else:
                result.append(_unknown_segment_text(segment))
    return result


async def parse_forward_nodes(
    bot: Bot,
    forward_id: str | None = None,
    inline_content: Any = None,
    current_depth: int = 1,
    max_depth: int = MAX_FORWARD_DEPTH,
) -> Message:
    try:
        return await _parse_forward_nodes(bot, forward_id, inline_content, current_depth, max_depth)
    except Exception as exc:
        core.logger.error("[Forward] 转发节点解析失败：ID=%s，原因=%s", forward_id, exc)
        result = Message()
        result.append(MessageSegment.text("\n【转发解析失败】消息内容无法展开。\n"))
        return result
