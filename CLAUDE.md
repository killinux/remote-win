# Blender-MCP 远程中继系统

## 架构

Windows（本机）运行 `server.py` 作为 HTTP 中继服务器。Mac 客户端轮询中继并通过 blender-mcp 转发命令到 Blender，然后将结果回传。

```
Claude Code  -->  server.py (Windows :8080)  <--轮询--  Mac 客户端  -->  Blender
```

## 启动中继服务器

```powershell
Start-Process -FilePath "python" -ArgumentList "server.py","--port","8080" -WorkingDirectory "C:\Users\Administrator\Desktop\winwork\remote-win" -NoNewWindow
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/command` | 提交命令到 Blender（JSON 请求体） |
| GET | `/commands/pending` | Mac 客户端轮询待处理命令 |
| GET | `/command/{id}` | 查询命令状态和结果 |
| POST | `/command/{id}/response` | Mac 客户端回传执行结果 |
| GET | `/status` | HTML 状态面板（自动刷新） |
| GET | `/api/status` | JSON 状态（mac_connected、队列计数） |

## 发送命令

```powershell
# 提交命令
$body = @{ type = "execute_code"; params = @{ code = "import bpy; print(bpy.data.objects.keys())" } } | ConvertTo-Json
$r = Invoke-RestMethod -Method Post -Uri "http://localhost:8080/command" -Body $body -ContentType "application/json"

# 轮询结果
Start-Sleep -Seconds 2
Invoke-RestMethod -Uri "http://localhost:8080/command/$($r.id)"
```

也可以用 `send.py` 辅助脚本发送 Python 文件：

```powershell
python send.py <python脚本文件> [超时秒数]
```

## 检查状态

```powershell
Invoke-RestMethod -Uri "http://localhost:8080/api/status" | ConvertTo-Json
```

关键字段：`mac_connected`（是否连接）、`queue.pending`（待处理）、`queue.processing`（处理中）、`queue.completed`（已完成）。

## 备注

- 服务器默认监听 `0.0.0.0:8080`（局域网可访问）
- 命令 1 小时后过期（每 5 分钟自动清理）
- Mac 客户端最后轮询在 10 秒内视为已连接

---

# RGBA 式胸部物理弹跳

## 原理

参考 [RGBA式おっぱい剛体](https://rgba.blog.jp/archives/10475373.html)。

原版 RGBA 方案在 MMD 中利用 Bullet 求解器的"零限制技巧"——关节限制设为 0 时，求解器精度误差会产生微小振荡。**此技巧在 Blender 中不适用**（Blender 的 Bullet 实现更精确）。

本项目采用**数学弹簧-阻尼器模拟**替代 Blender 物理，将弹跳效果直接烘焙到骨骼关键帧。

## 工作流程

1. 导入 PMX 模型（通过 mmd_tools）
2. 导入 VMD 动作
3. 记录父骨骼（上半身2）每帧的世界旋转
4. 弹簧-阻尼器模拟计算胸部骨骼的旋转偏移
5. 偏移量写入胸部骨骼关键帧

对应脚本：

```
sim_step1.py  →  导入 PMX + VMD，记录父骨骼旋转到 parent_rot.json
sim_step2.py  →  弹簧模拟 + 烘焙到骨骼关键帧
```

## 弹簧参数

```python
SPRING_K = 80.0    # 弹簧刚度（越低越松，摆幅越大）
DAMPING  = 6.0     # 阻尼系数（越低振荡越久）
MASS     = 1.0     # 质量（越大反应越迟钝）
SCALE    = 3.0     # 结果放大倍数（直接控制可见幅度）
DT       = 1/30    # 时间步长（对应 30fps）
```

### 调参指南

| 效果 | SPRING_K | DAMPING | MASS | SCALE |
|------|----------|---------|------|-------|
| 慢摆荡（ゆっさゆっさ） | 40~60 | 6~8 | 1.5~2.0 | 2~3 |
| 蓬松弹（ふわふわ） | 80~100 | 3~4 | 1.0 | 2~3 |
| 写实/收敛 | 100~150 | 10~15 | 1.0 | 1.5~2.0 |
| 夸张 | 60~80 | 4~6 | 1.0 | 4~5 |

## RGBA_mmd 插件

`C:\Users\Administrator\Desktop\winwork\RGBA_mmd` 是 RGBA 式刚体绑定的 Blender 插件实现。通过 `install_remote.py` 安装到远程 Blender。

插件功能：自动检测胸部骨骼 → 创建 5 刚体 + 8 关节 → 调用 mmd_tools build_rig。

**注意**：由于 Blender Bullet 的限制，此插件的物理效果可能不明显。推荐使用上述数学模拟方案。

## 相关文件

| 文件 | 说明 |
|------|------|
| `server.py` | HTTP 中继服务器 |
| `send.py` | 命令发送辅助脚本 |
| `sim_step1.py` | 导入模型 + 记录父骨骼旋转 |
| `sim_step2.py` | 弹簧模拟 + 烘焙关键帧 |
| `install_remote.py` | 远程安装 RGBA_mmd 插件 |
| `stage1_import.py` | PMX 导入脚本 |

## 模型路径

- PMX: `E:\mywork\mymodel\inase (purifier)_lezisell-A\inase54.pmx`
- VMD: `E:\mywork\mymodel\yaoxiang\yaoxiang.vmd`
- 最终输出: `E:\mywork\mymodel\inase54_bounce_final.blend`
