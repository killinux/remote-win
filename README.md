# Blender-MCP Remote Relay

HTTP 中继，让任意机器上的 Claude Code 远程控制另一台机器上的 Blender。

```
Claude Code  -->  server.py (:8080)  <--轮询--  win_client.py  -->  Blender (:9876)
```

## 启动

```bash
# 1. 启动中继服务器
python server.py --port 8080

# 2. 在 Blender 所在机器启动客户端
python win_client.py --server http://SERVER_IP:8080
```

浏览器打开 `http://localhost:8080/status` 查看状态面板。

## API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/command` | 提交命令（JSON body） |
| GET  | `/commands/pending` | 客户端轮询待处理命令 |
| GET  | `/command/{id}` | 查询命令状态 |
| POST | `/command/{id}/response` | 客户端回传结果 |
| GET  | `/status` | HTML 状态面板 |
| GET  | `/api/status` | JSON 状态 |

## 发送命令示例

```powershell
$body = @{ type = "execute_code"; params = @{ code = "import bpy; print(bpy.data.objects.keys())" } } | ConvertTo-Json
$r = Invoke-RestMethod -Method Post -Uri "http://localhost:8080/command" -Body $body -ContentType "application/json"

Start-Sleep 2
Invoke-RestMethod -Uri "http://localhost:8080/command/$($r.id)"
```
