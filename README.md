# 知识库问答助手

任务 4-4 交付包：FastAPI + Ollama + SQLite 向量检索 + 原生 HTML/JavaScript。
支持普通聊天、知识库问答、检索来源展示和文档列表查看。

## 1. 项目目录

```text
knowledge-assistant/
├── backend/
│   ├── main.py              # 后端接口与首页入口
│   ├── build_kb.py          # 读取资料、切分文本并构建向量索引
│   ├── requirements.txt     # Python 依赖
│   └── kb_docs/             # UTF-8 编码的 .md/.txt 资料
│       ├── 项目说明.md
│       └── 接口说明.md
├── frontend/
│   └── index.html           # 模式切换、聊天、文档列表页面
├── .gitignore
└── README.md
```

首次构建知识库后会生成 `backend/kb.db`。模型文件由 Ollama 管理，不放进项目压缩包。

## 2. 环境准备

- Python 3.10 或更高版本；本次验证使用 Windows + Python 3.12.8。
- 安装并启动 [Ollama](https://ollama.com/download)。
- 使用 Edge、Chrome 等现代浏览器。此项目不需要 Node.js 或单独的前端服务器。
- 第一次下载模型和安装 Python 依赖需要网络。

先解压整个项目文件夹，再在 `knowledge-assistant` 文件夹中打开终端。
下文命令除特别说明外，均从项目根目录执行。

检查 Python 与 Ollama：

```powershell
python --version
ollama --version
```

如果 `python` 打开 Microsoft Store，说明当前命令没有指向实际解释器。
可在 PyCharm 中选中已安装的 Python 环境，再使用该环境的终端；也可用 Python 的完整路径执行。

下载两个指定模型：

```powershell
ollama pull qwen2.5:7b
ollama pull bge-m3
ollama list
```

`ollama list` 中应能看到两个模型。Ollama 通常通过桌面应用在后台运行；
如果没有运行，可在另一个终端执行 `ollama serve` 并保持该终端开启。
如果提示 11434 端口已占用，先检查是否已有 Ollama 服务正在运行。

## 3. Windows 启动步骤

首次启动，在项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe backend\build_kb.py
.\.venv\Scripts\python.exe backend\main.py
```

这些命令依次创建项目环境、安装依赖、构建知识库并启动服务；某一步报错时，先处理该错误再继续。
直接调用虚拟环境中的 Python，无需激活脚本或修改 PowerShell 执行策略。

看到 `Uvicorn running on http://127.0.0.1:8000` 后，在浏览器打开：

**[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

后端必须保持运行。前端由 FastAPI 自动提供，不要直接双击 HTML 或用 PyCharm 的 HTML 预览地址打开。
开发时也可以从项目根目录运行：

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

两种启动方式任选一种。使用 `python backend/main.py` 时，修改后端代码后需要停止并重新运行。
停止当前终端中的服务使用 Ctrl+C；如果从 PyCharm 启动，则使用该运行窗口的停止按钮。

后续启动（模型、依赖与索引都已准备好）只需：

```powershell
.\.venv\Scripts\python.exe backend\main.py
```

如果 8000 端口已有你之前的练习服务，请先在原运行窗口停止它；或者使用上面的 uvicorn 命令，
将 `--port 8000` 改成 `--port 8001`，并访问 `http://127.0.0.1:8001/`。

## 4. macOS / Linux / WSL 启动步骤

先安装并启动同一环境中的 Ollama，并下载上述两个模型，然后从项目根目录执行：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
.venv/bin/python backend/build_kb.py
.venv/bin/python backend/main.py
```

浏览器同样访问 `http://127.0.0.1:8000/`。该平台步骤尚未在本次 Windows 环境外实测。

## 5. 体验与验收

1. 选择“普通聊天”，发送“你好，请用一句话介绍自己”。应收到模型生成的回答。
2. 点击“查看知识库文档”，应显示项目说明、接口说明两个文件。
3. 选择“知识库聊天”，提问“项目使用什么聊天模型和向量模型？”。
   应回答 `qwen2.5:7b` 和 `bge-m3`，并展示命中的来源与相似度分数；具体措辞可能变化。
4. 在知识库模式提问“报销审批需要几天？”。示例资料未包含该信息，模型应说明资料不足。

验证文档更新：

1. 用 UTF-8 编码在 `backend/kb_docs` 新建 `演示规则.txt`，写入“本项目的演示口令是蓝色松树。”。
2. 在另一个终端、项目根目录执行构建脚本：

   ```powershell
   .\.venv\Scripts\python.exe backend\build_kb.py
   ```

3. 等待显示“知识库构建完成”，然后在知识库模式提问“本项目的演示口令是什么？”。
   应回答“蓝色松树”，并出现新文件来源。
4. 构建脚本会重建 `backend/kb.db` 中的索引，原始文档保留。构建期间先暂停提问，完成后再继续。

文件列表按钮只查看目录，不能证明文件已入索引。问答读取的是最近一次构建生成的 `kb.db`。

## 6. 接口约定

| 方法与路径 | 用途 |
| --- | --- |
| `GET /` | 打开网页 |
| `POST /chat` | 普通聊天 |
| `POST /rag_chat` | 检索资料后聊天 |
| `GET /kb_docs` | 查看文档目录 |

两个聊天接口统一接收：

```json
{"question": "项目使用什么模型？", "session_id": "demo001"}
```

`question` 必填且不能全为空白；`session_id` 可省略，由后端生成并返回。
成功响应字段是 `mode`、`session_id`、`question`、`answer` 和 `sources`。
来源条目包含 `id`、`title`、`score`，普通聊天的 `sources` 为空数组。
`score` 是真实余弦相似度，越大表示向量越相似，不代表答案正确率。

调试接口请打开 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)。

## 7. 常见问题

| 现象 | 检查方法 |
| --- | --- |
| 页面请求返回 404 | 确认从 8000 端口首页打开，并在 `/docs` 检查接口；HTML 预览地址可能请求到别的服务 |
| 聊天返回 422 | 请求字段必须叫 `question`，且内容不能全为空白 |
| 返回 502 | 检查 Ollama 是否运行、两个模型是否已下载；在 `/docs` 中查看响应的 `detail` |
| 知识库聊天返回 503 | 查看 `/docs` 的错误详情，确认已成功运行 `backend/build_kb.py` |
| 出现端口占用错误 | 在原运行窗口停止旧服务，或使用不同端口启动并访问对应地址 |
| 添加文档后回答没变 | 重新运行构建脚本，等构建完成后再次提问 |
| 第一次回答较慢 | 模型需要加载到内存，页面在收到完整结果前显示“回答中…” |

## 8. 当前实现范围

- 普通聊天和知识库问答都实际调用本地模型；没有固定演示回答。
- 当前使用一次性 JSON 响应，未接入流式输出。
- `session_id` 目前只用于请求与响应标识；没有保存、读取历史消息，多轮记忆尚未实现。
- 检索最多返回三个片段，没有最低相似度阈值；来源表示检索命中，不能保证每条都被回答使用。
- 文档内容不足时通过提示词要求模型明确说明，仍需人工核对答案。
- 只解析 UTF-8 的 `.md`、`.txt` 文档，不解析 PDF 或 Word；目录列表可能显示其他文件，但它们不会被构建脚本索引。

## 9. 3 分钟讲解提纲

“用户在网页选择模式并输入问题，JavaScript 的 fetch 将 JSON 发给 FastAPI。
普通聊天直接调用 Ollama 的 qwen2.5:7b。知识库聊天先用 bge-m3 把问题转成向量，
与 SQLite 中保存的文档向量计算余弦相似度，取最多三个片段，连同问题一起发给聊天模型。
后端把回答和来源按统一格式返回，网页显示出来。更新资料后运行构建脚本，索引才会更新。”

## 10. 参考文档

- [Ollama 官方入门](https://docs.ollama.com/quickstart)
- [FastAPI 启动服务说明](https://fastapi.tiangolo.com/deployment/manually/)

## 11. 本次验证记录

2026-09-09，在 Windows + Python 3.12.8 新建虚拟环境并按 requirements.txt 安装依赖。
将压缩包解压到独立目录，在没有 kb.db 的情况下构建索引，并启动真实 HTTP 服务。
首页、文档列表、接口定义、普通聊天和知识库聊天均通过检查。
模型实际回答了项目使用 `qwen2.5:7b` 和 `bge-m3`。
另在测试副本中新增演示资料、重建索引后，成功回答“蓝色松树”并返回新资料来源。

验证复用了本机已安装的 Ollama 和模型，未重新下载模型；未自动操作浏览器点击按钮，
前端交互请按第 5 节手动验收。交付包不含测试副本中的临时文档、数据库或虚拟环境。
