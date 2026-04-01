# Estrutura da pasta `utils/`

Módulos especializados para melhor manutenção:

## `config.py`
- `load_dotenv()` - Carrega variáveis de ambiente do `.env`
- `load_json_config()` - Carrega config do `serena_fzf_config.json`
- `get_search_root()` - Define caminho base de busca
- `get_excludes()` - Obtém padrões de exclusão
- `get_max_depth()` - Obtém limite de profundidade
- `get_editor()` - Obtém editor configurado

## `filters.py`
- `should_exclude()` - Verifica se caminho deve ser excluído
- `filter_excluded_dirs()` - Filtra dirs durante traversal

## `search.py`
- `fallback_find_file()` - Busca arquivos por nome (com maxdepth)
- `fallback_search_content()` - Busca padrões em conteúdo (com maxdepth)

## `editor.py`
- `open_in_editor()` - Abre arquivo no editor + posiciona linha

## `fzf.py`
- `run_fzf()` - Executa fzf como seletor fuzzy

## `mcp.py`
- `extract_results()` - Extrai resultados do servidor MCP

## `__init__.py`
Exporta todas as funções públicas para imports convenientes em `serena_fzf.py`.
