# -------------------------
# Command parsing
# -------------------------
def parse_flags(args_str):
    """Extrai flags (--key=value) e retorna (flags_dict, query)"""
    flags = {}
    parts = []
    
    for part in args_str.split():
        if part.startswith("--"):
            # Flag format: --maxdepth=2 ou --exclude=*.log
            if "=" in part:
                key, value = part[2:].split("=", 1)
                if key == "maxdepth":
                    try:
                        flags["maxdepth"] = int(value)
                    except ValueError:
                        pass
                elif key == "exclude":
                    flags["exclude"] = value.split(",")
            else:
                # Flag sem valor (para futuros use-cases)
                flags[part[2:]] = True
        else:
            parts.append(part)
    
    return flags, " ".join(parts)


def parse_command(query):
    if query.startswith(":s "):
        flags, args = parse_flags(query[3:])
        return "find_symbol", {
            "name_path": args,
            "relative_path": ".",
            "include_body": False,
            "depth": 1,
            "_maxdepth": flags.get("maxdepth")
        }

    if query.startswith(":r "):
        flags, args = parse_flags(query[3:])
        return "find_referencing_symbols", {
            "name_path": args,
            "relative_path": ".",
            "_maxdepth": flags.get("maxdepth")
        }

    if query.startswith(":f "):
        flags, args = parse_flags(query[3:])
        return "find_file", {
            "pattern": args,
            "_maxdepth": flags.get("maxdepth")
        }

    if query.startswith(":g "):
        flags, args = parse_flags(query[3:])
        return "search_for_pattern", {
            "pattern": args,
            "relative_path": ".",
            "_maxdepth": flags.get("maxdepth")
        }

    return None, None

def choose_tool(query):
    q = query.lower()

    if "quem usa" in q or "who uses" in q:
        return "find_referencing_symbols", {
            "name_path": query,
            "relative_path": "."
        }

    if query and query[0].isupper():
        return "find_symbol", {
            "name_path": query,
            "relative_path": ".",
            "include_body": False,
            "depth": 1
        }

    return "search_for_pattern", {
        "pattern": query,
        "relative_path": "."
    }