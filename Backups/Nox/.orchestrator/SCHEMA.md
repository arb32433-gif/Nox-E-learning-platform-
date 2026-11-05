# Data and API Contracts

Source of truth: `server/db/schema.js`, `server/db/migrations/*.sql`, `server/app.js`, and `server/routes/*.js`. If this summary disagrees, source wins. The journal records migrations through `0005` then `0007`; `0006_rbac_normalized.sql` exists but is not journaled.
Last verified against: 2026-10-30.

## Database

Column notation: `?` means nullable; otherwise the Drizzle column is `.notNull()`. Defaults and references are stated where defined in Drizzle. Numeric money uses precision 14, scale 4. Physical money column names depend on `MONEY_SCHEMA_VERSION` (`server/lib/moneyStorage.js`).

| Table | Columns (application identifier: SQL column, type, nullability/default) | Keys/relations |
|---|---|---|
| `users` | `id`: uuid, PK/random; `username`: text; `email`: text?; `passwordHash`: text/`password_hash`; `role`: text; `isActive`: boolean/`is_active`, default true; `lastLoginAt`: timestamptz?; `createdBy`: uuid?; `createdAt`: timestamptz, now | `createdBy` → `users.id`; indexes `users_email_idx`, `users_username_idx` |
| `products` | `id`: uuid, PK/random; `name`: text; `description`: text?; `category`: text; `price`: numeric?; `stockQty`: integer/`stock_qty`, default 0; `lowStockThreshold`: integer/`low_stock_threshold`, default 0; `dailyLimit`: integer/`daily_limit`?; `imagePath`: text/`image_path`?; `isActive`: boolean, default true; `isSample`: boolean, default false; `createdAt`, `updatedAt`: timestamptz, now | `price` SQL column is `price` in major mode, otherwise `price_cents`; category/active index |
| `orders` | `id`: uuid, PK/random; `orderNumber`: text; `flowType`: text/`flow_type`; `status`: text, default `placed`; `total`: numeric, default 0; `paymentStatus`: text, default `pending`; `payoutStatus`: text, default `pending`; `customerName`: text?; `customerContact`: text?; `notes`: text?; `productionDate`: date; `createdAt`, `updatedAt`: timestamptz, now | `orderNumber` unique; status/created and flow/created indexes; `total` SQL column is `total` or `total_cents` by money mode |
| `order_items` | `id`: uuid, PK/random; `orderId`: uuid/`order_id`; `productId`: uuid/`product_id`; `quantity`: integer; `unitPrice`: numeric; `subtotal`: numeric | `orderId` → `orders.id` on delete cascade; `productId` → `products.id`; money SQL names switch to `_cents` in legacy mode |
| `dine_in_queue` | `id`: uuid, PK/random; `orderId`: uuid, unique; `queueNumber`: integer; `position`: integer; `status`: text, default `waiting`; `calledAt`, `completedAt`: timestamptz? | `orderId` → `orders.id`; status/position index |
| `pickup_slots` | `id`: uuid, PK/random; `orderId`: uuid, unique; `pickupDate`: date; `pickupTime`: time; `slotCapacity`: integer, default 5; `confirmedAt`: timestamptz? | `orderId` → `orders.id`; date/time index |
| `payments` | `id`: uuid, PK/random; `orderId`: uuid; `amount`: numeric; `method`: text; `status`: text, default `pending`; `confirmedAt`: timestamptz?; `createdAt`: timestamptz, now | `orderId` → `orders.id`; amount SQL name is `amount` or `amount_cents` by money mode |
| `payouts` | `id`: uuid, PK/random; `orderId`: uuid; `amount`: numeric; `status`: text, default `pending`; `completedAt`: timestamptz? | `orderId` → `orders.id`; amount SQL name is `amount` or `amount_cents` by money mode |
| `inventory_adjustments` | `id`: uuid, PK/random; `productId`: uuid; `delta`: integer; `reason`: text; `userId`: uuid?; `createdAt`: timestamptz, now | `productId` → `products.id`; `userId` → `users.id` |

Drizzle's `schema.js` declares no PostgreSQL enum types. Status/role fields are text; application-level identifiers and transition rules are in `.orchestrator/CONTEXT.md` and `server/lib/`.

## RLS and migration notes

- Migration `0007_single_shop.sql` removes tenant policies/columns/tables and revokes direct table privileges from Supabase `anon` and `authenticated` roles; it comments that RLS remains enabled without policies. Verify live state independently before relying on that migration having run.
- `0006_rbac_normalized.sql` inserts into `permissions`, `roles`, and `role_permissions`, but those tables are not in current Drizzle `schema.js` and this file is absent from `_journal.json`. Its prerequisites/application state are unresolved; do not document those as current schema.
- Migration `0007` adds global unique index `orders_order_number_unique` and indexes `users_email_idx`, `users_username_idx`.

## API

All paths are rooted at `/api`; JSON request parsing is limited to 100 KB. Staff-only endpoints require a valid active-user session plus the listed permission. `Public` means no staff permission guard appears on that route. Error envelopes are route-specific; common guard errors are `{error, code}`. Exact payload details are in the linked route source; do not infer omitted fields.

| Method + path | Request → response | Auth |
|---|---|---|
| `GET /health` | none → `{status, service, time}` | Public |
| `GET /ready` | none → ready JSON or 503 not-ready JSON | Public |
| `POST /auth/register` | `{email,password,name?,username?,role?}` → `{ok,user,permissions,accessLevel,message}`; role defaults to cashier if unrecognized | Public route; registration gates are in source |
| `POST /auth/login` | `{email}` or `{username}`, `password` → `{user,permissions,accessLevel}`; sets session cookie | Public route; lockout enforced |
| `POST /auth/logout` | none → `{ok:true}`; clears cookie | Public route |
| `GET /auth/me` | none → safe user object with `permissions`, or 401 | Session required by handler |
| `PATCH, PUT /auth/me` | `{username}`/`{name}`, `email`, and/or `{newPassword}`/`{password}`; password may use `currentPassword` → `{ok,user,permissions,accessLevel}` | Session required by handler |
| `GET /users` | none → safe user array (`id,username,email,role,isActive,createdAt`) | `users:view` plus admin role |
| `GET /users/:id` | id → safe user object | `users:view` plus admin role |
| `POST /users` | user fields → created safe user | `users:create` plus admin role |
| `PATCH /users/:id` | user patch → updated safe user | `users:update` plus admin role |
| `POST /users/:id/deactivate` | id → see `server/routes/users.js` | `users:deactivate` plus admin role |
| `DELETE /users/:id` | id → see `server/routes/users.js` | admin role |
| `GET /products`, `GET /products/:id` | optional `all=true` / id → product array/object; public queries return active products only | Public; `all=true` requires `products:view` |
| `POST /products` | product fields (`name`, `category`, `price`, optional description/image/stock/threshold/daily limit) → 201 product | `products:create` |
| `PUT, PATCH /products/:id` | product patch → updated product | `products:update` |
| `DELETE /products/:id` | id → archived product JSON or delete result; see `server/routes/products.js` for branch | `products:delete` |
| `POST /orders` | `flowType`/`flow_type`, nonempty `items` (`productId`/`product_id`, `quantity`/`qty`); pre-order also needs `pickupDate`/`pickup_date`, `pickupTime`/`pickup_time`; optional customer fields/notes → 201 order JSON | Public pre-order; otherwise staff session with `orders:create` |
| `GET /orders` | optional `status`, `flowType`/`flow_type` query → order array | `orders:view` |
| `GET /orders/track/:reference` | public order reference → `{status}` | Public; rate limited |
| `GET /orders/:id` | path → order with `items` | `orders:view` |
| `PATCH /orders/:id` | customer/name/contact/notes patch → order JSON | `orders:update` |
| `PATCH /orders/:id/status` | `{status}` → order JSON | `orders:update_status` |
| `POST /orders/:id/cancel` | path → cancelled order JSON | `orders:cancel` |
| `DELETE /orders/:id` | path → `{ok:true,deletedId,orderNumber}` | `orders:cancel` |
| `GET /orders/:id/payments` | path → payment array | `payments:view` |
| `POST /orders/:id/payments` | `{amount, method}` → 201 payment | `payments:confirm` |
| `POST /orders/:id/payments/verify` | `{method?, amount?, confirmPayout?, confirmPickup?, referenceNumber?, cashTendered?, changeGiven?, notes?, completeOrder?}` → `{success, order, payment, payout}` | `payments:confirm` |
| `PATCH /orders/:id/payments/:id/confirm` | nested order/payment path → confirmed payment; both router layers name the parameter `id` | `payments:confirm` |
| `GET /orders/:id/payouts` | path → payout array | `payouts:view` |
| `POST /orders/:id/payouts` | `{amount}` → 201 payout | `payouts:complete` |
| `PATCH /orders/:id/payouts/:id/complete` | nested order/payout path → completed payout; both router layers name the parameter `id` | `payouts:complete` |
| `GET /orders/:id/pickup` | order id → one pickup slot | `pickups:view` |
| `POST /orders/:id/pickup` | `{pickupDate, pickupTime}` (snake_case aliases accepted) → 201 slot; 409 if full/already booked | `orders:update` |
| `PATCH /orders/:id/pickup/confirm` | order id → confirmed slot | `pickups:confirm` |
| `GET /pickup-slots/availability` | required `date=YYYY-MM-DD` → availability JSON | Public |
| `GET /pickup-slots` | optional `date`, `orderId` → ordered slot array | `pickups:view` |
| `PATCH /pickup-slots/:id/confirm` | path → slot JSON | `pickups:confirm` |
| `GET /queue`, `GET /queue/:id` | optional status / path → queue JSON | `queue:view` |
| `POST /queue/:id/call` | path → queue entry | `queue:call` |
| `POST /queue/:id/complete` | path → queue entry | `queue:complete` |
| `PATCH /queue/:id` | `{position}` → queue entry | `queue:reorder` |
| `GET /inventory` | optional `productId` (or `product_id`) → adjustment array | `inventory:alerts_view` |
| `GET /inventory/low-stock` | none → active products at/below threshold | `inventory:alerts_view` |
| `POST /inventory` | `{productId}` (or `product_id`), integer `delta`, optional `reason` → 201 `{product, adjustment}` | `inventory:adjust` |
| `GET /reports/sales` | optional `group=day|week|month`, `from`, `to` → `[{bucket,total,count}]` | `reports:view` |
| `GET /reports/summary` | optional `from`, `to` → gross/order totals, categories, channels | `reports:view` |
| `GET /reports/queue-stats` | none → `[{status,count}]` | `reports:view` |
| `POST /upload` | multipart field `file`, max 5 MB, image formats jpeg/jpg/png/webp/gif → `{url,filename,size,mimetype}` | Any of `products:create`, `products:update`, `users:update` |

## Secret/config key names

From `.env.example` only; values are intentionally excluded: `PORT`, `ALLOW_SUPABASE_DEV_DATABASE`, `DATABASE_URL`, `MONEY_SCHEMA_VERSION`, `SESSION_SECRET`, `NODE_ENV`, `FRONTEND_ORIGINS`, `BOOTSTRAP_ADMIN_EMAIL`, `BOOTSTRAP_ADMIN_PASSWORD`, `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SECRET_KEY`, `SUPABASE_JWKS_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`.
