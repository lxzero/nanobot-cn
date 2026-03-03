# 工具使用说明

工具签名通过函数调用自动提供。本文件记录使用规范和限制。

## 通用原则

- 修改文件前，先用 `read_file` 确认当前内容
- 优先用 `edit_file` 局部修改，避免 `write_file` 全量覆盖
- 执行操作后，检查返回值确认是否成功

## exec

- 超时默认 60 秒，超时后进程被强制终止
- 输出截断至 10,000 字符
- 被屏蔽的危险模式：`rm -rf`、`format`、`dd if=`、`mkfs`、`diskpart`、`shutdown`、`reboot`、fork bomb
- `restrictToWorkspace` 开启时，禁止 `../` 路径穿越和工作区外的绝对路径
- 可选 `working_dir` 参数指定命令执行目录

## read_file / write_file / edit_file / list_dir

- 相对路径基于工作区目录解析
- `edit_file` 的 `old_text` 必须在文件中唯一匹配；出现多次时需提供更多上下文使其唯一
- `write_file` 会自动创建父目录

## message

- `content`（必需）：消息文本
- `media`（可选）：本地文件路径列表，作为附件发送。路径必须是真实存在的文件，不要编造
- `channel` / `chat_id`（可选）：不指定时使用当前会话的频道和用户

## web_search

- 参数：`query`（必需）、`count`（可选，1-10）
- 返回搜索结果的标题、URL 和摘要

## web_fetch

- 参数：`url`（必需）、`extractMode`（可选，`markdown` 或 `text`）、`maxChars`（可选）
- 仅支持 http/https 协议
- 返回 JSON，包含 `text`（提取的内容）、`url`、`status`、`truncated` 等字段

## cron

原生工具，直接调用，不要通过 `exec` 运行 shell 命令。不要直接编辑 `jobs.json` 文件。

- `action`（必需）：`add` | `list` | `remove` | `update`
- `add`：需要 `message` + 调度方式（`cron_expr` / `every_seconds` / `at` 三选一）；可选 `name`、`deliver`、`tz`
- `update`：需要 `job_id`，只传要修改的字段（`message`、`deliver`、`enabled`、调度参数等）
- `remove`：需要 `job_id`
- 修改任务时用 `update`，不要 remove + add
