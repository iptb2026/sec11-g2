# Bembank classroom demo

The easiest setup is Docker Desktop. It starts the website, API, MariaDB, and fictional demo data together.

## Windows quick start

1. Install [Git](https://git-scm.com/download/win) and [Docker Desktop](https://www.docker.com/products/docker-desktop/). During Docker setup, enable WSL 2 when asked.
2. Open PowerShell and run:

   ```powershell
   git clone https://github.com/iptb2026/sec11-g2.git
   cd sec11-g2\personal\evanoso
   docker compose up --build
   ```

3. Wait until the logs say the application started, then open <http://localhost:9000/bembank/>.
4. Stop it with `Ctrl+C`. Start it again later with `docker compose up`.

If Docker says a port is already in use, close the program using port 9000 or change `"9000:80"` to `"9001:80"` in `docker-compose.yml`, then open port 9001 instead.

## Demo logins

All accounts use password `BembankDemo!2026`.

| Role | Username |
| --- | --- |
| Admin | `alex.admin` |
| Staff | `jamie.staff` |
| Customer | `sofia.reyes` |
| Customer | `marco.santos` |
| Customer | `isla.retail` |

PINs are created when prompted and cannot be read back. This project contains fictional classroom data only.

## Reset the demo database

This deletes only the Docker database volume for this project and recreates the sample data:

```powershell
docker compose down -v
docker compose up --build
```

## Copy-paste prompt for an AI assistant

> Help me run the Bembank classroom project on Windows. The repository is https://github.com/iptb2026/sec11-g2 and the project folder is personal/evanoso. Use Docker Desktop and PowerShell. Check that Docker Desktop is running, clone or update the repository, run `docker compose up --build` inside personal/evanoso, and help me fix any exact error I paste. Do not change or delete files outside this project. The website should open at http://localhost:9000/bembank/.

## Android demo

The optional [`Bembank-demo.apk`](Bembank-demo.apk) connects to a backend running on a laptop. Both devices must be on the same private Wi-Fi. In the app, tap the Bembank logo and enter `http://<laptop-ip>:5001/`. The Docker setup does not expose port 5001 by default; add `ports: ["5001:5001"]` to the `backend` service only when the APK is needed.

Do not use this classroom configuration or its demo secrets for a real bank or public deployment.
