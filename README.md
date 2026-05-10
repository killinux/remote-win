# Blender-MCP Remote Relay

通过 HTTP 中继让 Claude Code 远程操控另一台 Windows 机器上的 Blender，同时隐藏客户端 IP。

## 架构原理

```
Claude Code (本机)
    │ POST /command
    ▼
server.py (:8080, 0.0.0.0 支持直连)
    ▲ 也可通过 nginx 反向代理（剥离客户端 IP 头）
    │
nginx (:8081, 0.0.0.0 对外，隐藏客户端 IP)
    ▲ 轮询 GET /commands/pending
    │
win_client.py (远程 Windows)  ← IP 被 nginx 隐藏
    │ socket
    ▼
Blender + blender-mcp (:9876, 远程 Windows)
```

### 工作流程

1. Claude Code 向本机 `server.py` 发送命令（`POST /command`）
2. `server.py` 将命令放入内存队列，返回命令 ID
3. 远程 `win_client.py` 通过 nginx（:8081）轮询 `GET /commands/pending`
4. 拿到命令后，`win_client.py` 通过 socket 转发给本地 Blender 的 blender-mcp 插件（:9876）
5. Blender 执行完毕，`win_client.py` 将结果 `POST /command/{id}/response` 回传
6. Claude Code 轮询 `GET /command/{id}` 获取结果

### IP 隐藏机制

远程客户端的 IP 通过多层保护被隐藏：

| 层级 | 措施 | 效果 |
|------|------|------|
| server.py | `get_request` 覆盖，丢弃客户端地址 | 无论直连还是经 nginx，server 都看不到真实 IP |
| server.py | `log_message` 被禁用 | 不输出任何请求日志 |
| nginx | `proxy_set_header X-Forwarded-For ""` | 清除转发头 |
| nginx | `access_log off` | 不记录客户端访问日志 |

无论客户端直连 :8080 还是经 nginx :8081，`server.py` 内部看到的 `client_address` 始终是 `0.0.0.0`，真实 IP 从未进入应用层。

## 快速启动

### 本机（中继服务器）

```powershell
# 1. 启动中继
python server.py --port 8080

# 2. 确保 nginx 已运行（8081 → 8080）
```

### 远程 Windows（Blender 机器）

```powershell
# 1. 启动 Blender，启用 blender-mcp 插件
# 2. 启动客户端
python win_client.py --server http://<本机IP>:8081
```

## API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/command` | 提交命令（JSON body） |
| GET  | `/commands/pending` | 客户端轮询待处理命令 |
| GET  | `/command/{id}` | 查询命令状态和结果 |
| POST | `/command/{id}/response` | 客户端回传 Blender 执行结果 |
| GET  | `/status` | HTML 状态面板（自动刷新） |
| GET  | `/api/status` | JSON 状态（`win_connected` 表示客户端在线） |

## 使用示例

```powershell
# 发送命令
$body = @{
    type = "execute_code"
    params = @{ code = "import bpy; print(bpy.data.objects.keys())" }
} | ConvertTo-Json
$r = Invoke-RestMethod -Method Post -Uri "http://localhost:8080/command" -Body $body -ContentType "application/json"

# 等待并获取结果
Start-Sleep 3
Invoke-RestMethod -Uri "http://localhost:8080/command/$($r.id)"

# 检查连接状态
Invoke-RestMethod -Uri "http://localhost:8080/api/status" | ConvertTo-Json
```

## 注意事项

- 命令 1 小时后自动过期清理
- 客户端 10 秒内有轮询即视为在线（`win_connected`）
- `BlenderBridge` 超时 180 秒，执行大型命令期间 `win_connected` 会暂时变 false
- 远程 Blender 中**禁止**使用 `read_factory_settings`，会断开 blender-mcp 链路
- 命令长期卡在 `processing` 说明远程 Blender MCP 端口 (9876) 不通
