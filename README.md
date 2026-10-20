# ⚡ RepackForge — Instalador de Juegos & Repacks para Linux

Aplicación gráfica en **Python + PyQt6** diseñada específicamente para ejecutar instaladores de juegos (`setup.exe`, FitGirl, ElAmigos, DODI, InnoSetup) en cualquier distribución de Linux **sin errores de memoria, `ISDone.dll`, `unarc.dll` ni `isskin.dll`**.

---

## 🚀 Instalación rápida en cualquier Linux (1 comando)

Cuando instales tu nuevo sistema operativo Linux (**Debian, Ubuntu, Linux Mint, Arch Linux, CachyOS, Manjaro, Fedora, Nobara, openSUSE**), abre una terminal y pega:

```bash
git clone https://github.com/OMEGA12492903/repackforge-linux.git
cd repackforge-linux
chmod +x instalar_en_cualquier_linux.sh iniciar_instalador.sh
./instalar_en_cualquier_linux.sh
```

Para abrir el programa en cualquier momento:
```bash
./iniciar_instalador.sh
```
*(También se creará automáticamente el icono **RepackForge** en tu Escritorio y en tu menú de aplicaciones).*

---

## 🛡️ ¿Qué hace RepackForge automáticamente por cada juego?

1. **Prefijo Limpio Exclusivo (`WINEPREFIX`)**:
   Crea un prefijo limpio en `<carpeta_del_juego>/.wineprefix` y mapea la carpeta de destino como la unidad **`G:\`** en Wine para evitar errores de rutas largas en `unarc.dll`.
2. **Pre-configuración en Segundo Plano**:
   - Fija la versión de Windows en **Windows 10** (`winecfg /v win10`).
   - Instala automáticamente **`vcrun6` + `vcrun6sp6`** (`MFC42.DLL` y `msvcp60.dll` para que nunca falle `isskin.dll` en instaladores con skins personalizados) y **`vcrun2022`** (Visual C++ 2015–2022 x86/x64).
3. **Inyección de Variables Anti-Crash (RAM / Fsync / Esync)**:
   - `WINE_LARGE_ADDRESS_AWARE=1`
   - `PROTON_NO_ESYNC=1`
   - `PROTON_NO_FSYNC=1`
   - `WINEDEBUG=-all`
   - `WINEDLLOVERRIDES="winemenubuilder.exe=d;mfc42,mfc42u,msvcp60,msvcirt=n,b"`
4. **Gestión automática de GE-Proton**:
   Detecta si ya tienes `GE-Proton` instalado en Steam (`compatibilitytools.d`) y, si no lo encuentra, descarga automáticamente la última versión desde GitHub Releases en la carpeta `runtime/`.

---

## 🧪 Autoverificación incluida

Para comprobar que todo el motor funciona al 100% en tu nuevo sistema:
```bash
./venv/bin/python3 test_verification.py
```
