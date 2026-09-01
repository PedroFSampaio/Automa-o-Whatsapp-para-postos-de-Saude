# Como Criar o Executável (.exe)

## Pré-requisitos

1. **Python 3.8+** instalado e no PATH
2. **PyInstaller** instalado

## Instalação do PyInstaller

Abra o Prompt de Comando (cmd) ou PowerShell e execute:

```bash
pip install pyinstaller
pip install -r requirements.txt
```

Se tiver problemas com proxy, tente:

```bash
pip install --trusted-host pypi.python.org --trusted-host files.pythonhosted.org pyinstaller
```

## Gerando o Executável

### Opção 1: Usando o Script Batch (Windows)

1. Abra o arquivo `build.bat`
2. O script automaticamente compilará o executável
3. Você encontrará o `.exe` na pasta `dist\`

### Opção 2: Usando Python Diretamente

Abra o Prompt de Comando na pasta do projeto e execute:

```bash
python build_exe.py
```

### Opção 3: Usando PyInstaller Diretamente

```bash
pyinstaller WhatsAppSender.spec
```

## Resultado

Após compilar com sucesso:

- ✅ Um executável será criado em `dist/WhatsApp Message Sender.exe`
- ✅ Você pode executar o programa sem precisar de Python instalado
- ✅ Pode criar um atalho na área de trabalho

## Usando o Executável

1. Localize `WhatsApp Message Sender.exe` na pasta `dist/`
2. Execute-o clicando duas vezes
3. A aplicação funcionará normalmente

## Tamanho do Arquivo

O executável gerado terá aproximadamente **500-700 MB** (inclui Python e todas as dependências).

## Possíveis Problemas

### "PyInstaller não encontrado"
Certifique-se de ter instalado com `pip install pyinstaller`

### "Arquivo .exe não é gerado"
Verifique se há erros na janela de console durante a compilação

### Antivírus detecta como malware
É falso positivo comum com executáveis criados por PyInstaller. Você pode:
1. Criar uma exceção no seu antivírus
2. Usar o programa via Python (sem gerar .exe)

## Próximas Versões

Para gerar novamente após fazer alterações no código:
1. Apague as pastas `build/` e `dist/`
2. Execute novamente o script de compilação

---

**Dúvidas?** Verifique se todas as dependências estão instaladas:
```bash
pip install -r requirements.txt
pip install pyinstaller
```
