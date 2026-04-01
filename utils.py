import subprocess
import os
import glob

# -------------------------
# Utils
# -------------------------
def extract_results(result):
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

def fallback_find_file(query):
    return glob.glob(f"**/*{query}*", recursive=True)

def fallback_search_content(pattern):
    results = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines, start=1):
                        if pattern in line:
                            results.append(f"{path}:{i}: {line.strip()}")
            except:
                pass
    return results

def run_fzf(options):
    if not options:
        return None

    proc = subprocess.Popen(
        ["fzf"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )

    out, _ = proc.communicate("\n".join(options))
    return out.strip() if out else None

def open_in_editor(selection):
    if not selection:
        return

    parts = selection.split(":", 2)
    if len(parts) >= 2 and parts[1].isdigit():
        file_line = f"{parts[0]}:{parts[1]}"
        if len(parts) > 2 and parts[2].isdigit():
            file_line += f":{parts[2]}"
        os.system(f'{EDITOR} --goto "{file_line}"')
    else:
        os.system(f'{EDITOR} "{selection}"')