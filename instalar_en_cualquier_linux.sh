#!/usr/bin/env bash
# ==============================================================================
# RepackForge — Instalador Automático Multi-Distro para Linux
# Soporta: Debian, Ubuntu, Linux Mint, Pop!_OS, Arch, CachyOS, Manjaro,
#          EndeavourOS, Fedora, Nobara, openSUSE
# ==============================================================================
set -euo pipefail

SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
PROJECT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
cd "$PROJECT_DIR"

echo "========================================================================"
echo "  ⚡ REPACKFORGE — INSTALACIÓN AUTOMÁTICA MULTI-DISTRO"
echo "========================================================================"

if [[ -f /etc/os-release ]]; then
    # shellcheck disable=SC1091
    source /etc/os-release
    echo "[INFO] Distribución detectada: ${PRETTY_NAME:-$ID}"
else
    ID="unknown"
fi

echo "[1/4] Instalando dependencias del sistema (wine, winetricks, cabextract, unzip, 7zip, PyQt6)..."
if command -v apt-get >/dev/null 2>&1; then
    sudo dpkg --add-architecture i386 2>/dev/null || true
    sudo apt-get update
    sudo apt-get install -y wine wine32 wine64 winetricks cabextract unzip p7zip-full curl wget python3 python3-venv python3-pip python3-pyqt6 || \
    sudo apt-get install -y wine winetricks cabextract unzip p7zip-full curl wget python3 python3-venv python3-pip
elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -Sy --needed --noconfirm wine-staging winetricks cabextract unzip p7zip curl wget python python-pip python-pyqt6 || \
    sudo pacman -Sy --needed --noconfirm wine winetricks cabextract unzip p7zip curl wget python python-pip python-pyqt6
    if pacman -Si umu-launcher >/dev/null 2>&1; then
        sudo pacman -S --needed --noconfirm umu-launcher || true
    elif command -v paru >/dev/null 2>&1; then
        paru -S --needed --noconfirm umu-launcher || true
    elif command -v yay >/dev/null 2>&1; then
        yay -S --needed --noconfirm umu-launcher || true
    fi
elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y wine winetricks cabextract unzip p7zip p7zip-plugins curl wget python3 python3-pip python3-pyqt6
    sudo dnf install -y umu-launcher 2>/dev/null || true
elif command -v zypper >/dev/null 2>&1; then
    sudo zypper install -y wine winetricks cabextract unzip p7zip-full curl wget python3 python3-pip python3-qt6
else
    echo "[WARN] Gestor de paquetes no reconocido automáticamente. Asegúrate de tener instalados: wine, winetricks, cabextract, unzip, 7z y python3."
fi

echo "[2/4] Configurando entorno Python (venv + PyQt6)..."
if [[ ! -d "$PROJECT_DIR/venv" ]]; then
    python3 -m venv "$PROJECT_DIR/venv"
fi
"$PROJECT_DIR/venv/bin/pip" install --upgrade pip
"$PROJECT_DIR/venv/bin/pip" install PyQt6

echo "[3/4] Generando iconos y accesos directos de RepackForge..."
chmod +x "$PROJECT_DIR/iniciar_instalador.sh" "$PROJECT_DIR/main.py" "$PROJECT_DIR/installer_engine.py" "$PROJECT_DIR/icon_generator.py"
"$PROJECT_DIR/venv/bin/python3" "$PROJECT_DIR/icon_generator.py"

mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/repackforge.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=RepackForge
GenericName=Instalador de Juegos y Repacks
Comment=Instalador Gaming para Linux Anti-ISDone.dll y unarc.dll (GE-Proton + umu-run)
Exec=$PROJECT_DIR/iniciar_instalador.sh
Icon=$PROJECT_DIR/assets/repackforge.png
Terminal=false
Categories=Game;Utility;
Keywords=Game;Repack;Installer;Wine;Proton;FitGirl;ElAmigos;ISDone;
StartupNotify=true
StartupWMClass=repackforge
EOF
chmod +x "$HOME/.local/share/applications/repackforge.desktop"

for DESK_DIR in "$HOME/Escritorio" "$HOME/Desktop"; do
    if [[ -d "$DESK_DIR" ]]; then
        cp -f "$HOME/.local/share/applications/repackforge.desktop" "$DESK_DIR/RepackForge.desktop"
        chmod +x "$DESK_DIR/RepackForge.desktop"
        gio set "$DESK_DIR/RepackForge.desktop" metadata::trusted true 2>/dev/null || true
    fi
done

echo "[4/4] Verificando / descargando última versión de GE-Proton..."
"$PROJECT_DIR/venv/bin/python3" -c "from installer_engine import ensure_ge_proton; ensure_ge_proton(print)"

echo "========================================================================"
echo "  ✅ REPACKFORGE INSTALADO Y LISTO"
echo "  Puedes abrirlo desde tu menú de aplicaciones, desde el Escritorio"
echo "  o ejecutando: ./iniciar_instalador.sh"
echo "========================================================================"
