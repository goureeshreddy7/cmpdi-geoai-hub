# 🚀 Deploying CMPDI GeoAI Hub to Vercel (100% Free)

This backend is designed with a hybrid architecture:
- **Local Development**: Runs 100% free with SQLite, local disk storage, and ChromaDB.
- **Vercel Cloud**: Serverless execution via `api/index.py` and `vercel.json`.

---

## ⚡ Step-by-Step Vercel Deployment

### 1. Import Project to Vercel
1. Log in to [vercel.com](https://vercel.com).
2. Click **Add New...** → **Project**.
3. Select your GitHub repository: **`goureeshreddy7/cmpdi-geoai-hub`**.
4. Framework Preset: **Other**.
5. Root Directory: `./` (leave default).

---

### 2. Configure Environment Variables
In the **Environment Variables** section on Vercel, add:

| Variable | Value | Description |
|---|---|---|
| `GEMINI_API_KEY` | `AQ.Ab8RN6...` | Your Google Gemini API Key |
| `GEMINI_MODEL` | `gemini-3.8-flash` | Primary AI model |
| `JWT_SECRET` | `any-random-long-secret-key-12345` | Secret key for signing login JWTs |

#### **Optional Free Cloud Databases (For Multi-User Cloud Persistence):**
If you want persistent multi-user database and file storage in the cloud for free:
- **Neon PostgreSQL (Free)**: [neon.tech](https://neon.tech) → Create free DB → Paste connection string as `DATABASE_URL`.
- **Supabase Storage (Free)**: [supabase.com](https://supabase.com) → Create bucket `cil-documents` → Add `SUPABASE_URL` and `SUPABASE_KEY`.
- **Google OAuth (Free)**: Add `GOOGLE_CLIENT_ID` from Google Cloud Console for 1-tap Google Login.

*(If you don't provide these, the app will run locally with SQLite and local storage).*

---

### 3. Click Deploy
Click **Deploy**! In about 1 minute, your backend will be live at:
`https://your-project.vercel.app`

Interactive Swagger API Documentation will be live at:
`https://your-project.vercel.app/docs`
