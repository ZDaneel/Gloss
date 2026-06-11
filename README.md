# Gloss

<p align="center">
  <img alt="Nuxt 3" src="https://img.shields.io/badge/Nuxt-3-00DC82?style=flat-square&logo=nuxt.js&logoColor=white"/>
  <img alt="Vue 3" src="https://img.shields.io/badge/Vue-3-4FC08D?style=flat-square&logo=vue.js&logoColor=white"/>
  <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript&logoColor=white"/>
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.112-009688?style=flat-square&logo=fastapi&logoColor=white"/>
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white"/>
  <img alt="OpenAI" src="https://img.shields.io/badge/OpenAI-API-412991?style=flat-square&logo=openai&logoColor=white"/>
</p>

<p align="center">
  An AI reading assistant for dense humanities texts — paste any passage from psychology, philosophy, or social theory, ask questions, and receive answers with inline citations that link directly to the source.
</p>

<p align="center">
  面向人文社科的 AI 精读助手 — 粘贴任意文本，提问，获取带脚注引用的回答，点击即跳转到原文。
</p>

[中文部署指南](./docs/部署指南.md) · [Deployment](#deployment)

---

## Screenshots

### Home — paste any text to start a session

![home](./docs/screenshot-home.png)

### Chat — cited answers with source passage drawer

![chat](./docs/screenshot-chat.png)

---

## Features

- **Paste any text** — no file upload required; works with excerpts, articles, book chapters
- **Inline citation footnotes** — AI answers include `[1]` `[2]` markers grounded in the source text
- **Click-to-source drawer** — click any footnote to open the exact source passage highlighted on the right
- **Real-time streaming** — responses stream token-by-token directly to the UI
- **Markdown + LaTeX rendering** — full support for formatted text, math formulas, and code blocks
- **Context control** — tune conversation history depth and temperature per session
- **Conversation management** — rename, delete, and switch between sessions; state persists across reloads
- **Screenshot export** — share any annotated conversation as an image
- **Light / Dark theme** — system-aware with manual toggle
- **i18n** — English and Chinese UI

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (Nuxt 3)                      │
│  Vue 3 · Pinia · Tailwind CSS · markdown-it · KaTeX     │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP / Streaming
┌──────────────────────▼──────────────────────────────────┐
│                  API Server (FastAPI)                     │
│  Routes · SQLAlchemy ORM · Snowflake ID · OpenAI SDK    │
└────────┬──────────────────────────────────┬─────────────┘
         │                                  │ HTTPS
┌────────▼────────┐              ┌──────────▼──────────────┐
│   PostgreSQL    │              │      OpenAI API          │
│  history        │              │  gpt-4o-mini             │
│  chats          │              │  streaming completions   │
│  resources      │              └─────────────────────────┘
└─────────────────┘
```

**Core flow:**

```
User pastes text → stored in DB
User asks question
  → full text + question → OpenAI (citation prompt)
  → streaming response with [1][2] inline markers
  → backend parses citations → stored as paragraphs[]
  → frontend renders footnotes → click opens source drawer
```

---

## Project Structure

```
Gloss/
├── gloss-web/     # Nuxt 3 frontend  (port 3006)
├── gloss-api/     # FastAPI backend   (port 3007)
├── dbscript/      # PostgreSQL init scripts
└── docs/          # Screenshots, deployment guide
```

---

## Deployment

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Node.js | ≥ 18.12 |
| pnpm | latest |
| Python | ≥ 3.10 |
| PostgreSQL | 16 |
| OpenAI API Key | — |

### 1. Database

```bash
createdb gloss
psql -d gloss -f dbscript/init.sql
```

### 2. API Server (`gloss-api/`)

```bash
cd gloss-api
cp .env.example .env
```

```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/gloss
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
CHAT_TIMEOUT=60
```

```bash
pip install -r requirements.txt
python run.py
# runs on http://localhost:3007
```

### 3. Frontend (`gloss-web/`)

```bash
cd gloss-web
cp .env.example .env
```

```env
NUXT_GLOB_API_URL=http://localhost:3007
CHAT_TIMEOUT=60000
```

```bash
pnpm install
pnpm run dev       # http://localhost:3006
```

---

## Roadmap

- [ ] PDF / Word / Markdown file upload
- [ ] Long-text support via pgvector RAG (chunk + embed + retrieve)
- [ ] Multi-document sessions with cross-text citation
- [ ] Concept graph extraction (visualize key term relationships)

---

## Acknowledgements

Data structures and TypeScript interface definitions adapted from [chatgpt-web](https://github.com/Chanzhaoyu/chatgpt-web).

---

## License

MIT © [ZDaneel](https://github.com/zdaneel)
