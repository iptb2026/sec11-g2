# Mini Banking System — Frontend (Quasar + Vite + Axios)

Role-based web UI for the FastAPI Mini Banking System (`../app`). Nav and pages differ by role:
**ADMIN**, **STAFF**, **CUSTOMER**.

Sections 0–5: everything needed for coursework. Section 6: optional, only if you need the app
reachable from outside the container.

## Contents

0. [Get the Code](#0-get-the-code)
1. [Local Setup](#1-local-setup)
2. [Demo Login](#2-demo-login)
3. [How Role-Based Access Works](#3-how-role-based-access-works)
4. [Project Structure](#4-project-structure)
5. [Build for Production](#5-build-for-production)
6. [Exposing the App via Nginx (optional)](#6-exposing-the-app-via-nginx-optional)
7. [Troubleshooting](#7-troubleshooting)

---

## 0. Get the Code

1. Download/clone the repo: [github.com/iptb2026/mytemplate](https://github.com/iptb2026/mytemplate)
2. You only need the `frontend` folder: [labdemo2/frontend](https://github.com/iptb2026/mytemplate/tree/main/labdemo2/frontend)
3. In VS Code, drag that `frontend` folder from `labdemo2/` into your root project folder.

**Folder organization** — your root project folder (`appserver/`) holds both apps as siblings:
```
appserver/            # parent/root — this is what you open in VS Code
├── app/               # FastAPI backend
└── frontend/           # Quasar frontend (this project)
```
Everything from here on assumes you're inside `appserver/frontend/`.

---

## 1. Local Setup

### 1.1 Check Node.js & npm

```bash
node --version
npm --version
```

Need `>= 22.12` (also `^24` or `>= 26`).

### 1.2 Install dependencies

```bash
cd appserver/frontend
npm install
```

### 1.3 Point the frontend at your backend

Set in [`.env`](.env):

```env
QCLI_API_BASE_URL=http://<your-server>:<your-port>/<your-username>/
```

Example: `QCLI_API_BASE_URL=http://192.168.118.150:3101/guiritan/` → login requests go to
`http://192.168.118.150:3101/guiritan/auth/login`. Match this to the endpoint your instructor
gave you.

> **Tip — which host to use:**
> - **On the school lab:** use `172.17.100.14:<your assigned port>` — not `localhost`, since the
>   backend runs in a different container/machine on the lab network.
> - **Home lab:** use `localhost` or `127.0.0.1` (equivalent), or whatever hostname/IP your
>   Docker container gives you (e.g. `192.168.1.10`, `192.168.118.150`) — `172.17.100.14` is
>   specific to the school lab network and won't resolve elsewhere.

### 1.4 Run it

```bash
npm run dev
```

Opens `http://localhost:9000` — you should land on the login page.

> **University lab:** `localhost:9000` only works from inside the container itself (e.g. a
> browser running on the same machine). To reach it from your own PC over the lab network, you
> need the IP + port mapping + Nginx reverse proxy in front of it — see §6 (Exposing the App via
> Nginx), specifically the `location` block in 6.3.

> **Sharing a container with classmates?** Port `9000` can only be held by one dev server at a
> time. If `npm run dev` fails to start (address already in use), someone else's frontend is
> already on that port — pick your own via §6.4 instead of guessing.

---

## 2. Demo Login

| Username    | Password | Role     | Sees                                   |
|-------------|----------|----------|------------------------------------------|
| `admin`     | `1234`   | ADMIN    | Full nav: system config + all banking operations |
| `mgarcia`   | `1234`   | STAFF    | Banking operations only, no system config |
| `jdelacruz` | `1234`   | CUSTOMER | My Account + My Transactions only |

Seed users through the backend first (see `../demomanual/layer_1.md`–`layer_2.md`).

## 3. How Role-Based Access Works

- After login, the app calls `GET /users/` to find your `role_id`, then `GET /roles/{role_id}`
  for the role code. There's no `/auth/me` endpoint, so this is resolved client-side.
- The router guard (`src/router/index.js`) and drawer nav (`src/layouts/MainLayout.vue`) both
  read each route's `meta.roles`.
- **Client-side only** — the backend enforces no authorization itself. Don't treat this UI as a
  real security boundary.

## 4. Project Structure

```
src/
├── boot/axios.js              # shared axios instance + JWT header interceptor
├── services/api.js            # axios instance (baseURL from .env)
├── stores/auth-store.js       # Pinia store: login/logout, token, resolved role
├── router/
│   ├── routes.js              # route tree with meta.requiresAuth / meta.roles
│   └── index.js               # navigation guard
├── layouts/MainLayout.vue     # toolbar + role-based drawer nav
└── pages/
    ├── LoginPage.vue
    ├── DashboardPage.vue
    ├── admin/                 # roles, account-types, banks, fee-types, users, audit-logs
    ├── staff/                 # accounts, deposits, withdrawals, transfers, interbank,
    │                          #   withdrawal-limits, interest-policies, fee/interest/ledger records
    └── customer/               # my-account, my-transactions
```

Every page under `admin/`/`staff/` has the same shape: `q-table` list, `q-dialog` + `q-form` for
create/edit, plain `api.get/post/put/delete` calls. Once you understand one (e.g.
`admin/RolesPage.vue`), you understand all 16.

## 5. Build for Production

```bash
npm run build
```

Outputs to `dist/spa/` (`quasar serve dist/spa` to check locally).

---

## 6. Exposing the App via Nginx (optional)

Only needed if the app must be reachable outside the container — e.g. so classmates/instructors
can reach it at your lab server's address, like your FastAPI backend already is.

### Placeholders

| Placeholder | Example |
|---|---|
| `<YOUR_USERNAME>` | `guiritan` |
| `<YOUR_LAB_SERVER_IP>` | `172.17.100.14` (university lab) / `192.168.118.150`, `127.0.0.1` (home lab, samples) |
| `<YOUR_HOST_PORT>` | `3101` |
| `<YOUR_NGINX_PORT>` | `8001` |
| `<YOUR_BACKEND_PORT>` | `5000` |
| `<YOUR_FRONTEND_DEV_PORT>` | `9000` |

Frontend path convention: `/<YOUR_USERNAME>-wui/` (backend keeps `/<YOUR_USERNAME>/`).

> `<YOUR_LAB_SERVER_IP>` follows the same rule as the §1.3 tip: `172.17.100.14` on the
> university lab, or `localhost`/`127.0.0.1`/your container's hostname or IP (e.g.
> `192.168.1.10`) in a home lab. This applies everywhere below — the config in 6.3, and the
> `curl` checks in 6.5.

### 6.1 Set the base path (`quasar.config.js`)

```js
build: {
  vueRouterMode: 'hash',
  vueRouterBase: '/<YOUR_USERNAME>-wui/',
  publicPath: '/<YOUR_USERNAME>-wui/',
  ...
}
```

Trailing slash required — `/guiritan-wui/`, not `/guiritan-wui`.

### 6.2 Trailing-slash rule for `proxy_pass`

| App | `proxy_pass` | Trailing slash |
|---|---|---|
| FastAPI (`--root-path` strips prefix) | `http://127.0.0.1:<PORT>/;` | Yes |
| Vite dev server (no such option) | `http://127.0.0.1:<PORT>;` | No |

Getting this backwards on the frontend causes an infinite redirect loop (Vite doesn't recognize
the stripped path and keeps redirecting back to it).

### 6.3 Nginx `location` block

Edit `/etc/nginx/sites-available/ipt2`:

```nginx
server {
    listen <YOUR_NGINX_PORT>;
    server_name _;

    location /<YOUR_USERNAME>/ {
        proxy_pass http://127.0.0.1:<YOUR_BACKEND_PORT>/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Prefix /<YOUR_USERNAME>;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /<YOUR_USERNAME>-wui/ {
        proxy_pass http://127.0.0.1:<YOUR_FRONTEND_DEV_PORT>;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Prefix /<YOUR_USERNAME>-wui;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Upgrade $http_upgrade;      # Vite HMR websocket
        proxy_set_header Connection "upgrade";
    }

    # other existing location blocks stay as-is
}
```

Each student on a shared container gets their own pair of blocks, same shape, different
username and frontend port. Worked example — `username1` (port `9000`, the default) alongside a
second student `username2` on port `9100`:

```nginx
    location /username1/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Prefix /username1;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /username1-wui/ {
        proxy_pass http://127.0.0.1:9000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Prefix /username1-wui;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /username2/ {
        proxy_pass http://127.0.0.1:5001/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Prefix /username2;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /username2-wui/ {
        proxy_pass http://127.0.0.1:9100;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Prefix /username2-wui;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
```

Note `username2-wui` proxies to `9100`, not `9000` — see §6.4 for setting a custom dev server
port so two students' frontends don't collide.

Use `127.0.0.1`, not the container's own IP (`172.21.0.2`-style) — that can change on restart.

### 6.4 Custom dev server port

`quasar.config.js`:
```js
devServer: { port: <YOUR_FRONTEND_DEV_PORT>, open: true },
```
or one-off: `npx quasar dev -p <YOUR_FRONTEND_DEV_PORT>`.

Update the `proxy_pass` port in 6.3 to match — a mismatch here means `502 Bad Gateway`.

### 6.5 Apply the config

**1. Check Nginx is running:**
```bash
sudo service nginx status
```
Not running? `sudo service nginx start`.

**2. Edit the config:**
```bash
sudo nano /etc/nginx/sites-available/ipt2
```
Add/update the `location /<YOUR_USERNAME>-wui/ { ... }` block from 6.3. Save (`Ctrl+O`, Enter),
exit (`Ctrl+X`).

> **Shared container:** this file is shared by everyone on the container — only add/edit your
> own `location` block, never a classmate's. Deleting or changing someone else's breaks their
> setup, not just yours.

**3. Validate before touching the live service:**
```bash
sudo nginx -t
```
Don't reload if this reports an error — fix the line it points to first.

**4. Reload Nginx:**
```bash
sudo service nginx reload
```

**5. Start the dev server** (separate terminal):
```bash
npm run dev
```

**6. If you changed the dev server port (6.4), reapply:** edit the `proxy_pass` port in the
config (step 2), re-validate (step 3), reload again (step 4) — Nginx won't pick up a port change
until you reload.

**7. Verify each layer:**
```bash
curl -I http://127.0.0.1:<YOUR_FRONTEND_DEV_PORT>/<YOUR_USERNAME>-wui/   # dev server
curl -I http://127.0.0.1:<YOUR_NGINX_PORT>/<YOUR_USERNAME>-wui/          # nginx, local
curl -I http://<YOUR_LAB_SERVER_IP>:<YOUR_HOST_PORT>/<YOUR_USERNAME>-wui/ # full chain
```
All three should return `200`. First failure tells you which layer is broken.

### 6.6 Production build instead of dev server

```bash
npm run build   # after setting 6.1
```
```nginx
location /<YOUR_USERNAME>-wui/ {
    alias /path/to/appserver/frontend/dist/spa/;
    index index.html;
    try_files $uri $uri/ /<YOUR_USERNAME>-wui/index.html;
}
```
No dev server needed — re-run `npm run build` to update the deployed copy.

---

## 7. Troubleshooting

| What you see | Cause | Fix |
|---|---|---|
| Login hangs / connection error | Backend isn't running | Start it — `../demomanual/initialize.md` |
| Login fails, backend is running | `.env` URL doesn't match your assigned backend | Recheck §1.3 |
| `EACCES ... node_modules/.q-cache` | Dev server was run as a different user before | `sudo chown -R $(whoami):$(whoami) node_modules/.q-cache .quasar` |
| `npm run dev` fails — port already in use | On a shared container, a classmate's dev server already holds that port | Use your own port — §6.4 |
| `Failed to open default browser` | No GUI in this environment | Harmless — open the URL manually |
| Page reload loop through Nginx | Trailing-slash mismatch | Fix per §6.2 — frontend `proxy_pass` needs no trailing slash |
| `502 Bad Gateway` | Nothing listening on the proxied port | Check dev server is running on the port `proxy_pass` expects (§6.4) |
| `nginx -t` syntax error | Typo — usually a missing `;` or `{`/`}` | Fix the reported line, re-run `nginx -t` before reloading |
