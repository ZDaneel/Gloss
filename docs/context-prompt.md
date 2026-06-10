# Gloss — 新对话上下文 Prompt

将以下内容复制到新对话开头，作为背景说明。

---

## 项目背景

我正在开发一个叫 **Gloss** 的全栈 Web 应用，是一个面向人文社科（心理学、哲学、社会学）的 AI 精读助手。

**核心功能**：用户粘贴一段文本，然后提问，AI 返回带有脚注标记 `[1][2]` 的回答，点击脚注会在右侧抽屉中高亮显示对应的原文片段。

---

## 技术栈

- **前端**：Nuxt 3 + Vue 3 + TypeScript + Pinia + Tailwind CSS + DaisyUI
- **后端**：Python + FastAPI + SQLAlchemy + PostgreSQL
- **AI**：OpenAI API（`gpt-4o-mini`，流式输出）
- **项目路径**：`c:\Vscode-Project\Gloss\`

```
Gloss/
├── gloss-web/     # Nuxt 3 前端（port 3006）
├── gloss-api/     # FastAPI 后端（port 3007）
├── dbscript/      # PostgreSQL 初始化脚本
└── docs/
```

---

## 当前状态

仓库已从旧项目（Theris，一个论文问答系统）复制改造而来，**代码结构完整但尚未适配新功能**，具体来说：

- 后端仍在调用旧的 Mock 模型服务（`mock_url`），需要替换为 OpenAI API
- 前端首页仍是文件上传 + 链接输入的 UI，需要改为文本粘贴框
- `openai==1.42.0` 已在 `requirements.txt` 中，无需额外安装

---

## 需要实现的改动

### 后端（`gloss-api/`）

#### 1. `app/core/config.py`

删除 `mock_url`、`upload_dir`、`paragraph_timeout`，新增 `openai_api_key` 和 `openai_model`：

```python
class Settings(BaseSettings):
    database_url: str
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    chat_timeout: int = 60

    class Config:
        env_file = ".env"
```

#### 2. `app/api/v1/endpoints/chat.py`

将转发给 Mock 服务的 HTTP 调用，替换为 OpenAI 流式调用：

```python
from openai import AsyncOpenAI
from app.core.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

CITATION_PROMPT = """你是一个人文社科文本阅读助手，帮助用户深入理解心理学、哲学、社会学等领域的文本。

规则：
1. 只根据用户提供的原文回答，不引入外部知识
2. 回答中必须用 [1][2] 等标注引用来源
3. 回答结束后，另起一行，按顺序列出引用的原文片段：
   [1]: "原文中的具体语句"
   [2]: "原文中的具体语句"

回答语言与用户问题保持一致。"""
```

流式调用替换原来的 `httpx` 调用：

```python
async def call_openai_stream(question, source_text, past_qa, temperature):
    messages = [{"role": "system", "content": CITATION_PROMPT}]
    # 加入历史对话上下文
    for q, a in zip(past_qa["questions"], past_qa["answers"]):
        messages.append({"role": "user", "content": q})
        messages.append({"role": "assistant", "content": a})
    messages.append({
        "role": "user",
        "content": f"原文：\n{source_text}\n\n问题：{question}"
    })
    stream = await client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=temperature,
        stream=True,
    )
    async for chunk in stream:
        yield chunk.choices[0].delta.content or ""
```

#### 3. `app/api/v1/endpoints/paragraphs.py`

不再调用 Mock 服务，改为从数据库取出原文，用正则解析 AI 回答中的 `[n]: "..."` 格式：

```python
import re

def parse_citations(response_text: str) -> list[str]:
    pattern = r'\[\d+\]:\s*["""](.*?)["""]'
    return re.findall(pattern, response_text, re.DOTALL)
```

实际调用时，先从 `resources` 表取出 `resource_name`（即粘贴的原文），拼入 prompt，OpenAI 返回完整内容后解析脚注。

#### 4. `app/api/v1/endpoints/resources.py`

去掉文件上传和链接验证逻辑，只保留「存储粘贴文本」：

```python
class TextRequest(BaseModel):
    uuid: int
    content: str    # 粘贴的原文

@router.post("/upload-text/")
async def upload_text(request: TextRequest, db: Session = Depends(get_db)):
    # 存入 resources 表，is_file=False，resource_name=content
    ...
```

---

### 前端（`gloss-web/`）

#### 1. `pages/index.vue`（首页）

把文件上传 + 链接输入的 UI，替换为两个文本框：

```
┌─────────────────────────────────────────┐
│  粘贴你的文本...（大 textarea，多行）       │
│                                          │
│                                          │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│  输入你的第一个问题...                     │
└─────────────────────────────────────────┘
                                  [开始解读]
```

#### 2. `api/index.ts`

删除 `uploadPDF`、`uploadLink`、`removePDF`、`removeLink`，新增：

```typescript
export const uploadText = (data: { uuid: number; content: string }) =>
  request({ url: '/resources/upload-text/', method: 'POST', data })
```

其余接口（`fetchChatAPIProcess`、`fetchParagraphAPI`、`fetchLikeAPI`）保持不变。

---

## 关键设计决策（已确定，不要改变）

1. **v1 不做段落检索**：直接把全文塞进 context 发给 OpenAI，文本不超过 30 页时够用
2. **脚注解析方式**：OpenAI 返回的完整文本里，用正则匹配 `[n]: "..."` 提取，存入 `paragraphs[]` 字段
3. **前端脚注联动**：前端已有完整的 `data-id` 点击 → 抽屉高亮机制，**不需要改**
4. **流式传输**：后端用 `StreamingResponse + AsyncGenerator`，前端用 Axios `onDownloadProgress`，**不需要改**
5. **数据库 Schema 不变**：`resources.resource_name` 用来存粘贴的原文，`is_file=False`

---

## 后端现有文件结构参考

```
gloss-api/app/
├── api/
│   ├── main.py                        # 路由聚合
│   └── v1/endpoints/
│       ├── chat.py                    # 对话流式接口（需改）
│       ├── paragraphs.py              # 段落获取接口（需改）
│       └── resources.py               # 资源管理接口（需改）
├── core/
│   └── config.py                      # 环境变量配置（需改）
├── db/
│   ├── crud/chat_crud.py              # 数据库 CRUD（不改）
│   ├── models/chat_models.py          # ORM 模型（不改）
│   └── session.py                     # DB 会话（不改）
├── models/
│   ├── chat_schemas.py                # Pydantic schemas（小改）
│   └── web_models.py                  # 网络模型（小改）
└── main.py                            # FastAPI 入口（不改）
```

---

## 请从以下任务开始

**第一步：修改 `gloss-api/app/core/config.py`，删除旧配置，加入 OpenAI 相关变量。**

然后依次：
1. 改 `resources.py`，实现 `upload-text` 接口
2. 改 `chat.py`，用 OpenAI 流式替换 Mock 调用
3. 改 `paragraphs.py`，从 AI 返回里解析脚注
4. 改前端 `pages/index.vue`，换成文本粘贴 UI
5. 改前端 `api/index.ts`，替换 API 调用
