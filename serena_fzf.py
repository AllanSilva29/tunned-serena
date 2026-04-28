#!/usr/bin/env python3
from serena_client import get_serena_command, MCPClient
from utils import (
    get_search_root, extract_results, fallback_find_file,
    fallback_find_size_files, fallback_find_modified_files,
    fallback_search_content, run_fzf, open_in_editor, load_dotenv
)
import os
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
    print(":fm buscar por data de modificação")
    print(":fs buscar por tamanho")
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
            print(":fm --after=2026-04-01 --before=2026-04-07")
            print(":fs --min=10K --max=1M arquivo")
            print(":g padrão\n")
            continue

        tool, args = parse_command(query)

        if not tool:
            tool, args = choose_tool(query)

        # Extrair maxdepth se fornecido no comando
        maxdepth = args.pop("_maxdepth", None)
        rpc_timeout = int(os.environ.get("SERENA_FZF_RPC_TIMEOUT", "5"))

        if tool == "find_file":
            options = fallback_find_file(args["pattern"], maxdepth=maxdepth)
        elif tool == "find_modified_file":
            options = fallback_find_modified_files(
                args.get("pattern", ""),
                before=args.get("before"),
                after=args.get("after"),
                order=args.get("order"),
                maxdepth=maxdepth
            )
        elif tool == "find_size_file":
            options = fallback_find_size_files(
                args.get("pattern", ""),
                min_size=args.get("min_size"),
                max_size=args.get("max_size"),
                order=args.get("order"),
                maxdepth=maxdepth
            )
        else:
            try:
                result = client.call("tools/call", {
                    "name": tool,
                    "arguments": {k: v for k, v in args.items() if not k.startswith("_")}
                }, timeout=rpc_timeout)
                options = extract_results(result)
            except TimeoutError:
                if tool == "search_for_pattern":
                    print("⚠ Serena demorou demais, fallback local...\n")
                    search_term = args.get("pattern", query).replace("*", "")
                    options = fallback_search_content(search_term, maxdepth=maxdepth)
                else:
                    print(f"❌ Serena timeout no tool {tool}")
                    continue

        # fallback para busca de símbolo
        if not options and tool == "find_symbol":
            print("⚠ fallback: busca local...\n")
            options = fallback_search_content(args.get("name_path", ""), maxdepth=maxdepth)

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