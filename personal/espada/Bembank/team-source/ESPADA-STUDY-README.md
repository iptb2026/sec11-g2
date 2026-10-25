# BEMBank team study demo

This is a copy of the team's frontend and backend. It uses a separate local SQLite database, so it does not change Espada's earlier banking database. It is a classroom demo, not a real banking service.

## Start the backend

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/seed_presentation.py
sh run-demo.sh
```

The seed creates fictional users and accounts. The customer login is `sofia.reyes` / `BembankDemo!2026`. On first login, choose and confirm a six-digit PIN. The server must remain running during phone testing. Sessions are invalidated when the server restarts unless `BEMBANK_SECRET_KEY` is set.

Put the phone and laptop on the same Wi-Fi. Enter `http://LAPTOP_IP:5001` in the Android app's Server address field. Replace `LAPTOP_IP` with the laptop's actual Wi-Fi address; do not use `127.0.0.1` on the phone. The address is saved on the phone.

The Android debug build allows plain HTTP for a local classroom demonstration. Never use real banking credentials, money, or personal customer data with it. For shared or production deployment, configure a separate secure database, HTTPS, and a private persistent `BEMBANK_SECRET_KEY`.

## Build the app

In `frontend/`, install Node dependencies with `npm ci`, then `npm ci --prefix src-capacitor`. Install JDK 21 and Android SDK platform 36, set `ANDROID_HOME`, and run `npx quasar build -m capacitor -T android --debug`. The APK is at `src-capacitor/android/app/build/outputs/apk/debug/app-debug.apk`.
