# Blender-MCP 远程中继

Windows 运行 `server.py` 作为 HTTP 中继，客户端 `win_client.py` 轮询中继并转发命令到本地 Blender。

```
Claude Code  -->  server.py (:8080)  <--轮询--  win_client.py  -->  Blender (:9876)
```

## 启动

```powershell
Start-Process -FilePath "python" -ArgumentList "server.py","--port","8080" -WorkingDirectory "C:\Users\Administrator\Desktop\winwork\remote-win" -NoNewWindow
```

## 发送命令

```powershell
$body = @{ type = "execute_code"; params = @{ code = "import bpy; print(bpy.data.objects.keys())" } } | ConvertTo-Json
$r = Invoke-RestMethod -Method Post -Uri "http://localhost:8080/command" -Body $body -ContentType "application/json"
Start-Sleep 2
Invoke-RestMethod -Uri "http://localhost:8080/command/$($r.id)"
```

## 检查状态

```powershell
Invoke-RestMethod -Uri "http://localhost:8080/api/status" | ConvertTo-Json
```

## 备注

- 服务器监听 `0.0.0.0:8080`（局域网可访问）
- 命令 1 小时后过期
- 客户端最后轮询在 10 秒内视为已连接
- 远程 Blender 中**禁止**使用 `read_factory_settings`，会断开 blender-mcp 链路
