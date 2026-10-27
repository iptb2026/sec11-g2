# Bembank Android demo

The installable classroom APK is [`Bembank-demo.apk`](Bembank-demo.apk). It can connect to the
Bembank backend on any demo laptop; the laptop address is not baked into the APK.

## Demo setup

1. Copy or clone this repository onto the demo laptop and use its already configured Python and
   database environment.
2. In `personal/evanoso/appserver`, start the API:

   ```bash
   chmod +x run.sh
   ./run.sh
   ```

   The API listens on all network interfaces on TCP port `5001`.
3. Connect the laptop and Android phone to the same private Wi-Fi network or phone hotspot.
4. Find the laptop's Wi-Fi IPv4 address:
   - Windows: run `ipconfig` and read **IPv4 Address** under the active Wi-Fi adapter.
   - Linux: run `ip -4 addr` and read the address for the active Wi-Fi adapter.
5. If the laptop firewall asks, allow inbound TCP port `5001` on the private network.
6. Copy [`Bembank-demo.apk`](Bembank-demo.apk) to the phone and install it. Android may ask you
   to allow installation from that file manager or browser.
7. Open Bembank. On the phone sign-in screen, tap the blue **B** logo to reveal **Demo server**.
8. Enter the laptop address as `http://<IPv4-address>:5001/`, for example:

   ```text
   http://192.168.1.20:5001/
   ```

9. Save, then sign in. The address remains saved on that phone. Tap the blue **B** again to
   change it when using another laptop or network.

Do not enter `localhost` or `127.0.0.1`; inside the APK those addresses mean the phone itself.
On desktop, the same settings dialog opens by clicking the first **b** in **bembank** or pressing
the `B` key while no text field is active.

## Quick troubleshooting

- **Cannot connect:** confirm both devices are on the same network and cellular data/VPN is off.
- **Still cannot connect:** open `http://<IPv4-address>:5001/` in the phone browser. A JSON health
  response means the network path works; otherwise check the API process and firewall.
- **Address changed:** reconnecting the laptop to Wi-Fi can assign a new IPv4 address. Tap the
  blue **B** and save the new address.
- **Installation blocked:** enable **Install unknown apps** only for the app used to open this APK,
  install it, then turn that permission off again.

This classroom build permits local HTTP so it works without certificates. Use a private hotspot
and simulated accounts only; use HTTPS and a properly signed release for real deployment.

## Rebuild the APK

With Node.js 22.12+ and Android SDK installed:

```bash
cd personal/evanoso/appserver/frontend
npm ci
ANDROID_HOME=/path/to/Android/Sdk npm run build -- --mode capacitor -T android --debug
```

The generated APK is under
`src-capacitor/android/app/build/outputs/apk/debug/app-debug.apk`.
