#!/usr/bin/env python3
from serena_client import get_serena_command, MCPClient
from utils import (
    get_search_root, extract_results, fallback_find_file, 
    fallback_search_content, run_fzf, open_in_editor, load_dotenv
)
from commands import parse_command, choose_tool

# Carregar .env
load_dotenv()


# -------------------------
# MAIN
# -------------------------
def main():
    print("🚀 Serena + fzf CLI\n")

    search_root = get_search_root()
    client = MCPClient(get_serena_command())

    # MCP init
    client.call("initialize", {
        "clientInfo": {"name": "serena-cli", "version": "1.0"}
    })
    client.notify("initialized")

    # ativa projeto
    client.call("tools/call", {
        "name": "activate_project",
        "arguments": {"project": "."}
    })

    # help inicial
    print("🧰 Comandos disponíveis:\n")
    print(":s  símbolo")
    print(":r  referências")
    print(":f  encontrar arquivo")
    print(":g  buscar padrão")
    print(":h  ajuda\n")

    while True:
        query = input(">> ")

        if query in ("exit", "quit"):
            break

        if query == ":h":
            print("\n:s UserService")
            print(":r UserService")
            print(":f arquivo.txt")
            print(":g padrão\n")
            continue

        tool, args = parse_command(query)

        if not tool:
            tool, args = choose_tool(query)

        # Extrair maxdepth se fornecido no comando
        maxdepth = args.pop("_maxdepth", None)

        if tool == "find_file":
            options = fallback_find_file(args["pattern"], maxdepth=maxdepth)
        else:
            result = client.call("tools/call", {
                "name": tool,
                "arguments": {k: v for k, v in args.items() if not k.startswith("_")}
            })
            options = extract_results(result)

        # fallback para busca de símbolo
        if not options and tool == "find_symbol":
            print("⚠ fallback: search_for_pattern\n")

            result = client.call("tools/call", {
                "name": "search_for_pattern",
                "arguments": {
                    "pattern": args.get("name_path", ""),
                    "relative_path": "."
                }
            })

            options = extract_results(result)

        # fallback filesystem
        if not options and tool == "search_for_pattern":
            print("🔍 Busca local em andamento...\n")
            search_term = args.get("pattern", query).replace("*", "")
            options = fallback_search_content(search_term, maxdepth=maxdepth)

        if not options:
            print("⚠ Nenhum resultado\n")
            continue

        selection = run_fzf(options)

        if selection:
            open_in_editor(selection)


if __name__ == "__main__":
    main()