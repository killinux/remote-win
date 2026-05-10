# Blender-MCP 远程中继

本机运行 `server.py` 作为 HTTP 中继，远程 Windows 机器上的 `win_client.py` 通过 nginx 轮询中继并转发命令到远程 Blender。

## 架构

```
Claude Code (本机)
    ↓ POST /command
server.py (:8080, 本机)
    ↑ nginx 反向代理
nginx (:8081, 本机, 0.0.0.0)
    ↑ 轮询 GET /commands/pending
win_client.py (远程 Windows)
    ↓ socket
Blender + blender-mcp (:9876, 远程 Windows)
```

## 网络说明

- `server.py` 监听 `0.0.0.0:8080`（支持直连或通过 nginx）
- nginx 监听 `0.0.0.0:8081`，反向代理到 `127.0.0.1:8080`，对外暴露此端口供远程客户端连接
- 远程 `win_client.py` 连接 `http://本机IP:8081`，隐藏远程机器 IP
- nginx 配置位于 `C:\nginx-1.26.3\conf\nginx.conf`

## 启动（本机）

```powershell
# 1. 启动中继服务器
Start-Process -FilePath "python" -ArgumentList "server.py","--port","8080" -WorkingDirectory "C:\Users\Administrator\Desktop\winwork\remote-win" -NoNewWindow

# 2. nginx 已作为服务运行（8081 → 8080）
```

远程 Windows 需要：启动 Blender → 启用 blender-mcp 插件 → 运行 `win_client.py --server http://本机IP:8081`

## 发送命令

```powershell
$body = @{ type = "execute_code"; params = @{ code = "import bpy; print(bpy.data.objects.keys())" } } | ConvertTo-Json
$r = Invoke-RestMethod -Method Post -Uri "http://localhost:8080/command" -Body $body -ContentType "application/json"
Start-Sleep 3
Invoke-RestMethod -Uri "http://localhost:8080/command/$($r.id)"
```

## 检查状态

```powershell
# JSON 状态（win_connected 表示远程客户端是否在线）
Invoke-RestMethod -Uri "http://localhost:8080/api/status" | ConvertTo-Json

# HTML 状态面板
# 浏览器打开 http://localhost:8080/status
```

## 备注

- 命令 1 小时后过期
- 客户端最后轮询在 10 秒内视为已连接（`win_connected`）
- 远程 Blender 中**禁止**使用 `read_factory_settings`，会断开 blender-mcp 链路
- `win_client.py` 的 `BlenderBridge` 超时 180 秒，期间会阻塞轮询导致 `win_connected` 变 false
- 如果命令长期卡在 `processing`，说明远程 Blender MCP 端口 (9876) 不通
