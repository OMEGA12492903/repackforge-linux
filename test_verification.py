#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Autoverificación E2E del Instalador Anti-ISDone.dll / unarc.dll.
"""

import shutil
import sys
import urllib.request
from pathlib import Path

from installer_engine import (
    MANDATORY_ENV_VARS,
    PROJECT_DIR,
    InstallerEngine,
    build_installer_environment,
    check_system_dependencies,
    ensure_ge_proton,
)


def verify_dependencies() -> None:
    print("=== [1/3] VERIFICANDO DEPENDENCIAS DEL SISTEMA ===")
    deps = check_system_dependencies()
    missing = []
    for name, (ok, detail) in deps.items():
        status = "OK" if ok else "ERROR"
        print(f"  [{status}] {name:<16}: {detail}")
        if not ok:
            missing.append(name)
    if missing:
        raise RuntimeError(f"Faltan dependencias obligatorias: {', '.join(missing)}")
    print("  -> Todas las dependencias del sistema están instaladas y operativas.\n")


def verify_pyqt6_gui() -> None:
    print("=== [2/3] VERIFICANDO INTERFAZ GRÁFICA PYQT6 ===")
    from PyQt6.QtWidgets import QApplication
    from main import RepackInstallerWindow

    app = QApplication.instance() or QApplication(sys.argv)
    window = RepackInstallerWindow()
    assert window.btn_select_setup is not None
    assert window.btn_select_dest is not None
    assert window.btn_install is not None
    assert window.console is not None
    assert "PREPARAR E INSTALAR" in window.btn_install.text().upper()
    console_text = window.console.toPlainText()
    for key, val in MANDATORY_ENV_VARS.items():
        assert f"{key}={val}" in console_text, f"Falta variable {key}={val} en consola inicial"
    window.close()
    print("  -> Ventana PyQt6, botones, selectores y consola en vivo verificados al 100%.\n")


def verify_backend_with_7zip() -> None:
    print("=== [3/3] VERIFICANDO BACKEND E2E CON 7-ZIP 64-BIT (7z-x64.exe /S) ===")
    tests_dir = PROJECT_DIR / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    exe_path = tests_dir / "7z-x64.exe"

    if not exe_path.exists() or exe_path.stat().st_size < 500_000:
        url = "https://www.7-zip.org/a/7z2409-x64.exe"
        print(f"  Descargando instalador oficial 7z-x64.exe desde {url} ...")
        urllib.request.urlretrieve(url, str(exe_path))

    print(f"  Instalador de prueba listo: {exe_path} ({exe_path.stat().st_size} bytes)")

    install_target = tests_dir / "verified_7z_install"
    if install_target.exists():
        shutil.rmtree(install_target)

    proton_path = ensure_ge_proton(print)
    env_check = build_installer_environment(install_target / ".wineprefix", proton_path)
    for k, expected_v in MANDATORY_ENV_VARS.items():
        actual_v = env_check.get(k)
        assert actual_v == expected_v, f"Variable {k} incorrecta: {actual_v} != {expected_v}"

    engine = InstallerEngine(
        log_callback=lambda msg: print(f"  {msg}", flush=True),
        status_callback=lambda st, pct: print(f"  >>> [{pct}%] {st}", flush=True),
    )

    prefix_path = engine.run_installation(
        setup_exe_path=str(exe_path),
        install_dir_path=str(install_target),
        extra_args=["/S", "/D=G:\\"],
    )

    assert prefix_path.exists(), "El WINEPREFIX no fue creado"
    assert (prefix_path / "system.reg").exists(), "Falta system.reg en el WINEPREFIX"

    sys32_msvcp = prefix_path / "drive_c/windows/system32/msvcp140.dll"
    syswow_msvcp = prefix_path / "drive_c/windows/syswow64/msvcp140.dll"
    syswow_mfc42 = prefix_path / "drive_c/windows/syswow64/mfc42.dll"
    assert sys32_msvcp.exists(), "vcrun2022 (64-bit msvcp140.dll) no se instaló en system32"
    assert syswow_msvcp.exists(), "vcrun2022 (32-bit msvcp140.dll) no se instaló en syswow64"
    assert syswow_mfc42.exists(), "vcrun6 (mfc42.dll) no se instaló en syswow64"

    extracted_7z_exe = install_target / "7z.exe"
    extracted_7z_dll = install_target / "7z.dll"
    extracted_7zfm = install_target / "7zFM.exe"

    assert extracted_7z_exe.exists(), f"No se encontró 7z.exe extraído en {install_target}"
    assert extracted_7z_dll.exists(), f"No se encontró 7z.dll extraído en {install_target}"
    assert extracted_7zfm.exists(), f"No se encontró 7zFM.exe extraído en {install_target}"

    print("\n========================================================================")
    print(" AUTOVERIFICACIÓN SUPERADA AL 100% (CÓDIGO DE SALIDA 0)")
    print("========================================================================")


if __name__ == "__main__":
    verify_dependencies()
    verify_pyqt6_gui()
    verify_backend_with_7zip()
