# Nox – Database Structure

E-learning platform data model. Source of truth for persisting the state currently held in `localStorage` (`nox-portal`, `nox-v2`) and the in-app content (`MODS`, `MISSIONS`, `BOARD`).

## Conventions

- Primary keys: `id` UUID (`gen_random_uuid()`), except where a natural key is noted.
- Timestamps: `timestamptz`, default `now()`; soft-delete via `deleted_at`.
- All user-facing text fields are `text`; slugs/codes are `varchar(n)`.
- Foreign keys use `ON DELETE CASCADE` for owned child rows, `ON DELETE SET NULL` for optional references.
- JSONB only for genuinely variable payloads (lesson ideas, mission metadata).

## Core entities

### users

Accounts and identity. Replaces the demo `nox-portal` session gate.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | uuid | PK | |
| email | citext | UNIQUE, NOT NULL | login identifier |
| password_hash | text | NOT NULL | nullable only for SSO-only accounts |
| display_name | varchar(64) | | derived from email local-part by default |
| callsign | varchar(16) | UNIQUE | leaderboard handle; regex `^[A-Za-z0-9_-]{3,16}$` |
| avatar_initial | char(1) | | cached first char of callsign/user |
| email_verified_at | timestamptz | | |
| status | varchar(16) | NOT NULL default 'active' | active / suspended / deleted |
| created_at | timestamptz | NOT NULL default now() | |
| updated_at | timestamptz | NOT NULL default now() | |
| last_login_at | timestamptz | | |

### sessions

Auth sessions (replaces `nox-portal` `{user, remember, session}`).

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | uuid | PK | session token id |
| user_id | uuid | FK users(id) CASCADE, NOT NULL | |
| token_hash | text | UNIQUE, NOT NULL | hashed bearer token |
| remember | boolean | NOT NULL default false | |
| expires_at | timestamptz | NOT NULL | `now() + 8h` (matches `SESSION_MS`) |
| created_at | timestamptz | NOT NULL default now() | |
| revoked_at | timestamptz | | soft revoke |
| user_agent | text | | |
| ip_address | inet | | |

Index: `(user_id, expires_at)`.

### modules

Course modules (from `MODS`).

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | uuid | PK | |
| slug | varchar(32) | UNIQUE, NOT NULL | e.g. `m1-foundations` |
| position | smallint | NOT NULL | display order (1-based) |
| title | text | NOT NULL | |
| subtitle | text | | |
| description | text | | |
| tag | varchar(32) | | "Everyone" / "Builders" |
| total_minutes | integer | NOT NULL default 0 | sum of lesson minutes |
| published | boolean | NOT NULL default true | |
| created_at | timestamptz | NOT NULL default now() | |
| updated_at | timestamptz | NOT NULL default now() | |

### lessons

Lessons belonging to a module (from `MODS[].lessons`).

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | uuid | PK | |
| module_id | uuid | FK modules(id) CASCADE, NOT NULL | |
| code | varchar(8) | NOT NULL | natural key e.g. `1.1`, `2.3` (unique within module) |
| position | smallint | NOT NULL | order within module |
| title | text | NOT NULL | |
| subtitle | text | | |
| body | text | NOT NULL | long-form content |
| minutes | smallint | NOT NULL | estimated minutes |
| tag | varchar(32) | | "Everyone" / "Builders" |
| premium | boolean | NOT NULL default false | maps to `p:2` |
| ideas | jsonb | NOT NULL default '[]' | key ideas list |
| try_prompt | text | | "Try it" exercise |
| created_at | timestamptz | NOT NULL default now() | |
| updated_at | timestamptz | NOT NULL default now() | |

Unique: `(module_id, code)`. Index: `(module_id, position)`.

### lesson_progress

Per-user completion of lessons (replaces `S.done[]`).

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | uuid | PK | |
| user_id | uuid | FK users(id) CASCADE, NOT NULL | |
| lesson_id | uuid | FK lessons(id) CASCADE, NOT NULL | |
| completed | boolean | NOT NULL default true | toggled (done/undo) |
| completed_at | timestamptz | | set when completed=true |
| updated_at | timestamptz | NOT NULL default now() | |

Unique: `(user_id, lesson_id)`. Index: `(user_id)`.

### user_course_state

Per-user UI/navigation state (replaces `S` minus auth/progress).

| Column | Type | Constraints | Notes |
|---|---|---|---|
| user_id | uuid | PK, FK users(id) CASCADE | |
| current_view | varchar(16) | NOT NULL default 'overview' | overview/modules/module/lesson/practice/board/profile/signin |
| current_module_id | uuid | FK modules(id) SET NULL | |
| current_lesson_id | uuid | FK lessons(id) SET NULL | |
| updated_at | timestamptz | NOT NULL default now() | |

For anonymous users, this state lives in `localStorage` only.

### missions

Practice missions (from `MISSIONS`).

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | uuid | PK | |
| slug | varchar(64) | UNIQUE, NOT NULL | |
| position | smallint | NOT NULL | |
| title | text | NOT NULL | |
| description | text | NOT NULL | |
| points | integer | NOT NULL | |
| tag | varchar(32) | | audience tag |
| metadata | jsonb | NOT NULL default '{}' | sample data, difficulty, etc. |
| published | boolean | NOT NULL default true | |
| created_at | timestamptz | NOT NULL default now() | |

### mission_attempts

User attempts at missions (currently only toasts; full version tracks).

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | uuid | PK | |
| user_id | uuid | FK users(id) CASCADE, NOT NULL | |
| mission_id | uuid | FK missions(id) CASCADE, NOT NULL | |
| status | varchar(16) | NOT NULL default 'started' | started / completed / abandoned |
| score | integer | | |
| started_at | timestamptz | NOT NULL default now() | |
| completed_at | timestamptz | | |

Index: `(user_id, mission_id)`.

### leaderboard_entries

Public leaderboard (from `BOARD` + user callsign).

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | uuid | PK | |
| user_id | uuid | FK users(id) CASCADE, UNIQUE, NOT NULL | one entry per user |
| callsign | varchar(16) | NOT NULL | denormalized for read speed |
| points | integer | NOT NULL default 0 | derived: `completed_lessons * 100` + mission points |
| rank | integer | | cached rank; recompute on update |
| updated_at | timestamptz | NOT NULL default now() | |

Index: `(points DESC)`.

### badges (optional, future)

Achievement badges.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | uuid | PK | |
| slug | varchar(64) | UNIQUE, NOT NULL | |
| title | text | NOT NULL | |
| description | text | | |
| icon | text | | asset path |
| criteria | jsonb | NOT NULL default '{}' | e.g. `{lessons_completed: 5}` |

### user_badges

| Column | Type | Constraints | Notes |
|---|---|---|---|
| user_id | uuid | FK users(id) CASCADE, NOT NULL | |
| badge_id | uuid | FK badges(id) CASCADE, NOT NULL | |
| awarded_at | timestamptz | NOT NULL default now() | |

PK: `(user_id, badge_id)`.

## Relationships

```
users 1--* sessions
users 1--1 user_course_state
users 1--* lesson_progress *--1 lessons
users 1--* mission_attempts *--1 missions
users 1--1 leaderboard_entries
users *--* badges  (via user_badges)
modules 1--* lessons
```

## Derived views

- `user_progress_summary`: per user, total lessons, completed, percent, minutes remaining.
- `leaderboard_view`: ranked callsigns with points, excluding users without a callsign.

## Migration notes

- Seed `modules`, `lessons`, `missions` from `MODS`/`MISSIONS` constants.
- Backfill `lesson_progress` from each user's `S.done[]` array on first sync.
- Promote `nox-portal` sessions into `sessions` rows with `expires_at = session`.
- Compute `leaderboard_entries.points = count(completed lessons)*100 + sum(mission points)`.

## Indexes summary

- `users(email)` unique, `users(callsign)` unique.
- `sessions(user_id, expires_at)`, `sessions(token_hash)` unique.
- `lessons(module_id, position)`, `lessons(module_id, code)` unique.
- `lesson_progress(user_id)`, `lesson_progress(user_id, lesson_id)` unique.
- `mission_attempts(user_id, mission_id)`.
- `leaderboard_entries(points DESC)`.

## Security

- Passwords hashed with Argon2id; never store plaintext.
- Session tokens stored hashed; raw token only in cookie.
- Email never exposed on leaderboard (only callsign).
- Soft-delete users sets `status='deleted'` and anonymizes callsign.

---

Related: [[Nox - The Web-based E-learning platform]] · [[Documentation Template (Structure).md]]
Tags: #docs #database #schema #elearning
Status: Draft
Date: 2026-11-04
Agent/tool: opencode
