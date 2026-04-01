def extract_results(result):
    """Extrai caminhos/linhas dos resultados do servidor MCP"""
    items = []

    try:
        content = result.get("result", {}).get("content", [])

        for c in content:
            text = c.get("text", "")
            for line in text.split("\n"):
                if "/" in line or "." in line:
                    items.append(line.strip())

    except:
        pass

    return list(set(items))
