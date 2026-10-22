# Mini Banking System Frontend

Quasar + Vite frontend for the FastAPI app in `../app`.

## Setup

```bash
npm install
npm run dev
```

The dev server runs at `http://localhost:9000`. The frontend is configured to call the backend
at `http://127.0.0.1:5006/`. Keep the trailing slash in `QCLI_API_BASE_URL`.

Start the backend on port `5006`:

```bash
cd /home/admin/sec11-g2/personal/costas/appserver
source /opt/virt/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 5006
```

After creating the `ADMIN`, `STAFF`, and `CUSTOMER` roles, sign in as an admin and open
**Users**. Create a staff user with `role_id` for `STAFF` and a customer user with `role_id` for
`CUSTOMER`; passwords are entered as `password` and are hashed by the API.

The app uses `/costas-wui/` as its deployment base path and hash routing. For an Nginx dev
proxy, proxy `/costas-wui/` to port `9000` without a trailing slash in `proxy_pass`.

## Current scope

The existing backend currently serves Layer 1 reference data: roles, account types, banks, and
fee types. Those four admin pages have working list/create/edit/delete flows. The remaining
guide routes, role shells, and route guards are included and will activate as the corresponding
backend layers are added.

## Production build

```bash
npm run build
```

Output is written to `dist/spa/`.