#!/bin/bash
# Hwpad Linux 설치: Ubuntu·Debian 계열은 .deb, 그 밖에는 AppImage 와 바로가기를 만든다.
set -euo pipefail
REPO="zoo3323/hwpad"
BASE="https://github.com/$REPO/releases/latest/download"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# 예전 이름(K-Doc)으로 깔린 것은 지운다.
if command -v dpkg >/dev/null 2>&1 && dpkg -s k-doc >/dev/null 2>&1; then
  sudo apt-get remove -y k-doc || true
fi
rm -f "$HOME/Applications/k-doc.AppImage" "$HOME/.local/share/applications/k-doc.desktop" "$HOME/.local/share/icons/k-doc.png"

if command -v apt-get >/dev/null 2>&1 && command -v dpkg >/dev/null 2>&1; then
  echo "Hwpad(.deb) 내려받는 중..."
  curl -fL --progress-bar -o "$TMP/hwpad.deb" "$BASE/hwpad-linux-x64.deb"
  echo "설치하는 중... (비밀번호를 물으면 입력하세요)"
  sudo apt-get install -y "$TMP/hwpad.deb"
else
  echo "Hwpad(AppImage) 내려받는 중..."
  mkdir -p "$HOME/Applications" "$HOME/.local/share/applications" "$HOME/.local/share/icons"
  curl -fL --progress-bar -o "$HOME/Applications/hwpad.AppImage" "$BASE/hwpad-linux-x64.AppImage"
  chmod +x "$HOME/Applications/hwpad.AppImage"
  curl -fsSL -o "$HOME/.local/share/icons/hwpad.png" \
    "https://raw.githubusercontent.com/$REPO/main/apps/desktop/src-tauri/icons-app/logo-256.png"
  cat > "$HOME/.local/share/applications/hwpad.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Hwpad
Exec=$HOME/Applications/hwpad.AppImage %f
Icon=$HOME/.local/share/icons/hwpad.png
MimeType=application/x-hwp;application/vnd.hancom.hwpx;
Categories=Office;WordProcessor;
DESKTOP
fi
echo "설치 완료! 프로그램 목록에서 'Hwpad'를 실행하세요."
