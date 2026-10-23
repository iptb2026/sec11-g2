# Espada banking project

This follows the course template's split between the API, customer Android app, and deployment files.

```text
espada/
├── appserver/       FastAPI API, dependencies, tests, and service launcher
├── frontendmobile/  Customer-only Quasar + Capacitor Android app
├── deployment/      NGINX and Supervisor configuration to install on the server
└── appclient/       Earlier practice copy; not used by the current app
```

## Run locally

```bash
cd appserver
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
./run.sh
```

For Android setup and API address configuration, read `frontendmobile/README.md`.

## Deploy

On the class server, copy `deployment/nginx-espada.conf` to NGINX's site configuration and `deployment/espada_service.conf` to `/etc/supervisor/conf.d/`. The provided Supervisor file assumes the course path `/home/admin/personal/espada`; change that path only if your assigned server uses a different one.
