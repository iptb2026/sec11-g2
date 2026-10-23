# Espada customer mobile app

Requirements: Node 20+, JDK 21, Android SDK platform 35 and build-tools 35.0.0. These versions match `src-capacitor/android/variables.gradle`.

1. Configure the MySQL connection in `../appserver/app/core/config.py` for the laptop's local database.
2. Run `cd ../appserver && .venv/bin/python seed_demo.py && ./run.sh`.
3. Put the laptop and Android phone on the same Wi-Fi.
4. Find the laptop Wi-Fi IP (`ipconfig` on Windows or `hostname -I` on Linux). In BEMBank's login screen, enter `http://YOUR_LAPTOP_IP:5005` as **Server address**. The app saves this per phone, so no APK rebuild is needed.
5. Run `npm install` and build the debug APK with `npm run android:build`.
6. Install it on one connected device/emulator with `npm run android:install`, or use `npm run android:run` to build and install.

For deployment through NGINX, use the server URL and path assigned by the class deployment. The debug build permits the classroom's plain-HTTP API; production deployment should use HTTPS.

Each phone-test APK is copied into `releases/` with a new filename. Install the newest named APK after removing the older Espada Bank app.

Demo logins: `espada` / `Espada1234` (administrator) and `marie.santos` / `Demo1234` (customer). All demo data is fictional.
