# Backend ↔ Frontend Communication Guide

How the FastAPI backend (`../app`, built layer by layer per `../demomanual/layer_1.md`–
`layer_5.md`) and this Quasar frontend actually talk to each other — endpoint by endpoint, file
by file, request by request. Each backend layer is paired with the exact Vue file(s) that consume
it, with real code from both sides and a step-by-step trace of what happens on the wire.

This is reference material, not a setup guide — see [`README.md`](README.md) for getting the app
running. Read this to understand *why* a given Vue file is shaped the way it is, in terms of the
specific backend endpoint it's talking to.

## Contents

0. [How the Two Sides Talk](#0-how-the-two-sides-talk)
1. [Authentication — Login, Session, Logout](#1-authentication--login-session-logout)
2. [Routing & Role-Based UI](#2-routing--role-based-ui)
3. [Layer 1 — Foundation & Reference Data](#3-layer-1--foundation--reference-data)
4. [Layer 2 — Identity & Access](#4-layer-2--identity--access)
5. [Layer 3 — Account Configuration](#5-layer-3--account-configuration)
6. [Layer 4 — Transactions](#6-layer-4--transactions)
7. [Layer 5 — Financial Records & Ledger](#7-layer-5--financial-records--ledger)
8. [Customer Self-Service Pages](#8-customer-self-service-pages)
9. [Full Endpoint ↔ Page Reference Table](#9-full-endpoint--page-reference-table)
10. [Known Gaps & Things to Watch](#10-known-gaps--things-to-watch)

---

## 0. How the Two Sides Talk

Every request from the frontend to the backend is plain HTTP, JSON in both directions — with one
exception (login, covered in §1). The frontend has exactly one axios instance, shared by every
page:

**[`src/services/api.js`](src/services/api.js)** (full file):
```js
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.QCLI_API_BASE_URL || 'http://127.0.0.1:8000',
})

export default api
```

Two interceptors wrap every request/response through it — **[`src/boot/axios.js`](src/boot/axios.js)**:
```js
api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      const auth = useAuthStore()
      auth.logout()
      router.push('/login')
    }
    return Promise.reject(error)
  }
)
```

- **Request side:** if a token is stored, every outgoing request gets `Authorization: Bearer
  <token>` attached automatically. Pages never set this header themselves.
- **Response side:** any `401` from *any* endpoint clears the session and bounces to `/login`,
  globally — no page needs its own 401 handling.
- **CORS:** `app/main.py` runs `CORSMiddleware` with `allow_origins=["*"]`, which is why the Vite
  dev server (a different origin/port than the backend) is allowed to call it at all.

> **Important — read before building on top of this:** the `Authorization: Bearer <token>` header
> is attached to every request, but almost nothing on the backend actually checks it.
> `get_current_user` (in `app/core/security.py`) exists and validates a JWT, but no router in the
> project uses it as a dependency — except `POST /auth/logout`, which reads the token only to
> find which session row to revoke. Every other endpoint, including every money-moving one,
> currently accepts requests with **no `Authorization` header at all**. The frontend's role-based
> nav/routing (§2) is a UI convenience, not a security boundary — the same caveat the
> [`README.md`](README.md) role-access section already states. Also: the JWT itself has **no
> expiry claim** — `create_token()` never sets `exp` — so don't build silent-token-refresh logic
> expecting the JWT to expire on its own.

**HTTP status codes used consistently across every router:**

| Status | Meaning here |
|---|---|
| `200` | GET succeeded |
| `201` | POST created a row (`response_model` returns the new object) |
| `204` | DELETE succeeded (no response body) |
| `400` | Business-rule failure — bad foreign key in the body, duplicate unique field, insufficient balance, etc. |
| `404` | The path's `{id}` doesn't exist |
| `409` | DELETE blocked because another table still has a foreign key pointing at this row (`commit_or_409`, `app/core/db_utils.py`) |
| `422` | Pydantic rejected the request body's shape before your route function ever ran |

Every page's `save()`/`removeRow()` reads `err.response?.data?.detail` to show the backend's
error message in a `$q.notify` — that `detail` string is exactly the `HTTPException(detail=...)`
text from the matching backend route.

---

## 1. Authentication — Login, Session, Logout

Login is the one endpoint that isn't JSON. Full sequence, `LoginPage.vue` submit → dashboard:

**1. `LoginPage.vue`'s form submit** calls `auth.login(username, password)` (the Pinia action
below), inside a try/catch that branches on `err.response` (backend rejected) vs `err.request`
(no response — backend down/CORS) vs a plain `err.message` (client-side logic error, e.g. #3
below).

**2. `useAuthStore().login()`** — **[`src/stores/auth-store.js`](src/stores/auth-store.js)**:
```js
async login (username, password) {
  const form = new URLSearchParams()
  form.append('username', username)
  form.append('password', password)

  const { data } = await api.post('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  this.token = data.access_token

  // No /auth/me endpoint exists on the backend, so the logged-in user's
  // own record (and therefore their role) is resolved client-side by
  // matching the username against the full user list.
  const { data: users } = await api.get('/users/')
  const me = users.find((u) => u.username === username)
  if (!me) {
    throw new Error('Logged in, but could not find a matching user record')
  }

  this.userId = me.id
  this.roleId = me.role_id
  // ...firstName/lastName/username assigned here too

  const { data: role } = await api.get(`/roles/${me.role_id}`)
  this.roleCode = role.role_code
  this.roleName = role.role_name

  this.persist()   // writes everything to localStorage under 'bank_auth'
}
```
Note the request body is a `URLSearchParams` with an explicit
`application/x-www-form-urlencoded` header — **not** `api.post('/auth/login', { username,
password })`. That's not a style choice; the backend requires it (step 3).

**3. Backend `POST /auth/login`** — **`app/routers/auth.py`**:
```python
@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not check_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password",
                             headers={"WWW-Authenticate": "Bearer"})
    if user.account_status != "ACTIVE":
        raise HTTPException(status_code=403, detail="Account is not active")

    token = create_token(user.username)
    new_session = UserSession(user_id=user.id, jwt_token=token, ...)
    db.add(new_session)
    user.last_login_at = datetime.utcnow()
    db.commit()
    return Token(access_token=token)
```
`OAuth2PasswordRequestForm` is what *forces* the form-urlencoded body — it's FastAPI's standard
OAuth2 password-flow dependency, and it only parses `application/x-www-form-urlencoded`, not
JSON. This is also why a bad login is `401` and a locked/disabled account is `403` — two
different failure modes the frontend's catch block can, in principle, distinguish by status code
(it currently just shows `err.response.data.detail` either way).

**4. Response** — `Token` schema (`app/schemas/auth.py`): `{"access_token": "<jwt>", "token_type":
"bearer"}`. Note the field is `access_token`, matching `data.access_token` in step 2 exactly.

**5–6. `GET /users/` then `GET /roles/{role_id}`** — two more round trips, purely to work around
the missing `/auth/me` endpoint. This means every login costs 3 HTTP requests, not 1.

**7. `this.persist()`** writes the whole auth state to `localStorage['bank_auth']`, so a page
refresh doesn't log the user out — `auth-store.js` rehydrates from this key at module load
(`loadPersisted()`), before Pinia even initializes state.

**8. Router redirect** — the `login()` call resolves, `LoginPage.vue` does `router.push('/')`,
and the navigation guard (§2) takes over from there based on the now-populated `auth.roleCode`.

### Logout

**[`src/layouts/MainLayout.vue`](src/layouts/MainLayout.vue)**'s `onLogout()` calls
`auth.logout()` then `router.push('/login')`. Look at what `logout()` actually does:
```js
logout () {
  this.token = null
  // ...clears every other field...
  localStorage.removeItem(STORAGE_KEY)
}
```
**It never calls the backend.** `POST /auth/logout` exists (`app/routers/auth.py`) and properly
revokes the session row server-side, but nothing in the frontend ever calls it — logout here is
purely local `localStorage` clearing. The JWT itself stays valid (it never expires, per §0) even
after the user "logs out" in the UI; it's just no longer stored anywhere client-side to send. If
you extend this project, wiring `MainLayout.vue`'s `onLogout()` to also `POST /auth/logout` before
clearing local state is the correct fix.

The **other** logout trigger is automatic: the response interceptor in §0 calls `auth.logout()`
on any `401`, from any page, at any time — not just from a dedicated logout button.

---

## 2. Routing & Role-Based UI

This layer has no backend counterpart — it's pure frontend architecture, but it's what decides
*which* backend endpoints a given logged-in user's UI ever calls.

**[`src/router/routes.js`](src/router/routes.js)** (trimmed):
```js
const routes = [
  { path: '/login', component: () => import('@/pages/LoginPage.vue') },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'dashboard', component: () => import('@/pages/DashboardPage.vue') },

      // ADMIN only
      { path: 'admin/roles', component: () => import('@/pages/admin/RolesPage.vue'), meta: { roles: ['ADMIN'] } },
      // ...5 more admin/* routes, same shape...

      // ADMIN + STAFF
      { path: 'accounts', component: () => import('@/pages/staff/AccountsPage.vue'), meta: { roles: ['ADMIN', 'STAFF'] } },
      // ...9 more staff-facing routes, same shape...

      // CUSTOMER only
      { path: 'my-account', component: () => import('@/pages/customer/MyAccountPage.vue'), meta: { roles: ['CUSTOMER'] } },
      { path: 'my-transactions', component: () => import('@/pages/customer/MyTransactionsPage.vue'), meta: { roles: ['CUSTOMER'] } },
    ],
  },
  { path: '/:catchAll(.*)*', component: () => import('@/pages/ErrorNotFound.vue') },
]
```

**[`src/router/index.js`](src/router/index.js)**'s guard runs before every navigation:
```js
Router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.path === '/login') {
    return auth.isAuthenticated ? '/' : true          // already logged in? skip login page
  }
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return '/login'                                     // not logged in? bounce to login
  }
  const allowedRoles = to.meta.roles
  if (allowedRoles && !allowedRoles.includes(auth.roleCode)) {
    return '/'                                          // wrong role? bounce to dashboard
  }
  return true
})
```
Three checks, in order: (1) don't show `/login` to someone already logged in, (2) require
`auth.isAuthenticated` (`!!token`) for anything under `meta.requiresAuth`, (3) require
`auth.roleCode` to be in `to.meta.roles` if that route restricts by role. A `STAFF` user hitting
`/admin/roles` directly (typed URL, bookmark, etc.) gets silently redirected to `/`, not a 403
page — there's no "access denied" screen anywhere in this app.

**`MainLayout.vue`** builds the drawer nav from the same store getters, so the visible links and
the enforced routes never drift apart — they both read `auth.isAdmin`/`isStaff`/`isCustomer`:

| Role | Sees in nav | Can navigate to |
|---|---|---|
| ADMIN | Everything | All routes |
| STAFF | Banking Operations only | `accounts`, `withdrawal-limits`, `interest-policies`, `deposits`, `withdrawals`, `transfers`, `interbank-transfers`, `fee-records`, `interest-records`, `ledger-entries` |
| CUSTOMER | My Banking only | `my-account`, `my-transactions` |

---

## 3. Layer 1 — Foundation & Reference Data

**Resources:** `roles`, `account_types`, `banks`, `fee_types` — no foreign keys, pure lookup
tables. Registered in `app/main.py` with no shared prefix; each router sets its own via
`APIRouter(prefix=...)`.

### Backend — `app/routers/roles.py` (canonical example; the other 3 are identical in shape)

```python
router = APIRouter(prefix="/roles", tags=["Layer 1 - Roles"])

@router.post("/", response_model=RoleOut, status_code=201)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    if db.query(Role).filter(Role.role_code == role.role_code).first():
        raise HTTPException(status_code=400, detail="role_code already exists")
    new_role = Role(**role.model_dump())
    db.add(new_role); db.commit(); db.refresh(new_role)
    return new_role

@router.get("/", response_model=list[RoleOut])
def list_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()

@router.get("/{role_id}", response_model=RoleOut)   # 404 if missing
@router.put("/{role_id}", response_model=RoleOut)    # full replace, 404 if missing
@router.delete("/{role_id}", status_code=204)         # commit_or_409 — 409 if a user references it
```

Schema (`app/schemas/role.py`):
```python
class RoleCreate(BaseModel):
    role_code: str
    role_name: str
    description: Optional[str] = None

class RoleOut(BaseModel):
    id: int
    role_code: str
    role_name: str
    description: Optional[str] = None
    created_at: datetime
```

### Frontend — `src/pages/admin/RolesPage.vue` (full logic)

```js
const rows = ref([])
const form = ref({ role_code: '', role_name: '', description: '' })

async function loadRows () {
  const { data } = await api.get('/roles/')
  rows.value = data
}

async function save () {
  if (editingId.value) {
    await api.put(`/roles/${editingId.value}`, form.value)
  } else {
    await api.post('/roles/', form.value)
  }
  loadRows()   // no optimistic update — always re-fetches the full list after a write
}

function removeRow (row) {
  $q.dialog({ title: 'Confirm Delete', message: `Delete role "${row.role_name}"?`, cancel: true })
    .onOk(async () => { await api.delete(`/roles/${row.id}`); loadRows() })
}

onMounted(loadRows)
```

### Trace: clicking "Save" on a new role

1. User fills the `q-dialog` form (`role_code`, `role_name`, `description`) and clicks **Save**.
2. `editingId.value` is `null` (this is a create) → `api.post('/roles/', form.value)`.
3. Axios sends `POST /roles/` with JSON body `{"role_code": "...", "role_name": "...",
   "description": "..."}` and header `Authorization: Bearer <token>` (attached by the interceptor,
   though `roles.py` never checks it).
4. FastAPI validates the body against `RoleCreate` — a missing `role_code` would `422` here
   before `create_role()` even runs.
5. `create_role()` checks for a duplicate `role_code` (`400` if found), inserts the row, commits,
   and returns the new row shaped as `RoleOut` — now including the DB-assigned `id` and
   `created_at` the client never sent.
6. Axios resolves; `showDialog.value = false`, a positive `$q.notify`, then `loadRows()` re-fetches
   `GET /roles/` from scratch and replaces `rows.value` — the `q-table` re-renders with the new row.
7. If step 5 instead raised `400`, the catch block reads `err.response.data.detail` (e.g.
   `"role_code already exists"`) into a negative `$q.notify`, and the dialog stays open.

### The other three Layer 1 pages

| Page | Endpoints | Notably different from Roles |
|---|---|---|
| `admin/AccountTypesPage.vue` | `/account-types/` (GET/POST/PUT/DELETE) | Numeric fields (`minimum_balance`, `opening_deposit`, `annual_interest_rate`, `daily_withdrawal_limit`) coerced via `Number()` in `openEdit` |
| `admin/BanksPage.vue` | `/banks/` | `status` is a `q-select` with static options `['ACTIVE','INACTIVE']` (matches the backend `Bank.status` ENUM) |
| `admin/FeeTypesPage.vue` | `/fee-types/` | Adds `fee_description` as a textarea; otherwise identical shape |

All three follow the exact `loadRows`/`save`/`removeRow` pattern above — only field names and the
endpoint prefix differ.

---

## 4. Layer 2 — Identity & Access

**Resources:** `users` (FK → `roles`), `sessions`, `audit_logs`. Auth itself (`POST
/auth/login`/`logout`) is covered in §1 since it's used from `LoginPage.vue`/`MainLayout.vue`
specifically, not a CRUD page.

### Backend

**`app/routers/users.py`** (`prefix="/users"`) — same 5-endpoint CRUD shape as Layer 1, plus:
`create_user`/`update_user` validate `role_id` is a real row (`400` if not), hash the incoming
plaintext `password` before storing, and `UserOut` **never includes the password in any form** —
not even hashed.

**`app/routers/sessions.py`** (`prefix="/sessions"`) — full CRUD plus one action endpoint, `PUT
/sessions/{id}/revoke` (sets `revoked_at`). **No frontend page calls any `/sessions/*` endpoint
at all** — this resource is written to only as a side effect of `POST /auth/login` (§1) and never
read back through the UI.

**`app/routers/audit_logs.py`** (`prefix="/audit-logs"`) — **no `PUT`**, deliberately:
```python
@router.post("/", response_model=AuditLogOut, status_code=201)
@router.get("/", response_model=list[AuditLogOut])
@router.get("/{log_id}", response_model=AuditLogOut)
@router.delete("/{log_id}", status_code=204)
# no update_audit_log — an audit trail that could be edited after the fact isn't a trail
```

### Frontend

`admin/UsersPage.vue` follows the Roles CRUD pattern exactly, plus a second `GET /roles/` call in
`onMounted` to populate the role `q-select` (`emit-value`/`map-options`), and blanks the
`password` field in `openEdit` (never pre-fills it from the row, since the backend never sends it
back either).

`admin/AuditLogsPage.vue` mirrors the missing backend `PUT` — its table's action column has only
a delete icon, no edit icon, and `save()` only ever does `POST /audit-logs/`, never `PUT`. The
form also deliberately omits `old_value`/`new_value` (JSON columns meant to be filled by
application code automatically, not typed by a human in a dialog).

---

## 5. Layer 3 — Account Configuration

**Resources:** `accounts` (FK → `users`, `account_types`), `withdrawal_limits` (1:1 with
`accounts`), `interest_policies` (FK → `account_types`).

### Backend — `app/routers/accounts.py` (`prefix="/accounts"`)

| Method | Path | Notes |
|---|---|---|
| POST | `/accounts/` | Validates `customer_id`/`account_type_id` FKs, unique `account_number`. **`available_balance`/`ledger_balance` are server-computed** from `account_type.opening_deposit` — the client never sends a starting balance (`AccountCreate` has no balance fields at all). |
| GET | `/accounts/`, `/accounts/{id}` | — |
| PUT | `/accounts/{id}` | Uses a *different* schema, `AccountUpdate` (adds `status`), so status changes go through the same endpoint as everything else; auto-sets `closed_at` when status transitions to `CLOSED`. |
| DELETE | `/accounts/{id}` | `commit_or_409` |

`withdrawal_limits.py` (`prefix="/withdrawal-limits"`) enforces the 1:1 relationship in code
(`400` if the account already has a limit row on create) and its `PUT` uses `WithdrawalLimitUpdate`
— only `daily_limit_amount`/`last_reset_date`, no `account_id` (an existing limit can't be
reassigned to a different account through this endpoint).

`interest_policies.py` (`prefix="/interest-policies"`) is a plain 5-endpoint CRUD, validating
`account_type_id` on write.

### Frontend — `staff/AccountsPage.vue`: the grouped-table pattern

This page's `q-table` doesn't render `rows` directly — the backend has no "group by customer"
query, so the frontend builds one client-side with a `computed`:

```js
const groupedRows = computed(() => {
  const sorted = [...rows.value].sort((a, b) => {
    const nameA = customerNameById.value[a.customer_id] || ''
    const nameB = customerNameById.value[b.customer_id] || ''
    return nameA.localeCompare(nameB) || a.account_number.localeCompare(b.account_number)
  })
  const result = []
  let lastCustomerId = null
  for (const row of sorted) {
    if (row.customer_id !== lastCustomerId) {
      result.push({ isGroupHeader: true, key: `group-${row.customer_id}`,
                    groupLabel: customerNameById.value[row.customer_id] || `Customer #${row.customer_id}` })
      lastCustomerId = row.customer_id
    }
    result.push(row)
  }
  return result
})
```
`customerNameById` is built once in `loadOptions()` from the full `GET /users/` response (the
`accounts` endpoint itself only returns `customer_id`, an integer — the frontend has to fetch
`/users/` separately and join client-side to show a name). The template then uses a manual
`v-slot:body` instead of the default row renderer, checking `props.row.isGroupHeader` to decide
whether to render a `colspan="100%"` header row or a normal data row. `save()`/`removeRow()`
otherwise follow the exact same `POST`/`PUT`/`DELETE /accounts/{id}` pattern as every other CRUD
page.

`staff/WithdrawalLimitsPage.vue` mirrors its backend's split schema: on edit, `save()` sends only
`{ daily_limit_amount, last_reset_date }` (not the full form) — a direct reflection of
`WithdrawalLimitUpdate` not accepting `account_id`.

`staff/InterestPoliciesPage.vue` is a plain CRUD page against `/interest-policies/`, with an
`account_type_id` `q-select` sourced from `GET /account-types/`.

---

## 6. Layer 4 — Transactions

This is where endpoints stop being simple CRUD — every write here also mutates an `accounts` row
**in the same request/commit**, using `.with_for_update()` to lock the row against concurrent
writes.

### Backend — `app/routers/deposits.py` (canonical "money movement" endpoint)

```python
@router.post("/", response_model=DepositOut, status_code=201)
def create_deposit(deposit: DepositCreate, db: Session = Depends(get_db)):
    # Locks this account row until commit — a second request touching the
    # same account has to wait instead of reading a stale balance.
    account = db.query(Account).filter(Account.id == deposit.account_id).with_for_update().first()
    if not account:
        raise HTTPException(status_code=400, detail="account_id does not exist")
    if db.query(Deposit).filter(Deposit.reference_number == deposit.reference_number).first():
        raise HTTPException(status_code=400, detail="reference_number already exists")

    new_deposit = Deposit(**deposit.model_dump())
    db.add(new_deposit)

    account.available_balance += deposit.amount     # the actual point of a deposit
    account.ledger_balance += deposit.amount

    db.commit(); db.refresh(new_deposit)
    return new_deposit
```
`update_deposit` (`PUT`) and `delete_deposit` both carry explicit docstring warnings: they edit or
remove the *record* only and **never touch the account balance** — editing a posted transaction
doesn't reverse the money movement it caused. `withdrawals.py` mirrors this exactly but subtracts,
and additionally checks the linked `withdrawal_limits` row (sufficient balance **and** the daily
limit not yet used up) before allowing the withdrawal.

`transfers.py` moves money between two of *your own* accounts in one commit — and has to lock
**both** rows:
```python
# Locking order matters: always lock the lower id first, or two transfers
# running in opposite directions at the same time (A->B and B->A) could
# each be waiting on the row the other one is holding — a deadlock.
first_id, second_id = sorted([transfer.source_account_id, transfer.destination_account_id])
accounts_by_id = {a.id: a for a in db.query(Account)
                  .filter(Account.id.in_([first_id, second_id])).with_for_update().all()}
...
source.available_balance -= transfer.amount;  destination.available_balance += transfer.amount
```
Status is set to `"SUCCESS"` immediately — an internal transfer settles instantly, no async step.

`interbank_transfers.py` is different again: the destination is a different bank, so the backend
can only debit its own side —
```python
total_debit = transfer.amount + transfer.transfer_fee
if source.available_balance < total_debit:
    raise HTTPException(status_code=400, detail="Insufficient balance to cover amount + transfer fee")

new_transfer = InterbankTransfer(**transfer.model_dump(), status="PROCESSING")
source.available_balance -= total_debit
```
— and starts at `status="PROCESSING"`, not `"SUCCESS"`, because settling with another bank isn't
instant. A separate endpoint moves it forward:
```python
@router.put("/{transfer_id}/status", response_model=InterbankTransferOut)
def update_interbank_transfer_status(transfer_id: int, data: InterbankTransferStatusUpdate, ...):
    transfer.status = data.status                                    # SUCCESS / FAILED / REVERSED
    if data.status in ("SUCCESS", "FAILED", "REVERSED"):
        transfer.completed_at = datetime.utcnow()
```

### Frontend

`staff/DepositsPage.vue`/`WithdrawalsPage.vue` (near-identical) both: fetch `/accounts/` +
`/users/` in `loadOptions()` to build an "Account Holder" name lookup (backend `deposits`/
`withdrawals` rows only carry `account_id`, an integer); their `channel` `q-select` uses
`use-input`/`new-value-mode="add-unique"` against a static `['ONLINE','ATM','TELLER']` list with
client-side substring filtering, but still allows free-text entry — the backend's ENUM validation
is the real gate, not the dropdown.

`staff/TransfersPage.vue` presents both `source_account_id` and `destination_account_id` as
`q-select`s built from the same `accountOptions` list — nothing in the UI stops picking the same
account for both (the backend's `400` on equal IDs, seen above, is the only thing that catches it).

`staff/InterbankTransfersPage.vue` is the one page with a genuinely different action, not just
CRUD:
```js
async function markStatus (row, status) {
  await api.put(`/interbank-transfers/${row.id}/status`, { status })
  loadRows()
}
```
wired to two icon buttons in the table's actions column, both `v-if="props.row.status ===
'PROCESSING'"` — they simply don't render once a transfer is already settled:
```html
<q-btn v-if="props.row.status === 'PROCESSING'" icon="check_circle" @click="markStatus(props.row, 'SUCCESS')" />
<q-btn v-if="props.row.status === 'PROCESSING'" icon="cancel" @click="markStatus(props.row, 'FAILED')" />
```

### Trace: posting a deposit end to end

1. Staff user opens Deposits, picks an account (`q-select`, shows holder name via the client-side
   lookup), enters `reference_number`, `amount`, `deposit_channel`, clicks **Save**.
2. `POST /deposits/` fires with the form as JSON body.
3. Backend locks the account row, validates the FK and the unique reference, inserts the
   `deposits` row, **and in the same transaction** increments `available_balance`/
   `ledger_balance` on the locked account row, then commits — both writes land together or not
   at all.
4. Response is `DepositOut` (the new deposit row, including server-assigned `id`/`created_at`) —
   note this response does **not** include the account's new balance; the frontend would need a
   separate `GET /accounts/{id}` to see it reflected.
5. `loadRows()` re-fetches `/deposits/` — the table shows the new row. If the same page (or
   `DashboardPage.vue`, or `MyAccountPage.vue`) is also showing the account's balance, it won't
   update until *that* component's own `loadRows()`/`onMounted` fires again — there's no shared
   reactive account-balance state anywhere in the app.

---

## 7. Layer 5 — Financial Records & Ledger

**Resources:** `fee_records` (mutates balance), `interest_records` (mutates balance + snapshot),
`ledger_entries` (snapshot only, no mutation).

### Backend

`fee_records.py` (`prefix="/fee-records"`) locks the account and applies the fee — **with no
balance check**, unlike withdrawals: a fee can legitimately push `available_balance` negative.

`interest_records.py` (`prefix="/interest-records"`) — **no `PUT`** — increases the balance and
records both `balance_before` and `balance_after` as part of the same insert, computed
server-side; the create schema (`InterestRecordCreate`) has no balance fields at all.

`ledger_entries.py` (`prefix="/ledger-entries"`) — **no `PUT`** — is architecturally the odd one
out, and the code says so directly:
```python
# In a fully wired system, every deposit/withdrawal/transfer/fee/interest
# endpoint in Layers 4-5 would call a shared helper to insert its own
# ledger_entries row automatically, at the exact moment it changes the
# balance — that's what makes a ledger authoritative. Wiring that up
# everywhere is a bigger refactor than this project takes on, so here
# `ledger_entries` is its own simple CRUD table instead: it does NOT
# apply debit_amount/credit_amount to the account (that already
# happened via the real transaction endpoint). `balance_after` is a
# read-only snapshot of the account's current balance at insert time,
# not something the client can set.
new_entry = LedgerEntry(**entry.model_dump(), balance_after=account.available_balance)
```
In other words: posting a deposit does **not** automatically create a matching `ledger_entries`
row. They're two independent tables a staff user would have to populate separately today.

### Frontend

`staff/FeeRecordsPage.vue` is a plain CRUD page (`account_id` + `fee_type_id` selects).
`staff/InterestRecordsPage.vue` and `staff/LedgerEntriesPage.vue` both omit their edit button
entirely and only ever call `POST`/`DELETE` — a direct mirror of the missing backend `PUT` — and
both forms exclude the backend-computed fields (`balance_before`/`balance_after`), with an inline
comment in the `.vue` file explaining why, matching the backend's own comment above.

---

## 8. Customer Self-Service Pages

These don't correspond to a *new* backend resource — they're read-only views over Layer 3/4 data,
filtered to the logged-in customer entirely client-side (there's no `?customer_id=` query param
or `/my/*` endpoint on the backend; every filter happens in the browser after fetching everything).

`customer/MyAccountPage.vue`: `GET /accounts/`, then `data.filter(a => a.customer_id ===
auth.userId)` — nothing else.

`customer/MyTransactionsPage.vue` is the most elaborate page in the app — it reconstructs a unified
transaction history from **four separate endpoints**, because the backend has no single
"transactions" resource:
```js
const { data: allAccounts } = await api.get('/accounts/')
const myAccountIds = allAccounts.filter((a) => a.customer_id === auth.userId).map((a) => a.id)

const [deposits, withdrawals, transfers, interbank] = await Promise.all([
  api.get('/deposits/'), api.get('/withdrawals/'),
  api.get('/transfers/'), api.get('/interbank-transfers/'),
])

// each of the 4 responses is filtered against myAccountIds and mapped into
// a common { key, date, type, account_number, reference, amount, direction } shape,
// then combined and sorted by date descending
```
A `transfers` row can produce **two** entries for this customer (`TRANSFER OUT` if they're the
source, `TRANSFER IN` if they're the destination — both checked independently, since a customer
could theoretically own both accounts in a transfer). An `interbank-transfers` row's displayed
amount is `Number(amount) + Number(transfer_fee)` — the actual total debited from the account,
which the raw `amount` field alone doesn't represent.

---

## 9. Full Endpoint ↔ Page Reference Table

| Layer | Resource | Backend prefix | Frontend page(s) | Roles |
|---|---|---|---|---|
| 1 | Roles | `/roles/` | `admin/RolesPage.vue` | ADMIN |
| 1 | Account Types | `/account-types/` | `admin/AccountTypesPage.vue` | ADMIN |
| 1 | Banks | `/banks/` | `admin/BanksPage.vue` | ADMIN |
| 1 | Fee Types | `/fee-types/` | `admin/FeeTypesPage.vue` | ADMIN |
| 2 | Users | `/users/` | `admin/UsersPage.vue` | ADMIN |
| 2 | Auth | `/auth/login`, `/auth/logout` | `LoginPage.vue`, `stores/auth-store.js` | (public) |
| 2 | Sessions | `/sessions/` | *none* — write-only side effect of login | — |
| 2 | Audit Logs | `/audit-logs/` | `admin/AuditLogsPage.vue` | ADMIN |
| 3 | Accounts | `/accounts/` | `staff/AccountsPage.vue` + read-only in `customer/MyAccountPage.vue` | ADMIN, STAFF (+ CUSTOMER read) |
| 3 | Withdrawal Limits | `/withdrawal-limits/` | `staff/WithdrawalLimitsPage.vue` | ADMIN, STAFF |
| 3 | Interest Policies | `/interest-policies/` | `staff/InterestPoliciesPage.vue` | ADMIN, STAFF |
| 4 | Deposits | `/deposits/` | `staff/DepositsPage.vue` + read-only in `customer/MyTransactionsPage.vue` | ADMIN, STAFF (+ CUSTOMER read) |
| 4 | Withdrawals | `/withdrawals/` | `staff/WithdrawalsPage.vue` + read-only in `customer/MyTransactionsPage.vue` | ADMIN, STAFF (+ CUSTOMER read) |
| 4 | Transfers | `/transfers/` | `staff/TransfersPage.vue` + read-only in `customer/MyTransactionsPage.vue` | ADMIN, STAFF (+ CUSTOMER read) |
| 4 | Interbank Transfers | `/interbank-transfers/`, `/interbank-transfers/{id}/status` | `staff/InterbankTransfersPage.vue` + read-only in `customer/MyTransactionsPage.vue` | ADMIN, STAFF (+ CUSTOMER read) |
| 5 | Fee Records | `/fee-records/` | `staff/FeeRecordsPage.vue` | ADMIN, STAFF |
| 5 | Interest Records | `/interest-records/` | `staff/InterestRecordsPage.vue` | ADMIN, STAFF |
| 5 | Ledger Entries | `/ledger-entries/` | `staff/LedgerEntriesPage.vue` | ADMIN, STAFF |

`DashboardPage.vue` doesn't belong to any single layer — it role-branches in `onMounted` and pulls
a small slice from whichever layers are relevant to the logged-in role (e.g. Admin dashboard hits
`/roles/`, `/users/`, `/accounts/`, `/banks/` in one `Promise.all`).

---

## 10. Known Gaps & Things to Watch

Worth knowing before you extend either side — these are current, real characteristics of the code,
not bugs to silently work around:

- **Auth is attached but not enforced.** The frontend sends `Authorization: Bearer <token>` on
  every request; almost no backend endpoint checks it (§0). Don't assume role restrictions in the
  UI reflect real backend access control.
- **JWTs never expire.** No `exp` claim is ever set (§0).
- **Frontend logout never calls the backend.** `POST /auth/logout` exists and works, but
  `MainLayout.vue`'s `onLogout()` doesn't call it (§1) — sessions in the `sessions` table are
  never marked `revoked_at` from the UI.
- **No pagination or server-side search anywhere.** Every list page fetches the *entire*
  collection on every load, including ones used only to populate a dropdown (e.g. Deposits
  fetches all of `/accounts/` and all of `/users/` just to show account-holder names).
- **PUT/DELETE on money-moving records never reverse the balance change.** Editing or deleting a
  posted deposit/withdrawal/transfer/fee/interest record changes or removes that record only —
  the account balance it already affected stays changed. This is explicit in code comments on
  every Layer 4/5 router (§6, §7).
- **`ledger_entries` isn't populated automatically.** Posting a deposit does not create a matching
  ledger entry — they're independent tables today (§7).
- **No shared reactive state for account balances.** Two pages showing the same account's balance
  (e.g. a Dashboard tile and `MyAccountPage.vue`) can disagree until each independently re-fetches
  — there's no global store for account data, only for auth (§6 trace, step 5).
