# Theris — Frontend

Nuxt 3 frontend for the Theris academic paper Q&A system.

See the [root README](../README.md) for full project documentation and deployment instructions.

## Dev

```bash
pnpm install
pnpm run dev        # http://localhost:3006
```

## Build

```bash
pnpm run build
pnpm run preview
```

## Environment

Copy `.env.example` to `.env` before starting:

```env
NUXT_GLOB_API_URL=http://localhost:3007
PARAGRAPH_TIMEOUT=60000
CHAT_TIMEOUT=60000
```
