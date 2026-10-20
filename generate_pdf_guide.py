#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de la Guía en PDF de RepackForge (GUIA_DE_USO_REPACKFORGE.pdf)
con diseño limpio, alto contraste en bloques de comandos e icono integrado.
"""

from pathlib import Path
from PyQt6.QtCore import QMarginsF, QSizeF
from PyQt6.QtGui import QGuiApplication, QPageLayout, QPageSize, QTextDocument
from PyQt6.QtPrintSupport import QPrinter


PROJECT_DIR = Path(__file__).resolve().parent
ICON_PATH = PROJECT_DIR / "assets" / "repackforge.png"


HTML_GUIDE = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<style>
  body {{
    font-family: 'DejaVu Sans', 'Noto Sans', sans-serif;
    color: #1e293b;
    line-height: 1.5;
    font-size: 11pt;
  }}
  h1 {{
    color: #0f172a;
    font-size: 20pt;
    margin-bottom: 2px;
  }}
  .subtitle {{
    color: #2563eb;
    font-size: 12pt;
    font-weight: bold;
    margin-top: 0px;
    margin-bottom: 8px;
  }}
  .badges {{
    color: #15803d;
    font-size: 9.5pt;
    font-weight: bold;
    margin-bottom: 14px;
  }}
  hr {{
    border: none;
    border-top: 2px solid #2563eb;
    margin: 10px 0 16px 0;
  }}
  h2 {{
    color: #1d4ed8;
    font-size: 14pt;
    margin-top: 16px;
    margin-bottom: 6px;
    border-bottom: 1px solid #cbd5e1;
    padding-bottom: 3px;
  }}
  h3 {{
    color: #0f172a;
    font-size: 11.5pt;
    margin-top: 10px;
    margin-bottom: 4px;
  }}
  .codebox {{
    background-color: #f1f5f9;
    border: 1px solid #94a3b8;
    border-left: 5px solid #2563eb;
    padding: 8px 12px;
    margin: 6px 0 10px 0;
    font-family: 'DejaVu Sans Mono', monospace;
    font-size: 10pt;
    color: #0f172a;
  }}
  .notebox {{
    background-color: #ecfdf5;
    border-left: 5px solid #16a34a;
    padding: 8px 12px;
    margin: 8px 0;
    color: #065f46;
    font-size: 10.5pt;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 8px;
    margin-bottom: 12px;
  }}
  th {{
    background-color: #dbeafe;
    color: #1e3a8a;
    text-align: left;
    padding: 7px 10px;
    font-size: 10pt;
    border: 1px solid #bfdbfe;
  }}
  td {{
    padding: 7px 10px;
    font-size: 10pt;
    border: 1px solid #e2e8f0;
    vertical-align: top;
  }}
  .footer {{
    margin-top: 18px;
    text-align: center;
    color: #64748b;
    font-size: 9pt;
  }}
</style>
</head>
<body>

  <table style="border: none; margin-bottom: 0;">
    <tr>
      <td style="border: none; width: 76px; padding: 0;">
        <img src="{ICON_PATH}" width="64" height="64">
      </td>
      <td style="border: none; padding: 0 0 0 10px; vertical-align: middle;">
        <h1>REPACKFORGE — Guía de Instalación y Uso</h1>
        <div class="subtitle">Instalador Gaming para Linux Anti-Errores (ISDone.dll • unarc.dll • isskin.dll)</div>
        <div class="badges">Compatible con Debian • Ubuntu • Mint • Arch • CachyOS • Manjaro • Fedora • Nobara • openSUSE</div>
      </td>
    </tr>
  </table>
  <hr>

  <h2>1. Cómo Instalarlo en tu Nuevo Linux (Opción A: Desde el Pendrive OMEGAX)</h2>
  <p>En tu pendrive <b>OMEGAX</b> ya tienes la carpeta lista <b><code>REPACKFORGE_LINUX</code></b> (y también el archivo <code>RepackForge-Portable-Linux.zip</code>).</p>
  <ol>
    <li>Conecta el pendrive en tu nuevo sistema Linux y entra en la carpeta <b><code>REPACKFORGE_LINUX</code></b>.</li>
    <li>Haz clic derecho dentro de la carpeta, selecciona <b>"Abrir en una terminal"</b> y ejecuta:</li>
  </ol>
  <div class="codebox">
    chmod +x instalar_en_cualquier_linux.sh iniciar_instalador.sh<br>
    ./instalar_en_cualquier_linux.sh
  </div>

  <h2>2. Cómo Instalarlo en tu Nuevo Linux (Opción B: Desde tu GitHub)</h2>
  <p>Si no tienes el pendrive a mano, puedes descargarlo directamente desde tu repositorio oficial de GitHub desde cualquier terminal:</p>
  <div class="codebox">
    git clone https://github.com/OMEGA12492903/repackforge-linux.git<br>
    cd repackforge-linux<br>
    chmod +x instalar_en_cualquier_linux.sh iniciar_instalador.sh<br>
    ./instalar_en_cualquier_linux.sh
  </div>

  <div class="notebox">
    <b>¿Qué hace el instalador automático?</b><br>
    • Detecta tu distribución de Linux (<code>apt</code>, <code>pacman</code>, <code>dnf</code> o <code>zypper</code>) e instala <code>wine</code>, <code>winetricks</code>, <code>cabextract</code>, <code>unzip</code>, <code>p7zip</code> y <code>PyQt6</code>.<br>
    • Descarga o enlaza automáticamente la última versión de <b>GE-Proton</b>.<br>
    • Crea el icono <b>RepackForge</b> en tu <b>Escritorio</b> y en el menú de aplicaciones del sistema.
  </div>

  <h2>3. Cómo Instalar Cualquier Juego o Repack (FitGirl / ElAmigos / DODI)</h2>
  <ol>
    <li>Abre <b>RepackForge</b> desde el icono de tu Escritorio, tu menú de aplicaciones o ejecutando <code>./iniciar_instalador.sh</code>.</li>
    <li>Pulsa <b>"Seleccionar setup.exe"</b> y elige el instalador del juego.</li>
    <li>Pulsa <b>"Elegir Carpeta Destino"</b> y selecciona dónde quieres instalar el juego (ej. <code>~/Games/NombreDelJuego</code>).</li>
    <li>Pulsa el botón verde <b>"⚡ PREPARAR E INSTALAR"</b>.</li>
    <li>Cuando aparezca la ventana del instalador del juego y te pregunte la ruta de instalación en Windows, selecciona la unidad <b><code>G:\\</code></b> (que RepackForge conecta automáticamente a tu carpeta destino para evitar errores de rutas largas).</li>
  </ol>

  <h2>4. Protección Interna que Aplica RepackForge Automáticamente</h2>
  <table>
    <tr>
      <th style="width: 32%;">Componente / Variable</th>
      <th>Función Anti-Crash</th>
    </tr>
    <tr>
      <td><b>WINEPREFIX limpio exclusivo</b></td>
      <td>Crea un prefijo nuevo y aislado en <code>&lt;carpeta_juego&gt;/.wineprefix</code> y mapea la unidad <code>G:\\</code>.</td>
    </tr>
    <tr>
      <td><b>winecfg /v win10</b></td>
      <td>Configura el entorno del prefijo en Windows 10 automáticamente antes de abrir el instalador.</td>
    </tr>
    <tr>
      <td><b>vcrun6 + vcrun6sp6 + vcrun2022</b></td>
      <td>Instala <code>MFC42.DLL</code> y <code>msvcp60.dll</code> (evita el error de <code>isskin.dll</code>) más el runtime C++ 2022 (32 y 64 bits).</td>
    </tr>
    <tr>
      <td><b>WINE_LARGE_ADDRESS_AWARE=1</b></td>
      <td>Permite a descompresores de 32 bits usar hasta 4 GB de RAM sin colapsar por memoria.</td>
    </tr>
    <tr>
      <td><b>PROTON_NO_ESYNC=1<br>PROTON_NO_FSYNC=1</b></td>
      <td>Desactiva esync/fsync durante la descompresión masiva para que <code>ISDone.dll</code> y <code>unarc.dll</code> no se bloqueen.</td>
    </tr>
    <tr>
      <td><b>WINEDLLOVERRIDES</b></td>
      <td><code>winemenubuilder.exe=d;mfc42,mfc42u,msvcp60,msvcirt=n,b</code></td>
    </tr>
  </table>

  <div class="footer">
    RepackForge • Repositorio GitHub: https://github.com/OMEGA12492903/repackforge-linux • 2026
  </div>

</body>
</html>
"""


def build_pdf(output_paths: list[Path]) -> None:
    app = QGuiApplication.instance() or QGuiApplication(["pdf_gen", "-platform", "offscreen"])

    doc = QTextDocument()
    doc.setHtml(HTML_GUIDE)

    for out_path in output_paths:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(str(out_path))
        page_layout = QPageLayout(
            QPageSize(QPageSize.PageSizeId.A4),
            QPageLayout.Orientation.Portrait,
            QMarginsF(14, 14, 14, 14),
            QPageLayout.Unit.Millimeter,
        )
        printer.setPageLayout(page_layout)
        doc.setPageSize(QSizeF(printer.pageRect(QPrinter.Unit.Point).size()))
        doc.print(printer)
        print(f"PDF generado en: {out_path} ({out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    targets = [
        PROJECT_DIR / "GUIA_DE_USO_REPACKFORGE.pdf",
        Path.home() / "Escritorio" / "GUIA_DE_USO_REPACKFORGE.pdf",
    ]
    usb_mount = Path("/media/omegax/OMEGAX")
    if usb_mount.exists():
        targets.append(usb_mount / "GUIA_DE_USO_REPACKFORGE.pdf")
    build_pdf(targets)
