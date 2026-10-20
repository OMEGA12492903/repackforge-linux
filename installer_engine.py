#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor de instalación Anti-Errores (ISDone.dll / unarc.dll) para Repacks y Setup.exe en Linux.
Gestiona la creación de WINEPREFIX limpio, configuración de Windows 10, instalación de vcrun2022
vía winetricks, descarga/gestión de GE-Proton y ejecución mediante umu-run con variables
de entorno críticas para evitar colapsos de memoria en descompresores pesados.
"""

import json
import os
import platform
import shutil
import signal
import subprocess
import sys
import tarfile
import time
import urllib.request
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple


PROJECT_DIR = Path(__file__).resolve().parent
RUNTIME_DIR = PROJECT_DIR / "runtime"
LOCAL_PROTON_DIR = RUNTIME_DIR / "GE-Proton"
LOCAL_UMU_BIN = RUNTIME_DIR / "umu-run"

# Variables de entorno obligatorias contra errores de ISDone.dll / unarc.dll / isskin.dll / RAM
MANDATORY_ENV_VARS: Dict[str, str] = {
    "WINE_LARGE_ADDRESS_AWARE": "1",
    "PROTON_NO_ESYNC": "1",
    "PROTON_NO_FSYNC": "1",
    "WINEDEBUG": "-all",
    "WINEDLLOVERRIDES": "winemenubuilder.exe=d;mfc42,mfc42u,msvcp60,msvcirt=n,b",
}


def detect_linux_distro() -> str:
    """Detecta la distribución de Linux leyendo /etc/os-release."""
    os_release = Path("/etc/os-release")
    if os_release.exists():
        data = {}
        for line in os_release.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                data[k.strip()] = v.strip().strip('"')
        return data.get("PRETTY_NAME") or data.get("NAME") or "Linux"
    return f"{platform.system()} {platform.release()}"


def find_umu_run() -> Optional[str]:
    """Busca el binario umu-run en la carpeta del proyecto, PATH o rutas conocidas."""
    candidates = [
        str(LOCAL_UMU_BIN),
        shutil.which("umu-run"),
        str(Path.home() / ".local/bin/umu-run"),
        str(Path.home() / ".local/share/faugus-launcher/umu-run"),
        "/opt/Hydra/resources/umu-run",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists() and os.access(candidate, os.X_OK):
            return str(Path(candidate).resolve())
    return None


def find_ge_proton() -> Optional[str]:
    """Busca GE-Proton en la carpeta local del proyecto o en Steam compatibilitytools.d."""
    candidates = [
        LOCAL_PROTON_DIR,
        Path.home() / ".local/share/Steam/compatibilitytools.d/Proton-GE Latest",
        Path.home() / ".steam/root/compatibilitytools.d/Proton-GE Latest",
    ]
    if RUNTIME_DIR.exists():
        for item in sorted(RUNTIME_DIR.glob("GE-Proton*"), reverse=True):
            if item.is_dir() and (item / "proton").exists():
                candidates.insert(0, item)

    steam_compat = Path.home() / ".local/share/Steam/compatibilitytools.d"
    if steam_compat.exists():
        for item in sorted(steam_compat.glob("*Proton*"), reverse=True):
            if item.is_dir() and (item / "proton").exists():
                candidates.append(item)

    for candidate in candidates:
        if candidate.exists() and (candidate / "proton").exists():
            return str(candidate.resolve())
    return None


def ensure_ge_proton(log_fn: Optional[Callable[[str], None]] = None) -> str:
    """
    Asegura que GE-Proton esté disponible en la carpeta local del proyecto (runtime/GE-Proton).
    Si ya existe en el sistema lo enlaza localmente; si no existe, descarga automáticamente
    la última versión de GE-Proton desde GitHub Releases.
    """
    def log(msg: str) -> None:
        if log_fn:
            log_fn(msg)

    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    existing = find_ge_proton()
    if existing:
        if not LOCAL_PROTON_DIR.exists():
            try:
                LOCAL_PROTON_DIR.symlink_to(existing)
                log(f"[OK] GE-Proton enlazado en carpeta local: {LOCAL_PROTON_DIR} -> {existing}")
            except OSError:
                pass
        return str(LOCAL_PROTON_DIR.resolve() if LOCAL_PROTON_DIR.exists() else existing)

    log("[INFO] No se encontró GE-Proton local. Consultando última versión en GitHub...")
    api_url = "https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases/latest"
    req = urllib.request.Request(api_url, headers={"User-Agent": "LinuxRepackInstaller/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        release_data = json.loads(resp.read().decode("utf-8"))

    tag_name = release_data.get("tag_name", "GE-Proton-Latest")
    tar_url = None
    for asset in release_data.get("assets", []):
        name = asset.get("name", "")
        if name.endswith(".tar.gz") and "aarch64" not in name:
            tar_url = asset.get("browser_download_url")
            break

    if not tar_url:
        raise RuntimeError("No se encontró el archivo .tar.gz de GE-Proton en GitHub Releases.")

    tar_path = RUNTIME_DIR / f"{tag_name}.tar.gz"
    log(f"[INFO] Descargando {tag_name} desde {tar_url} ...")
    urllib.request.urlretrieve(tar_url, str(tar_path))
    log(f"[INFO] Extrayendo {tar_path.name} en {RUNTIME_DIR} ...")
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=RUNTIME_DIR)
    tar_path.unlink(missing_ok=True)

    extracted_dir = RUNTIME_DIR / tag_name
    if extracted_dir.exists() and not LOCAL_PROTON_DIR.exists():
        LOCAL_PROTON_DIR.symlink_to(extracted_dir)

    resolved = find_ge_proton()
    if not resolved:
        raise RuntimeError("Error al verificar GE-Proton tras la extracción.")
    log(f"[OK] GE-Proton listo en: {resolved}")
    return resolved


def get_ge_proton_version(proton_path: Optional[str]) -> str:
    """Obtiene la versión legible de GE-Proton."""
    if not proton_path:
        return "Gestionado por umu-run"
    version_file = Path(proton_path) / "version"
    if version_file.exists():
        parts = version_file.read_text(encoding="utf-8", errors="ignore").strip().split()
        if len(parts) >= 2:
            return parts[1]
        if parts:
            return parts[0]
    return Path(proton_path).name


def check_system_dependencies() -> Dict[str, Tuple[bool, str]]:
    """
    Comprueba las herramientas críticas del sistema requeridas para descomprimir e instalar repacks.
    Devuelve un diccionario {nombre: (disponible, detalle)}.
    """
    results: Dict[str, Tuple[bool, str]] = {}

    umu_path = find_umu_run()
    wine_path = shutil.which("wine")
    if umu_path:
        results["umu-launcher"] = (True, umu_path)
    elif wine_path:
        results["umu-launcher / wine"] = (True, wine_path)
    else:
        results["umu-launcher"] = (False, "No encontrado")

    for tool, binary_candidates in [
        ("winetricks", ["winetricks"]),
        ("cabextract", ["cabextract"]),
        ("unzip", ["unzip"]),
        ("p7zip", ["7z", "7za", "p7zip"]),
    ]:
        found = None
        for b in binary_candidates:
            path = shutil.which(b)
            if path:
                found = path
                break
        results[tool] = (found is not None, found or "No encontrado")

    try:
        import PyQt6.QtCore  # noqa: F401
        results["python-pyqt6"] = (True, f"PyQt6 {PyQt6.QtCore.PYQT_VERSION_STR}")
    except Exception as exc:
        results["python-pyqt6"] = (False, str(exc))

    proton_path = find_ge_proton()
    if proton_path:
        results["GE-Proton"] = (True, f"{get_ge_proton_version(proton_path)} ({proton_path})")
    else:
        results["GE-Proton"] = (bool(umu_path), "Auto-gestionado por umu-run")

    return results


def build_installer_environment(
    prefix_path: Path,
    proton_path: Optional[str] = None,
) -> Dict[str, str]:
    """
    Construye el entorno con las variables críticas anti-errores de memoria/descompresión
    (ISDone.dll / unarc.dll) y las rutas del WINEPREFIX y GE-Proton.
    """
    env = os.environ.copy()
    extra_paths = [
        str(RUNTIME_DIR),
        str(Path.home() / ".local/bin"),
        "/usr/local/bin",
        "/usr/bin",
        "/bin",
    ]
    current_path = env.get("PATH", "")
    env["PATH"] = ":".join(extra_paths + ([current_path] if current_path else []))

    env["WINEPREFIX"] = str(prefix_path.resolve())
    env["GAMEID"] = "0"

    if proton_path and Path(proton_path).exists():
        resolved_proton = str(Path(proton_path).resolve())
        env["PROTONPATH"] = resolved_proton
        proton_wine = Path(resolved_proton) / "files/bin/wine"
        proton_wineserver = Path(resolved_proton) / "files/bin/wineserver"
        if proton_wine.exists():
            env["WINE"] = str(proton_wine)
        if proton_wineserver.exists():
            env["WINESERVER"] = str(proton_wineserver)
    else:
        env["PROTONPATH"] = "GE-Proton"

    for key, value in MANDATORY_ENV_VARS.items():
        env[key] = value

    return env


class InstallerEngine:
    """
    Motor de ejecución paso a paso para preparar un WINEPREFIX limpio e instalar un setup.exe.
    """

    def __init__(
        self,
        log_callback: Optional[Callable[[str], None]] = None,
        status_callback: Optional[Callable[[str, int], None]] = None,
    ) -> None:
        self.log_callback = log_callback
        self.status_callback = status_callback
        self._current_process: Optional[subprocess.Popen] = None
        self._cancelled = False

    def log(self, message: str) -> None:
        timestamp = time.strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        if self.log_callback:
            self.log_callback(formatted)
        else:
            print(formatted, flush=True)

    def set_status(self, text: str, progress: int) -> None:
        if self.status_callback:
            self.status_callback(text, progress)

    def cancel(self) -> None:
        """Cancela el proceso en ejecución y cierra wineserver del prefijo."""
        self._cancelled = True
        proc = self._current_process
        if proc and proc.poll() is None:
            self.log("[WARN] Cancelando proceso activo por solicitud del usuario...")
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except Exception:
                try:
                    proc.terminate()
                except Exception:
                    pass

    def _run_streaming_command(
        self,
        cmd: List[str],
        env: Dict[str, str],
        cwd: Optional[Path] = None,
        step_name: str = "Comando",
    ) -> int:
        """Ejecuta un comando capturando stdout/stderr en tiempo real línea por línea."""
        if self._cancelled:
            raise RuntimeError("Operación cancelada por el usuario.")

        self.log(f"$ {' '.join(cmd)}")
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            cwd=str(cwd) if cwd else None,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            start_new_session=True,
        )
        self._current_process = proc

        assert proc.stdout is not None
        for raw_line in proc.stdout:
            line = raw_line.rstrip("\r\n")
            if line.strip():
                self.log(f"  {line}")
            if self._cancelled:
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                except Exception:
                    proc.terminate()
                raise RuntimeError("Operación cancelada por el usuario.")

        return_code = proc.wait()
        self._current_process = None
        if return_code != 0:
            raise RuntimeError(f"{step_name} finalizó con código de error {return_code}.")
        return return_code

    def run_installation(
        self,
        setup_exe_path: str,
        install_dir_path: str,
        extra_args: Optional[List[str]] = None,
    ) -> Path:
        """
        Ejecuta todo el flujo de preparación e instalación:
        1. Crea un WINEPREFIX limpio y exclusivo para la instalación.
        2. Inicializa el prefijo con GE-Proton / umu-run y mapea la unidad G: a la carpeta destino.
        3. Ejecuta `winecfg /v win10` para fijar Windows 10.
        4. Ejecuta `winetricks -q vcrun6 vcrun6sp6 vcrun2022` en segundo plano.
        5. Ejecuta `setup.exe` inyectando las variables críticas anti-ISDone.dll / unarc.dll.
        """
        self._cancelled = False
        setup_exe = Path(setup_exe_path).expanduser().resolve()
        install_dir = Path(install_dir_path).expanduser().resolve()

        if not setup_exe.exists() or not setup_exe.is_file():
            raise FileNotFoundError(f"No se encontró el archivo instalador: {setup_exe}")

        self.set_status("Verificando entorno y GE-Proton...", 5)
        self.log("=" * 72)
        self.log("INICIANDO MOTOR DE INSTALACIÓN ANTI-ERRORES (ISDone.dll / unarc.dll)")
        self.log("=" * 72)
        self.log(f"Distribución detectada : {detect_linux_distro()}")
        self.log(f"Instalador seleccionado: {setup_exe}")
        self.log(f"Carpeta de destino     : {install_dir}")

        proton_path = ensure_ge_proton(self.log)
        umu_bin = find_umu_run()
        wine_bin = str(Path(proton_path) / "files/bin/wine")
        if not Path(wine_bin).exists():
            wine_bin = shutil.which("wine") or "wine"

        self.log(f"Runner activo          : {umu_bin or wine_bin}")
        self.log(f"Versión de GE-Proton   : {get_ge_proton_version(proton_path)} ({proton_path})")

        # 1. Crear un prefijo limpio (WINEPREFIX) exclusivo para esta instalación
        self.set_status("Creando WINEPREFIX limpio y exclusivo...", 15)
        install_dir.mkdir(parents=True, exist_ok=True)
        prefix_path = install_dir / ".wineprefix"

        if prefix_path.exists():
            self.log(f"[INFO] Limpiando prefijo previo para garantizar un WINEPREFIX 100% limpio: {prefix_path}")
            shutil.rmtree(prefix_path, ignore_errors=True)

        prefix_path.mkdir(parents=True, exist_ok=True)
        self.log(f"[OK] WINEPREFIX exclusivo creado en: {prefix_path}")

        env = build_installer_environment(prefix_path=prefix_path, proton_path=proton_path)

        self.log("-" * 72)
        self.log("Variables de entorno Anti-Crash inyectadas:")
        for k in [
            "WINEPREFIX",
            "PROTONPATH",
            "WINE_LARGE_ADDRESS_AWARE",
            "PROTON_NO_ESYNC",
            "PROTON_NO_FSYNC",
            "WINEDEBUG",
            "WINEDLLOVERRIDES",
        ]:
            self.log(f"  export {k}={env.get(k)}")
        self.log("-" * 72)

        # 2. Inicializar el prefijo con GE-Proton y configurar Windows 10 (winecfg /v win10)
        self.set_status("Inicializando prefijo y configurando Windows 10 (winecfg /v win10)...", 30)
        self.log("[PASO 1/3] Configurando versión de Windows en Windows 10 (winecfg /v win10)...")
        if umu_bin:
            self._run_streaming_command(
                [umu_bin, "winecfg", "/v", "win10"],
                env=env,
                cwd=install_dir,
                step_name="Inicialización de prefijo con umu-run",
            )
        self._run_streaming_command(
            [wine_bin, "winecfg", "/v", "win10"],
            env=env,
            cwd=install_dir,
            step_name="Configuración de Windows 10 (winecfg /v win10)",
        )

        # Mapear la carpeta de instalación como unidad G: y C:\Games para rutas cortas (evita errores de unarc.dll)
        dosdevices_dir = prefix_path / "dosdevices"
        dosdevices_dir.mkdir(parents=True, exist_ok=True)
        drive_g = dosdevices_dir / "g:"
        if drive_g.exists() or drive_g.is_symlink():
            drive_g.unlink(missing_ok=True)
        drive_g.symlink_to(install_dir)

        drive_c_games = prefix_path / "drive_c" / "Games"
        if not drive_c_games.exists() and not drive_c_games.is_symlink():
            try:
                drive_c_games.symlink_to(install_dir)
            except OSError:
                pass

        win_temp = prefix_path / "drive_c" / "windows" / "temp"
        win_temp.mkdir(parents=True, exist_ok=True)

        self.log(f"[OK] Carpeta de instalación mapeada en Wine como G:\\ y Z:{install_dir}")
        self.log("[OK] Versión de Windows fijada en Windows 10 (win10).")

        # 3. Ejecutar winetricks -q vcrun6 vcrun6sp6 vcrun2022 en segundo plano
        self.set_status("Instalando librerías C++ y MFC42 (vcrun6 + vcrun2022)...", 55)
        self.log(
            "[PASO 2/3] Ejecutando en segundo plano: winetricks -q vcrun6 vcrun6sp6 vcrun2022 "
            "(incluye mfc42.dll para isskin.dll y runtime C++ 2022)..."
        )
        winetricks_bin = shutil.which("winetricks") or "/usr/local/bin/winetricks"
        self._run_streaming_command(
            [winetricks_bin, "-q", "vcrun6", "vcrun6sp6", "vcrun2022"],
            env=env,
            cwd=install_dir,
            step_name="Instalación de vcrun6 + vcrun6sp6 + vcrun2022 (winetricks)",
        )
        self.log("[OK] Librerías MFC42 (isskin.dll) y Visual C++ 2022 (x86/x64) instaladas correctamente.")

        # 4. Ejecutar el setup.exe con todas las variables críticas inyectadas
        self.set_status(f"Ejecutando instalador {setup_exe.name}...", 80)
        self.log(f"[PASO 3/3] Lanzando instalador: {setup_exe.name}")
        self.log(
            "[INFO] Si el instalador muestra interfaz gráfica, selecciona G:\\ "
            f"(o Z:{install_dir}) como ruta de instalación."
        )

        args = list(extra_args) if extra_args else []
        if umu_bin:
            launch_cmd = [umu_bin, str(setup_exe)] + args
        else:
            launch_cmd = [wine_bin, str(setup_exe)] + args

        self._run_streaming_command(
            launch_cmd,
            env=env,
            cwd=setup_exe.parent,
            step_name=f"Ejecución de {setup_exe.name}",
        )

        wineserver_bin = env.get("WINESERVER") or shutil.which("wineserver")
        if wineserver_bin and Path(wineserver_bin).exists():
            subprocess.run([wineserver_bin, "-w"], env=env, check=False)

        self.set_status("¡Instalación finalizada con éxito!", 100)
        self.log("=" * 72)
        self.log("[ÉXITO] El instalador finalizó sin errores (código 0).")
        self.log(f"Archivos instalados en : {install_dir}")
        self.log(f"Prefijo Wine exclusivo : {prefix_path}")
        self.log("=" * 72)
        return prefix_path
