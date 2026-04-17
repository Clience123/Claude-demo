# Claude-demo

一个最小可运行的 Claude Opus 服务示例。

## 启动

```bash
export ANTHROPIC_API_KEY="your_api_key"
python claude_opus_service.py
```

默认监听 `127.0.0.1:8000`，可通过环境变量修改：

- `HOST`（默认 `127.0.0.1`）
- `PORT`（默认 `8000`）
- `CLAUDE_MODEL`（默认 `claude-opus-4-1`）

## 接口

### 健康检查

```bash
curl http://127.0.0.1:8000/health
```

### Claude Opus 对话

```bash
curl -X POST http://127.0.0.1:8000/claude/opus/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "你好，介绍一下你自己"}],
    "max_tokens": 256,
    "temperature": 0.7
  }'
```
