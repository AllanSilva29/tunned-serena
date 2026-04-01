# Serena + fzf CLI

Uma interface de linha de comando que integra o Serena (MCP server) com fzf para navegação rápida em código, permitindo buscar símbolos, referências, arquivos e padrões de forma interativa.

## Como Funciona

O script principal (`serena_fzf.py`) inicia um cliente MCP que se conecta ao servidor Serena. Ele oferece comandos para:

- **:s símbolo**: Buscar definições de símbolos (ex.: classes, funções).
- **:r símbolo**: Encontrar referências ao símbolo.
- **:f arquivo**: Localizar arquivos por nome.
- **:g padrão**: Buscar padrões no conteúdo dos arquivos (grep semântico).

Para buscas sem comando explícito, o script escolhe automaticamente a ferramenta baseada no input (ex.: maiúscula para símbolo, senão padrão).

O resultado é passado para `fzf`, um seletor fuzzy, onde você escolhe a opção desejada. Ao selecionar, o arquivo é aberto no editor (VS Code por padrão) na linha exata.

Se o Serena não encontrar resultados, há fallbacks locais para buscas robustas.

## Estrutura dos Arquivos

O projeto é modularizado para facilitar manutenção:

- **`serena_fzf.py`**: Script principal. Gerencia o loop interativo, inicializa o cliente MCP e coordena as buscas.
- **`serena_client.py`**: Contém `get_serena_command()` (resolve como executar o Serena) e a classe `MCPClient` (comunicação JSON-RPC com o servidor MCP).
- **`utils.py`**: Funções utilitárias:
  - `extract_results()`: Extrai caminhos de arquivos/linhas dos resultados do MCP.
  - `fallback_find_file()`: Busca arquivos por nome usando glob.
  - `fallback_search_content()`: Busca padrões no conteúdo dos arquivos localmente.
  - `run_fzf()`: Executa fzf com as opções.
  - `open_in_editor()`: Abre o arquivo no editor, posicionando o cursor se houver linha.
- **`commands.py`**: Parsing de comandos e escolha automática de ferramentas MCP.

## Configuração de caminho de busca

O script usa o caminho padrão `.` mas você pode configurar:

- variável de ambiente: `SERENA_FZF_SEARCH_PATH`
- arquivo JSON: `serena_fzf_config.json` com chave `search_path`
- arquivo `.env` (lido no startup): `SERENA_FZF_SEARCH_PATH`, `SERENA_FZF_EDITOR`, `SERENA_FZF_SERENA_CMD`

Exemplo `serena_fzf_config.json`:

```json
{
  "search_path": "./src"
}
```

Exemplo `.env`:

```dotenv
SERENA_FZF_SEARCH_PATH=./src
SERENA_FZF_EDITOR=code
SERENA_FZF_SERENA_CMD=serena
SERENA_FZF_EXCLUDE=node_modules, .git, dist
```

# Setup

## 1. Instalar uv

https://github.com/astral-sh/uv

## 2. Instalar Serena CLI

```bash
uv tool install git+https://github.com/oraios/serena
```

## 3. Iniciar MCP Server (obrigatório)

```bash
serena start-mcp-server
```

Se você não quiser instalar, o script tenta usar `uvx` automaticamente para rodar o MCP.

## 4. Rodar CLI

```bash
python serena_fzf.py
```

## Alternativa (sem instalar)

O script também suporta execução via uvx automaticamente.
