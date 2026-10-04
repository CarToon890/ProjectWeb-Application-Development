# Technology Stack — The Disposal Guilt

แผนภาพนี้สรุปเทคโนโลยีใน implementation ปัจจุบัน โดยแสดงช่องทาง local development และ production ที่ repo เตรียมไว้

```mermaid
flowchart TB
    BROWSER[Browser: Customer / Staff / Admin]
    subgraph FRONTEND[Frontend — static web]
      HTML[HTML5 pages]
      CSS[CSS3 responsive design]
      JS[Vanilla JavaScript ES6+]
      APIJS[fetch API wrapper + Bearer JWT]
      HTML --> CSS
      HTML --> JS
      JS --> APIJS
    end
    subgraph APP[Application layer]
      FASTAPI[FastAPI + Uvicorn]
      ROUTERS[REST routers: auth, users, items, products, bookings, staff, eco, uploads]
      SCHEMAS[Pydantic v2 schemas]
      ORM[SQLModel / SQLAlchemy]
      MIGRATIONS[Alembic migrations]
      FASTAPI --> ROUTERS
      ROUTERS --> SCHEMAS
      ROUTERS --> ORM
      MIGRATIONS --> ORM
    end
    subgraph DATA[Data and media]
      POSTGRES[(PostgreSQL 16)]
      VOLUME[Docker named volume]
      SUPABASE[(Supabase PostgreSQL / Storage — optional production integration)]
      ORM --> POSTGRES
      POSTGRES --> VOLUME
      ORM -. configured DATABASE_URL .-> SUPABASE
    end
    DOCKER[Docker Compose: web + db + pgAdmin]
    VERCEL[Vercel: static frontend + Python serverless API]
    BROWSER --> FRONTEND
    APIJS -->|HTTP JSON / multipart| FASTAPI
    FRONTEND -. local container hosting .-> DOCKER
    APP -. local container hosting .-> DOCKER
    FRONTEND -. deployment configuration .-> VERCEL
    APP -. api/index.py entrypoint .-> VERCEL
```

## รายการเทคโนโลยี

| Layer | เทคโนโลยี / หน้าที่ |
|---|---|
| UI | HTML5, CSS3, Vanilla JavaScript (ES6+) |
| API client | `fetch()`, JSON และ multipart upload, JWT Bearer token |
| Web/API | Python 3.12, FastAPI, Uvicorn |
| Validation and data access | Pydantic v2, SQLModel, SQLAlchemy |
| Database | PostgreSQL 16; Supabase PostgreSQL ใช้ได้ผ่าน `DATABASE_URL` |
| Schema changes | Alembic |
| Authentication | JWT (`python-jose`) และ bcrypt (`passlib`) |
| Image storage | Local volume ใน dev หรือ Supabase Storage เมื่อกำหนดค่า |
| Local runtime | Docker, Docker Compose, pgAdmin |
| Deployment path | Vercel rewrites + Python serverless function; ต้องตั้งค่า database/JWT/storage secrets ใน deployment environment |

## Runtime paths

- **Local:** `docker compose up --build` รัน FastAPI และ PostgreSQL; FastAPI เสิร์ฟหน้าเว็บและ `/api/*` จาก origin เดียวกัน
- **Vercel:** `vercel.json` ส่ง `/api/*` ไป `api/index.py` และเสิร์ฟไฟล์ frontend แบบ static; ใช้ Supabase หรือ PostgreSQL ที่เข้าถึงได้จาก serverless runtime
- ไฟล์ `.env.example` เป็นตัวอย่างสำหรับพัฒนาในเครื่องเท่านั้น ควรใช้ secrets จริงผ่าน environment ของ deployment และไม่ commit ไฟล์ `.env`

