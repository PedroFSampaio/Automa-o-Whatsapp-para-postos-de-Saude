# WhatsApp Message Sender

Aplicativo Windows para organizar o envio individual de mensagens pelo WhatsApp Web.

## Etapa atual: 3

A Etapa 1 entrega a interface principal:

- editor de mensagem geral com a variavel `[nome]`;
- selecao de arquivos CSV e XLSX;
- resumo de contatos, enviados, pendentes e erros;
- controles Iniciar, Pausar, Continuar e Parar;
- indicacao de status da operacao.
- importacao de CSV e XLSX com colunas `nome` e `telefone`;
- importacao de agendas PDF com nomes e telefones;
- suporte a varios telefones para o mesmo paciente;
- normalizacao automatica dos telefones;
- visualizacao dos contatos importados.
- envio individual pelo WhatsApp Web com personalizacao por `[nome]`;
- pausa e parada do envio em segundo plano;
- atualizacao dos status Enviado e Erro na tabela.

O banco SQLite ainda sera implementado em uma etapa seguinte.

## Executar no Windows

1. Instale Python 3.11 ou superior, marcando `Add Python to PATH`.
2. Abra o PowerShell nesta pasta.
3. Execute:

```powershell
python -m app.main
```

Para importar PDF ou XLSX, instale as dependencias:

```powershell
pip install -r requirements.txt
```

Para enviar pelo WhatsApp Web, o aplicativo baixa automaticamente a versao adequada
do Microsoft Edge WebDriver na primeira utilizacao. Essa primeira execucao requer
acesso a internet. Como alternativa, voce pode colocar `msedgedriver.exe` em:

```text
Downloads\edgedriver_win64\msedgedriver.exe
Downloads\edgedriver_win64\edgedriver\msedgedriver.exe
```

O aplicativo usa `webdriver.Edge`, abre `https://web.whatsapp.com` e cria o perfil
persistente `C:\Users\SEU_USUARIO\whatsapp_edge_profile`. Na primeira execucao,
escaneie o QR Code manualmente; nas seguintes, a sessao sera reutilizada enquanto
continuar valida.

Na primeira execucao, escaneie o QR Code no navegador aberto pelo aplicativo.

### Usar uma guia do Edge que ja esta aberta

O Selenium nao consegue controlar uma janela comum do Edge que foi aberta sem
depuracao remota. Para reutilizar a guia que ja esta com o QR Code, feche todas
as janelas do Edge e inicie uma nova instancia pelo PowerShell:

```powershell
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" `
	--remote-debugging-port=9222 `
	--user-data-dir="$env:USERPROFILE\whatsapp_edge_profile"
```

Depois abra `https://web.whatsapp.com` nessa instancia, deixe o QR Code visivel
e execute o aplicativo em outro PowerShell:

```powershell
$env:EDGE_DEBUGGER_ADDRESS="127.0.0.1:9222"
python -m app.main
```

Nesse modo, o aplicativo se conecta ao Edge existente e nao cria outra guia
para o navegador. O QR Code continua sendo escaneado manualmente.
