# 安全编码规范（Sprint 0 Day 3）

> 文档 D：外部进程、路径、凭据、错误处理

## 1. 外部进程调用

### 安全写法

```python
import subprocess

result = subprocess.run(
    ["ffmpeg", "-y", "-i", input_file, "-c:v", "libx264", output_file],
    capture_output=True,
    text=True,
    timeout=600,
    check=False,
)
```

视频引擎统一入口：`cursor-novel-video/engine/scripts/subprocess_safe.py` → `run_command()`。

### 禁止写法

```python
# 字符串拼接 + shell=True — 命令注入
subprocess.run(f"ffmpeg -i {user_input} out.mp4", shell=True)

# 无 timeout — 可能永久挂起
subprocess.run(["ffmpeg", ...])
```

## 2. 文件路径

- 使用 `novel_suite.core.path_safety` / `assert_project_in_allowed_roots`
- 禁止把未校验的用户字符串拼进路径或 shell

## 3. 凭据

- 通过 `novel_suite.core.env_config` 或 `os.getenv` 读取
- 默认值必须为空或 localhost URL，不能是真实 API Key
- 见 `.env.example`；`.env` 已在 `.gitignore`

## 4. 错误处理

- 捕获 `subprocess.TimeoutExpired` 并返回 Result Contract 错误
- 文件操作捕获 `OSError`
- 禁止裸 `except: pass`

## 5. Prompt 注入（Day 4）

- 输入：`core/sanitizer.sanitize_prompt_input`
- 模板：`core/prompt_template.safe_prompt`
- 输出：`core/sanitizer.filter_llm_output`
