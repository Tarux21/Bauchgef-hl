#!/usr/bin/env bash
# Richtet den Bauchgefühl-Erinnerungs-Server auf dem Raspberry Pi ein.
# Aufruf im Ordner server/:  bash install.sh
# Danach erreichbar im eigenen Tailscale-Netz unter https://<pi-name>.<tailnet>.ts.net
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
USER_NAME="$(id -un)"
PORT="${BG_PORT:-8787}"
# Öffentlicher HTTPS-Port im Tailnet. 443 ist oft schon belegt (z. B. Vaultwarden), dann z. B. BG_HTTPS_PORT=8444
HTTPS_PORT="${BG_HTTPS_PORT:-443}"

echo "== 1/4 Python-Pakete"
if sudo apt-get install -y python3-pywebpush python3-cryptography >/dev/null 2>&1; then
  PY=/usr/bin/python3
  echo "   pywebpush aus Raspberry Pi OS installiert"
else
  sudo apt-get install -y python3-venv >/dev/null
  python3 -m venv "$DIR/.venv"
  "$DIR/.venv/bin/pip" install --quiet pywebpush
  PY="$DIR/.venv/bin/python"
  echo "   pywebpush in $DIR/.venv installiert"
fi

echo "== 2/4 Selbsttest"
"$PY" "$DIR/bauchgefuehl_push.py" --selftest

echo "== 3/4 Dienst einrichten (startet automatisch, auch nach Stromausfall)"
sudo tee /etc/systemd/system/bauchgefuehl-push.service >/dev/null <<EOF
[Unit]
Description=Bauchgefuehl Erinnerungs-Server
After=network-online.target
Wants=network-online.target

[Service]
User=$USER_NAME
WorkingDirectory=$DIR
Environment=BG_PORT=$PORT
Environment=BG_TZ=Europe/Berlin
ExecStart=$PY $DIR/bauchgefuehl_push.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now bauchgefuehl-push
sleep 2
curl -fsS "http://127.0.0.1:$PORT/api/health" && echo

echo "== 4/4 Im Tailscale-Netz per HTTPS freigeben (nur eigene Geräte, kein Funnel)"
# Nicht versehentlich einen anderen Dienst auf Port 443 überschreiben
if [ "$HTTPS_PORT" = "443" ] && sudo tailscale serve status 2>/dev/null | grep -qE "^https://[^ :]+\.ts\.net( |$)"; then
  echo "Port 443 ist in tailscale serve schon belegt. Bitte mit BG_HTTPS_PORT=8444 bash install.sh erneut starten."; exit 1
fi
sudo tailscale serve --bg --https="$HTTPS_PORT" "$PORT"
tailscale serve status
echo
echo "Fertig. Die Adresse oben (https://….ts.net, ggf. mit :Port) in der App unter Einstellungen → Erinnerungen eintragen."
