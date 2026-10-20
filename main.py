#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RepackForge — Interfaz Gráfica PyQt6 para Instalación de Juegos (setup.exe / Repacks) en Linux
Diseñado contra errores de memoria, ISDone.dll y unarc.dll.
"""

import shlex
import sys
from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap, QTextCursor
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from installer_engine import (
    MANDATORY_ENV_VARS,
    PROJECT_DIR,
    InstallerEngine,
    check_system_dependencies,
    detect_linux_distro,
    find_ge_proton,
    get_ge_proton_version,
)


ICON_PNG_PATH = PROJECT_DIR / "assets" / "repackforge.png"
ICON_SVG_PATH = PROJECT_DIR / "assets" / "repackforge.svg"


def load_app_icon() -> QIcon:
    """Carga el icono oficial de RepackForge (generándolo si aún no existe)."""
    if not ICON_PNG_PATH.exists():
        try:
            from icon_generator import generate_all_icons
            generate_all_icons()
        except Exception:
            pass
    if ICON_PNG_PATH.exists():
        return QIcon(str(ICON_PNG_PATH))
    if ICON_SVG_PATH.exists():
        return QIcon(str(ICON_SVG_PATH))
    return QIcon.fromTheme("applications-games")


class InstallerWorker(QThread):
    """Hilo en segundo plano para ejecutar la preparación del prefijo y el setup.exe sin bloquear la GUI."""

    log_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str, int)
    finished_success = pyqtSignal(str)
    finished_error = pyqtSignal(str)

    def __init__(
        self,
        setup_exe: str,
        install_dir: str,
        extra_args: Optional[List[str]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setup_exe = setup_exe
        self.install_dir = install_dir
        self.extra_args = extra_args or []
        self.engine = InstallerEngine(
            log_callback=self.log_signal.emit,
            status_callback=self.status_signal.emit,
        )

    def run(self) -> None:
        try:
            prefix_path = self.engine.run_installation(
                setup_exe_path=self.setup_exe,
                install_dir_path=self.install_dir,
                extra_args=self.extra_args,
            )
            self.finished_success.emit(str(prefix_path))
        except Exception as exc:
            self.finished_error.emit(str(exc))

    def stop(self) -> None:
        self.engine.cancel()


class RepackInstallerWindow(QMainWindow):
    """Ventana principal de RepackForge (Anti-ISDone / unarc.dll)."""

    def __init__(self) -> None:
        super().__init__()
        self.worker: Optional[InstallerWorker] = None
        self.setWindowTitle(
            "RepackForge — Instalador de Juegos & Repacks (Anti-ISDone.dll / unarc.dll)"
        )
        self.setWindowIcon(load_app_icon())
        self.resize(980, 760)
        self.setMinimumSize(820, 640)
        self._apply_dark_gaming_theme()
        self._build_ui()
        self._populate_initial_logs()

    def _apply_dark_gaming_theme(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow, QWidget#centralWidget {
                background-color: #0f141c;
                color: #e6edf3;
                font-family: 'Sans Serif', 'DejaVu Sans', 'Noto Sans';
                font-size: 13px;
            }
            QFrame#cardFrame {
                background-color: #161d28;
                border: 1px solid #263244;
                border-radius: 10px;
            }
            QLabel#titleLabel {
                font-size: 21px;
                font-weight: bold;
                color: #58a6ff;
            }
            QLabel#subtitleLabel {
                font-size: 12px;
                color: #8b949e;
            }
            QLabel#sectionHeader {
                font-size: 13px;
                font-weight: bold;
                color: #79c0ff;
            }
            QLabel#envBadge {
                background-color: #112438;
                color: #56d364;
                border: 1px solid #1f6feb;
                border-radius: 5px;
                padding: 4px 8px;
                font-family: 'Monospace', 'DejaVu Sans Mono';
                font-size: 11px;
            }
            QLineEdit {
                background-color: #0d1117;
                color: #e6edf3;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 8px 10px;
                selection-background-color: #1f6feb;
            }
            QLineEdit:focus {
                border: 1px solid #58a6ff;
            }
            QPushButton {
                background-color: #212835;
                color: #e6edf3;
                border: 1px solid #384459;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2c3648;
                border-color: #58a6ff;
            }
            QPushButton:disabled {
                background-color: #161b22;
                color: #484f58;
                border-color: #21262d;
            }
            QPushButton#installButton {
                background-color: #238636;
                color: #ffffff;
                border: 1px solid #2ea043;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                padding: 14px 24px;
            }
            QPushButton#installButton:hover {
                background-color: #2ea043;
                border-color: #3fb950;
            }
            QPushButton#installButton:disabled {
                background-color: #193c23;
                color: #7d8590;
                border-color: #1f4c2b;
            }
            QPushButton#cancelButton {
                background-color: #da3633;
                color: #ffffff;
                border: 1px solid #f85149;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 14px 18px;
            }
            QPushButton#cancelButton:hover {
                background-color: #f85149;
            }
            QPlainTextEdit#logConsole {
                background-color: #090d12;
                color: #d2f4dc;
                border: 1px solid #263244;
                border-radius: 8px;
                padding: 8px;
                font-family: 'Monospace', 'DejaVu Sans Mono';
                font-size: 12px;
            }
            QProgressBar {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
                min-height: 22px;
            }
            QProgressBar::chunk {
                background-color: #238636;
                border-radius: 5px;
            }
            """
        )

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(18, 16, 18, 16)
        main_layout.setSpacing(12)

        header_card = QFrame()
        header_card.setObjectName("cardFrame")
        header_row = QHBoxLayout(header_card)
        header_row.setContentsMargins(16, 12, 16, 12)
        header_row.setSpacing(14)

        logo_label = QLabel()
        if ICON_PNG_PATH.exists():
            pix = QPixmap(str(ICON_PNG_PATH)).scaled(
                58,
                58,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo_label.setPixmap(pix)
        logo_label.setFixedSize(60, 60)
        header_row.addWidget(logo_label)

        header_text_layout = QVBoxLayout()
        header_text_layout.setSpacing(4)

        title = QLabel("RepackForge — Instalador de Juegos & Repacks (Anti-ISDone / unarc.dll)")
        title.setObjectName("titleLabel")

        distro = detect_linux_distro()
        proton_path = find_ge_proton()
        proton_ver = get_ge_proton_version(proton_path)
        subtitle = QLabel(
            f"Sistema: {distro}  |  Motor: umu-run + {proton_ver}  |  "
            "Pre-configuración automática: WINEPREFIX limpio + Windows 10 + vcrun6 + vcrun2022"
        )
        subtitle.setObjectName("subtitleLabel")

        header_text_layout.addWidget(title)
        header_text_layout.addWidget(subtitle)
        header_row.addLayout(header_text_layout, stretch=1)
        main_layout.addWidget(header_card)

        paths_card = QFrame()
        paths_card.setObjectName("cardFrame")
        paths_grid = QGridLayout(paths_card)
        paths_grid.setContentsMargins(16, 14, 16, 14)
        paths_grid.setHorizontalSpacing(12)
        paths_grid.setVerticalSpacing(10)

        lbl_setup = QLabel("1. Archivo Instalador (setup.exe):")
        lbl_setup.setObjectName("sectionHeader")
        self.setup_input = QLineEdit()
        self.setup_input.setPlaceholderText("Selecciona el archivo setup.exe del juego o repack...")
        metro_setup = Path.home() / "Descargas" / "Metro Last Light Redux" / "setup.exe"
        if metro_setup.exists():
            self.setup_input.setText(str(metro_setup))
        self.btn_select_setup = QPushButton("Seleccionar setup.exe")
        self.btn_select_setup.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select_setup.clicked.connect(self._on_select_setup)

        lbl_dest = QLabel("2. Carpeta de Instalación del Juego:")
        lbl_dest.setObjectName("sectionHeader")
        self.dest_input = QLineEdit()
        default_games_dir = (
            Path.home() / "Games" / "Metro Last Light Redux"
            if metro_setup.exists()
            else Path.home() / "Games" / "NuevoJuego"
        )
        self.dest_input.setText(str(default_games_dir))
        self.dest_input.setPlaceholderText("Selecciona la carpeta donde se instalará el juego...")
        self.btn_select_dest = QPushButton("Elegir Carpeta Destino")
        self.btn_select_dest.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select_dest.clicked.connect(self._on_select_dest)

        lbl_args = QLabel("3. Argumentos Opcionales (ej. /S para silencioso):")
        lbl_args.setObjectName("sectionHeader")
        self.args_input = QLineEdit()
        self.args_input.setPlaceholderText(
            "Dejar vacío para instalación interactiva normal (o usar /S en tests silenciosos)"
        )

        paths_grid.addWidget(lbl_setup, 0, 0, 1, 2)
        paths_grid.addWidget(self.setup_input, 1, 0)
        paths_grid.addWidget(self.btn_select_setup, 1, 1)

        paths_grid.addWidget(lbl_dest, 2, 0, 1, 2)
        paths_grid.addWidget(self.dest_input, 3, 0)
        paths_grid.addWidget(self.btn_select_dest, 3, 1)

        paths_grid.addWidget(lbl_args, 4, 0, 1, 2)
        paths_grid.addWidget(self.args_input, 5, 0, 1, 2)

        main_layout.addWidget(paths_card)

        env_card = QFrame()
        env_card.setObjectName("cardFrame")
        env_layout = QVBoxLayout(env_card)
        env_layout.setContentsMargins(16, 10, 16, 10)
        env_layout.setSpacing(6)

        env_header = QLabel(
            "Protección Activa contra Errores de Memoria y Descompresión (FitGirl / ElAmigos / InnoSetup):"
        )
        env_header.setObjectName("sectionHeader")
        env_layout.addWidget(env_header)

        badges_row = QHBoxLayout()
        badges_row.setSpacing(8)
        for k, v in MANDATORY_ENV_VARS.items():
            badge = QLabel(f'{k}={v}')
            badge.setObjectName("envBadge")
            badges_row.addWidget(badge)
        badges_row.addStretch()
        env_layout.addLayout(badges_row)
        main_layout.addWidget(env_card)

        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        self.btn_install = QPushButton("⚡  PREPARAR E INSTALAR")
        self.btn_install.setObjectName("installButton")
        self.btn_install.setMinimumHeight(54)
        self.btn_install.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_install.clicked.connect(self._on_start_install)

        self.btn_cancel = QPushButton("Detener")
        self.btn_cancel.setObjectName("cancelButton")
        self.btn_cancel.setMinimumHeight(54)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.clicked.connect(self._on_cancel_install)

        action_row.addWidget(self.btn_install, stretch=5)
        action_row.addWidget(self.btn_cancel, stretch=1)
        main_layout.addLayout(action_row)

        status_row = QHBoxLayout()
        self.lbl_status = QLabel("Estado: Listo para preparar el prefijo e instalar.")
        self.lbl_status.setObjectName("subtitleLabel")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedWidth(260)

        status_row.addWidget(self.lbl_status, stretch=1)
        status_row.addWidget(self.progress_bar)
        main_layout.addLayout(status_row)

        console_header_row = QHBoxLayout()
        lbl_console = QLabel("Consola de Logs en Vivo:")
        lbl_console.setObjectName("sectionHeader")
        btn_clear = QPushButton("Limpiar Consola")
        btn_clear.clicked.connect(self._on_clear_console)
        btn_copy = QPushButton("Copiar Logs")
        btn_copy.clicked.connect(self._on_copy_logs)

        console_header_row.addWidget(lbl_console)
        console_header_row.addStretch()
        console_header_row.addWidget(btn_copy)
        console_header_row.addWidget(btn_clear)
        main_layout.addLayout(console_header_row)

        self.console = QPlainTextEdit()
        self.console.setObjectName("logConsole")
        self.console.setReadOnly(True)
        mono_font = QFont("DejaVu Sans Mono", 10)
        mono_font.setStyleHint(QFont.StyleHint.Monospace)
        self.console.setFont(mono_font)
        main_layout.addWidget(self.console, stretch=1)

    def _populate_initial_logs(self) -> None:
        self.append_log("========================================================================")
        self.append_log(" REPACKFORGE — MOTOR ANTI-ERRORES (ISDone.dll / unarc.dll) LISTO")
        self.append_log("========================================================================")
        self.append_log(f"Distribución Linux : {detect_linux_distro()}")
        deps = check_system_dependencies()
        for name, (ok, detail) in deps.items():
            mark = "OK" if ok else "FALTA"
            self.append_log(f"  [{mark}] {name:<15} -> {detail}")
        self.append_log("------------------------------------------------------------------------")
        self.append_log("Variables que se inyectarán al instalar:")
        for k, v in MANDATORY_ENV_VARS.items():
            self.append_log(f"  * {k}={v}")
        self.append_log("------------------------------------------------------------------------")
        self.append_log("Selecciona tu archivo setup.exe, elige la carpeta destino y pulsa")
        self.append_log("'PREPARAR E INSTALAR'.")

    def append_log(self, text: str) -> None:
        self.console.appendPlainText(text)
        cursor = self.console.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.console.setTextCursor(cursor)
        self.console.ensureCursorVisible()

    def _on_select_setup(self) -> None:
        start_dir = str(Path.home() / "Descargas")
        if not Path(start_dir).exists():
            start_dir = str(Path.home())
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar instalador setup.exe",
            start_dir,
            "Ejecutables de Windows (*.exe *.msi *.bat);;Todos los archivos (*)",
        )
        if file_path:
            self.setup_input.setText(file_path)
            exe_parent_name = Path(file_path).resolve().parent.name
            if exe_parent_name and exe_parent_name not in ("Descargas", "Downloads", "tests"):
                suggested_dest = Path.home() / "Games" / exe_parent_name
                self.dest_input.setText(str(suggested_dest))
            self.append_log(f"[UI] Instalador seleccionado: {file_path}")

    def _on_select_dest(self) -> None:
        current = self.dest_input.text().strip()
        start_dir = current if current and Path(current).parent.exists() else str(Path.home())
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Elegir carpeta donde se instalará el juego",
            start_dir,
        )
        if folder_path:
            self.dest_input.setText(folder_path)
            self.append_log(f"[UI] Carpeta de instalación seleccionada: {folder_path}")

    def _on_clear_console(self) -> None:
        self.console.clear()

    def _on_copy_logs(self) -> None:
        QApplication.clipboard().setText(self.console.toPlainText())
        self.lbl_status.setText("Estado: Logs copiados al portapapeles.")

    def _on_start_install(self) -> None:
        setup_path = self.setup_input.text().strip()
        dest_path = self.dest_input.text().strip()
        raw_args = self.args_input.text().strip()

        if not setup_path:
            QMessageBox.warning(
                self,
                "Falta setup.exe",
                "Por favor selecciona primero el archivo ejecutable del instalador (setup.exe).",
            )
            return

        if not Path(setup_path).expanduser().is_file():
            QMessageBox.critical(
                self,
                "Archivo no encontrado",
                f"El archivo seleccionado no existe:\n{setup_path}",
            )
            return

        if not dest_path:
            QMessageBox.warning(
                self,
                "Falta carpeta de destino",
                "Por favor selecciona o escribe la carpeta donde se instalará el juego.",
            )
            return

        extra_args = shlex.split(raw_args) if raw_args else []

        self.btn_install.setEnabled(False)
        self.btn_select_setup.setEnabled(False)
        self.btn_select_dest.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setValue(2)

        self.worker = InstallerWorker(
            setup_exe=setup_path,
            install_dir=dest_path,
            extra_args=extra_args,
            parent=self,
        )
        self.worker.log_signal.connect(self.append_log)
        self.worker.status_signal.connect(self._on_worker_status)
        self.worker.finished_success.connect(self._on_worker_success)
        self.worker.finished_error.connect(self._on_worker_error)
        self.worker.start()

    def _on_cancel_install(self) -> None:
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.btn_cancel.setEnabled(False)

    def _on_worker_status(self, text: str, progress: int) -> None:
        self.lbl_status.setText(f"Estado: {text}")
        self.progress_bar.setValue(progress)

    def _restore_controls(self) -> None:
        self.btn_install.setEnabled(True)
        self.btn_select_setup.setEnabled(True)
        self.btn_select_dest.setEnabled(True)
        self.btn_cancel.setEnabled(False)

    def _on_worker_success(self, prefix_path: str) -> None:
        self._restore_controls()
        self.progress_bar.setValue(100)
        self.lbl_status.setText("Estado: ¡Instalación completada sin errores!")
        QMessageBox.information(
            self,
            "Instalación Finalizada — RepackForge",
            f"El proceso de preparación e instalación concluyó con éxito.\n\n"
            f"Carpeta del juego:\n{self.dest_input.text().strip()}\n\n"
            f"WINEPREFIX exclusivo:\n{prefix_path}",
        )

    def _on_worker_error(self, error_msg: str) -> None:
        self._restore_controls()
        self.lbl_status.setText(f"Estado: Error — {error_msg}")
        self.append_log(f"[ERROR] {error_msg}")
        QMessageBox.critical(
            self,
            "Error durante la instalación — RepackForge",
            f"Se produjo un error durante el proceso:\n\n{error_msg}\n\n"
            "Revisa la consola de texto en vivo para más detalles.",
        )


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("repackforge")
    app.setApplicationDisplayName("RepackForge")
    app.setDesktopFileName("repackforge")
    app.setWindowIcon(load_app_icon())
    window = RepackInstallerWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
