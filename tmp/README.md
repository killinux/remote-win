# Blender-MCP Remote Relay

通过 HTTP 中继实现跨机器控制 Blender，支持 RGBA 式胸部物理弹跳烘焙。

## 架构

```
Claude Code (Windows) --> server.py (Windows :8080) <--轮询-- mac_client.py (Mac) --> Blender
```

- **Windows** 运行中继服务器 `server.py`，Claude Code 通过 HTTP 提交命令
- **Mac** 运行 `mac_client.py` 轮询中继，转发到本地 Blender（blender-mcp :9876）

## 快速开始

### 1. 启动中继服务器（Windows）

```bash
python server.py --port 8080
```

### 2. 启动 Mac 客户端（Mac）

```bash
python3 mac_client.py --server http://WINDOWS_IP:8080
```

### 3. 发送命令（Windows）

```bash
# 发送 Python 脚本到 Blender 执行
python send.py my_script.py

# 或直接用 PowerShell
$body = @{ type = "execute_code"; params = @{ code = "import bpy; print(bpy.data.objects.keys())" } } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://localhost:8080/command" -Body $body -ContentType "application/json"
```

### 4. 查看状态

浏览器打开 `http://localhost:8080/status` 查看状态面板。

## 文件说明

| 文件 | 说明 |
|------|------|
| `server.py` | HTTP 中继服务器（Windows） |
| `send.py` | 命令发送辅助脚本 |
| `win_client.py` | Windows 端 Blender 客户端 |
| `mac_client.py` | Mac 端 Blender 客户端 |
| `sim_step1.py` | 导入 PMX + VMD，记录父骨骼旋转 |
| `sim_step2.py` | 弹簧-阻尼器模拟 + 烘焙关键帧 |
| `stage1_import.py` | PMX 模型导入 |
| `install_remote.py` | 远程安装 RGBA_mmd 插件到 Blender |
| `_archive/` | 开发过程中的调试/测试脚本存档 |

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/command` | 提交命令（JSON body） |
| GET | `/commands/pending` | 客户端轮询待处理命令 |
| GET | `/command/{id}` | 查询命令状态和结果 |
| POST | `/command/{id}/response` | 客户端回传执行结果 |
| GET | `/status` | HTML 状态面板（自动刷新） |
| GET | `/api/status` | JSON 状态 |

## RGBA 式胸部物理

采用数学弹簧-阻尼器模拟替代 Blender 物理引擎，将弹跳效果烘焙到骨骼关键帧。

```bash
# 步骤 1：导入模型，记录父骨骼旋转
python send.py sim_step1.py

# 步骤 2：弹簧模拟 + 烘焙
python send.py sim_step2.py
```

### 弹簧参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| SPRING_K | 80.0 | 弹簧刚度（越低越松） |
| DAMPING | 6.0 | 阻尼系数（越低振荡越久） |
| MASS | 1.0 | 质量（越大反应越迟钝） |
| SCALE | 3.0 | 放大倍数 |

### 调参参考

| 效果 | SPRING_K | DAMPING | MASS | SCALE |
|------|----------|---------|------|-------|
| 慢摆荡 | 40~60 | 6~8 | 1.5~2.0 | 2~3 |
| 蓬松弹 | 80~100 | 3~4 | 1.0 | 2~3 |
| 写实 | 100~150 | 10~15 | 1.0 | 1.5~2.0 |
| 夸张 | 60~80 | 4~6 | 1.0 | 4~5 |
