# Architecture Context

Source of truth: implementation files listed below; if this summary disagrees, implementation wins. Planning docs describe proposals unless code confirms them.
Last verified against: 2026-10-30.

## Product and runtime
- One configured shop and one PostgreSQL database; no tenant provisioning or tenant scoping in the current application (`README.md`, `server/db/migrations/0007_single_shop.sql`).
- Frontend: Vite HTML, CSS, and vanilla JS under `src/`; staff admin routes are migrating to a persistent host at `src/Assets/Admin panel/Admin.html`, with legacy page documents temporarily mounted in its workspace. API: Express app in `server/app.js`, routes in `server/routes/`.
- Supabase-managed PostgreSQL is the application's database platform. Drizzle schema is `server/db/schema.js`; migrations live in `server/db/migrations/`.
- Vite proxies `/api` to `http://localhost:3000` (`vite.config.js`).

## Roles and authorization
- Role identifiers: `admin`, `manager`, `cashier`, `baker`, `kitchen`, `delivery` (`server/lib/permissions.js`). `kitchen` receives the baker permission set. `admin` receives all declared permissions.
- `manager`, `cashier`, `baker`/`kitchen`, and `delivery` receive explicit subsets in `server/lib/permissions.js`; consult that file for exact membership. Do not infer authority from role labels or UI visibility.
- `authMiddleware` reads the configured session cookie or a Bearer token, verifies JWT, reloads an active user, and computes permissions (`server/middleware/auth.js`). Route guards return 401 when unauthenticated and 403 when disallowed.
- Customers may create pre-orders and look up an order by reference without staff authentication. Dine-in order creation requires staff authentication (`server/routes/orders.js`).

## State and business rules
- Order status identifiers: `placed`, `queued`, `confirmed`, `preparing`, `ready`, `completed`, `cancelled` (`server/lib/orderWorkflow.js`). Allowed role transitions and cancellation/edit eligibility are encoded there; consult it before changing transitions.
- Dine-in queue statuses currently written by route handlers: `waiting` → `serving` → `done` (`server/routes/orders.js`, `server/routes/queue.js`).
- Payment statuses written by routes: `pending`, `confirmed`; order `paymentStatus` uses `pending`, `paid` (`server/routes/payments.js`).
- Payout statuses written by routes: `pending`, `completed`; order `payoutStatus` uses the same values (`server/routes/payouts.js`, `server/routes/payments.js`).
- Pre-orders require valid `pickupDate` and normalized `pickupTime`; production date defaults to the current Asia/Manila date (`server/lib/productionDate.js`, `server/lib/pickup.js`). Slot capacity and product daily limits are enforced at order creation (`server/routes/orders.js`).
- Order creation checks stock and records an inventory adjustment; cancellation restores stock through the cancellation handler (`server/routes/orders.js`). Do not assume stock and production capacity are interchangeable.
- Monetary storage is environment-dependent: `MONEY_SCHEMA_VERSION=major` selects major units; otherwise `legacy` selects legacy cents-named columns. API serializers convert stored values (`server/lib/moneyStorage.js`).

## Boundaries and conventions
- API mounting and middleware order are in `server/app.js`; shared auth guards are in `server/middleware/auth.js`; role permissions and order transition rules are in `server/lib/permissions.js` and `server/lib/orderWorkflow.js`.
- Database access uses Drizzle tables from `server/db/schema.js`; route handlers live in one file per domain under `server/routes/`.
- UI uses one HTML file per screen with matching CSS; CSS files are canonical screen specifications. Preserve Obsidian wikilinks in Markdown (`README.md`).
- Route handlers generally catch and pass errors to `next(err)`; shared error serialization is `server/middleware/errorHandler.js`.
- Follow existing JavaScript ES module style and ESLint configuration (`package.json`, `eslint.config.js`).

## Authority and known conflict
- Migration journal `server/db/migrations/meta/_journal.json` lists `0005_daily_production_limits` followed by `0007_single_shop`; `0006_rbac_normalized.sql` exists but is absent from that journal. This is unresolved; do not infer it was applied.
- The database connection safety checks and README warn that the live migration journal/schema may not match the current app; do not run database-changing commands without a specifically authorized, safe target.
