# NekroAgent 合并转发阅读器

> 展开 OneBot 合并转发消息，保留其中的文本、图片、视频、语音和文件内容，供 NekroAgent 及后续插件继续处理。

## 快速开始

将整个 `nekro_plugin_forward` 目录复制到 NekroAgent 数据目录的插件工作区：

```text
DATA_DIR/plugins/workdir/nekro_plugin_forward/
```

确认目录中包含 `__init__.py`，然后按照 NekroAgent 的插件加载流程启动。插件只支持 OneBot V11 适配器。

## 插件结构

```text
nekro_plugin_forward/
├── __init__.py       # 插件实例、配置与包导出
├── nodes.py          # 转发节点获取、递归展开和消息段转换
├── matcher.py        # OneBot 消息拦截器
├── lifecycle.py      # 生命周期清理
└── registration.py   # 注册生命周期回调
```

## 功能说明

- 以优先级 `8` 注册 OneBot 消息拦截器。
- 展开通过 `id` 引用的合并转发节点，也处理消息中直接携带的节点内容。
- 支持递归展开，并保留非目标消息段。
- 图片、视频、语音和文件消息段会继续以原始类型传递。
- 不会阻断后续消息处理流程。

展开内容使用以下标记包围：

```text
【合并转发内容展开】
...
【合并转发内容结束】
```

## 开发

插件入口在 `__init__.py` 中定义并导出 `plugin` 实例。修改后可在本地执行语法检查：

```powershell
python -m py_compile *.py
```

完整行为需要真实的 NekroAgent、OneBot V11 和合并转发接口环境验证。

## 相关资源

- [NekroAgent 官方文档](https://doc.nekro.ai/)
- [插件开发快速上手](https://doc.nekro.ai/docs/04_plugin_dev/01_quick_start.html)
- [Nekro 插件模板](https://github.com/KroMiose/nekro-plugin-template)

## 许可证

本项目当前未单独声明许可证。
