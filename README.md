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
- arquivo `.env` (lido no startup): `SERENA_FZF_SEARCH_PATH`, `SERENA_FZF_EDITOR`, `SERENA_FZF_SERENA_CMD`, `SERENA_FZF_EXCLUDE`, `SERENA_FZF_MAXDEPTH`

Exemplo `serena_fzf_config.json`:

```json
{
  "search_path": "./src",
  "maxdepth": 3,
  "exclude": ["node_modules", ".git", "dist"]
}
```

Exemplo `.env`:

```dotenv
SERENA_FZF_SEARCH_PATH=./src
SERENA_FZF_EDITOR=code
SERENA_FZF_SERENA_CMD=serena
SERENA_FZF_EXCLUDE=node_modules, .git, dist
SERENA_FZF_MAXDEPTH=3
```

### Usando flags no comando

Você pode sobrescrever o `maxdepth` globalmente via comando individual:

```bash
>> :f --maxdepth=2 arquivo.txt    # busca só 2 níveis fundo
>> :g --maxdepth=1 padrão         # grep limitado a 1 nível
>> :s --maxdepth=3 MinhaClasse    # símbolo até 3 níveis
```

**Hierarquia de configuração:**
1. `--maxdepth=N` no comando → prevalece (mais flexível)
2. `SERENA_FZF_MAXDEPTH` no `.env` → caso não tenha flag
3. `"maxdepth"` no config JSON → caso não tenha env
4. Sem limite → glob é mais rápido para pastas pequenas

## Dependências

- **ripgrep** (`rg`) - Para buscas extremamente rápidas (instale com `sudo apt install ripgrep` ou `brew install ripgrep`)
- **fzf** - Para seleção fuzzy (geralmente já vem com algumas distribuições)
- **Python 3.8+**

Se `ripgrep` não estiver disponível, o script usa fallbacks em Python (mais lentos).

## Performance

O script usa **ripgrep** (`rg`) quando disponível para buscas extremamente rápidas:

- **Com ripgrep**: ~0.01s para milhares de arquivos
- **Sem ripgrep**: Pode levar segundos/minutos dependendo do tamanho do projeto

Para projetos grandes, instale ripgrep e configure `SERENA_FZF_MAXDEPTH=3` no `.env` para limitar profundidade.

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
