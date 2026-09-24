"""Script de compilação do Gerador Pix para Executável Windows (.exe) e Instalador Inno Setup."""

import os
import shutil
import subprocess
import sys


def find_iscc() -> str | None:
    """Localiza o executável do compilador Inno Setup (ISCC.exe)."""
    candidates = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        shutil.which("iscc"),
    ]
    for path in candidates:
        if path and os.path.exists(path):
            return path
    return None


def build_installer(base_dir: str):
    """Compila o instalador oficial Windows via Inno Setup."""
    iscc_path = find_iscc()
    iss_file = os.path.join(base_dir, "installer.iss")

    if not iscc_path:
        print("\n[AVISO] Inno Setup (ISCC.exe) não encontrado no sistema.")
        print("Para gerar o instalador, instale o Inno Setup 6 em https://jrsoftware.org/isdl.php")
        return False

    if not os.path.exists(iss_file):
        print(f"\n[ERRO] Script de instalação não encontrado: {iss_file}")
        return False

    print("\n==================================================")
    print("Iniciando compilação do Instalador (Inno Setup)...")
    print("==================================================")

    cmd = [iscc_path, iss_file]
    result = subprocess.run(cmd, cwd=base_dir)

    if result.returncode == 0:
        installer_path = os.path.join(base_dir, "dist", "GeradorPix_Setup_v1.1.0.exe")
        print("\n==================================================")
        print("INSTALADOR GERADO COM SUCESSO!")
        print(f"Instalador disponível em: {installer_path}")
        print("==================================================")
        return True
    else:
        print(f"\n[ERRO] Falha na compilação do instalador. Código: {result.returncode}")
        return False


def build():
    print("==================================================")
    print("Iniciando compilação do Gerador Pix (.exe)...")
    print("==================================================")

    # Fecha instâncias abertas para evitar PermissionError de arquivo travado
    if sys.platform == "win32":
        try:
            subprocess.run(["taskkill", "/F", "/IM", "GeradorPix.exe"], capture_output=True)
        except Exception:
            pass

    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, "src", "assets", "icon.ico")
    assets_dir = os.path.join(base_dir, "src", "assets")
    config_file = os.path.join(base_dir, "config.json")

    # Comando PyInstaller
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=GeradorPix",
        "--noconsole",
        "--onefile",
        "--clean",
        f"--icon={icon_path}",
        f"--add-data={assets_dir};src/assets",
        f"--add-data={config_file};.",
        "--collect-all=customtkinter",
        os.path.join(base_dir, "main.py"),
    ]

    print("Executando comando:")
    print(" ".join(cmd))
    print()

    result = subprocess.run(cmd, cwd=base_dir)

    if result.returncode == 0:
        exe_path = os.path.join(base_dir, "dist", "GeradorPix.exe")
        print("\n==================================================")
        print("COMPILAÇÃO DO EXECUTÁVEL CONCLUÍDA COM SUCESSO!")
        print(f"Executável gerado em: {exe_path}")
        print("==================================================")

        # Garante cópia atualizada do config.json ao lado do executável
        dist_config = os.path.join(base_dir, "dist", "config.json")
        shutil.copy2(config_file, dist_config)
        print(f"Arquivo de configurações sincronizado em: {dist_config}")

        # Compilar instalador se solicitado ou disponível
        build_installer(base_dir)
    else:
        print(f"\nErro na compilação. Código de retorno: {result.returncode}")
        sys.exit(result.returncode)


if __name__ == "__main__":
    build()
