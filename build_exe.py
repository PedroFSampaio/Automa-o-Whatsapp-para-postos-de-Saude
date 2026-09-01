#!/usr/bin/env python
"""
Script para compilar o WhatsApp Message Sender em um executável.
Use: python build_exe.py
"""

import subprocess
import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("WhatsApp Message Sender - Compilador de Executável")
    print("=" * 60)
    print()
    
    # Verify PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller não está instalado!")
        print("\nInstale com:")
        print("  pip install pyinstaller")
        sys.exit(1)
    
    print("✓ PyInstaller encontrado")
    print()
    
    # Get project path
    project_path = Path(__file__).parent
    main_file = project_path / "app" / "main.py"
    spec_file = project_path / "WhatsAppSender.spec"
    
    if not main_file.exists():
        print(f"❌ Arquivo principal não encontrado: {main_file}")
        sys.exit(1)
    if not spec_file.exists():
        print(f"❌ Arquivo de compilação não encontrado: {spec_file}")
        sys.exit(1)
    
    print(f"✓ Arquivo principal: {main_file}")
    print()
    print("Compilando executável...")
    print()
    
    # Use the canonical spec so Selenium and webdriver-manager submodules are bundled.
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        str(spec_file),
        "--noconfirm",
    ]
    
    try:
        result = subprocess.run(cmd, cwd=project_path)
        
        if result.returncode == 0:
            print()
            print("=" * 60)
            print("✅ Executável criado com sucesso!")
            print("=" * 60)
            print()
            print(f"Localização: {project_path / 'dist' / 'WhatsApp Message Sender.exe'}")
            print()
            print("Próximos passos:")
            print("1. O arquivo .exe está na pasta 'dist'")
            print("2. Copie a pasta inteira 'dist' para onde você quer usar")
            print("3. Você pode criar um atalho para WhatsApp Message Sender.exe")
            print()
        else:
            print()
            print("❌ Erro na compilação")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
