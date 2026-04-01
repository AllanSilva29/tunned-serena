# -------------------------
# Command parsing
# -------------------------
def parse_command(query):
    if query.startswith(":s "):
        return "find_symbol", {
            "name_path": query[3:],
            "relative_path": ".",
            "include_body": False,
            "depth": 1
        }

    if query.startswith(":r "):
        return "find_referencing_symbols", {
            "name_path": query[3:],
            "relative_path": "."
        }

    if query.startswith(":f "):
        return "find_file", {
            "pattern": query[3:]
        }

    if query.startswith(":g "):
        return "search_for_pattern", {
            "pattern": query[3:],
            "relative_path": "."
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