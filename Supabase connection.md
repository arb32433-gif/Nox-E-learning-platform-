# Supabase Connection

## Server (Build APIs)

### 1. Install package

Add `@supabase/server` to your backend.

```bash
npm install @supabase/server
```

> On Edge Functions you can import it directly, no install needed.

### 2. Set environment variables

Copy these into your environment so your handler can verify users and use supabase-js.

```env
SUPABASE_URL=https://bfsnraigvxktrqpwsbwh.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_kaC29ACuczGkiVlk973Afw_MHFzdZ2J
SUPABASE_SECRET_KEY=sb_secret_GO0-n••••••••••••••••••••
SUPABASE_JWKS_URL=https://bfsnraigvxktrqpwsbwh.supabase.co/auth/v1/.well-known/jwks.json
```

> On Edge Functions these are injected automatically. For other runtimes, copy the values above. Manage keys in API Keys settings.

### 3. Install the Supabase Server skill (optional)

Give AI coding tools instructions for building APIs with `@supabase/server`.

```bash
npx skills add supabase/server
```

## Session Pooler

### 1. Connection string

Copy the connection details for your database.

- **Shared pooler** — if your database password contains special characters, percent-encode them in the connection string.
- **Connection parameters**
  - host: `aws-0-ap-northeast-2.pooler.supabase.com`
  - port: `5432`
  - database: `postgres`
  - user: `postgres.bfsnraigvxktrqpwsbwh`

```bash
postgresql://postgres.bfsnraigvxktrqpwsbwh:[YOUR-PASSWORD]@aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres
```

### 2. Install Agent Skills (optional)

Agent Skills give AI coding tools ready-made instructions, scripts, and resources for working with Supabase more accurately and efficiently.

```bash
npx skills add supabase/agent-skills
```
