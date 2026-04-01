import subprocess
import os
import glob
import json

# -------------------------
# Utils
# -------------------------

def load_dotenv(path=".env"):
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


load_dotenv()

def get_search_root():
    path = os.environ.get("SERENA_FZF_SEARCH_PATH")

    if not path and os.path.exists("serena_fzf_config.json"):
        try:
            with open("serena_fzf_config.json", "r", encoding="utf-8") as f:
                cfg = json.load(f)
                path = cfg.get("search_path")
        except Exception:
            path = None

    return path or "."


def get_excludes():
    env_value = os.environ.get("SERENA_FZF_EXCLUDE", "")
    cfg_excludes = []

    if os.path.exists("serena_fzf_config.json"):
        try:
            with open("serena_fzf_config.json", "r", encoding="utf-8") as f:
                cfg = json.load(f)
                cfg_excludes = cfg.get("exclude", []) or []
        except Exception:
            cfg_excludes = []

    if isinstance(cfg_excludes, str):
        cfg_excludes = [p.strip() for p in cfg_excludes.split(",") if p.strip()]

    env_list = [p.strip() for p in env_value.split(",") if p.strip()]
    return list(dict.fromkeys(cfg_excludes + env_list))



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

def should_exclude(path, excludes):
    normalized = path.replace("\\", "/")
    for ex in excludes:
        if not ex:
            continue
        if ex.endswith("/"):
            if normalized.startswith(ex.rstrip("/")):
                return True
        if ex in normalized:
            return True
    return False

def fallback_find_file(query, base_path=None):
    base_path = base_path or get_search_root()
    excludes = get_excludes()
    pattern = os.path.join(base_path, f"**/*{query}*")
    candidates = glob.glob(pattern, recursive=True)
    return [p for p in candidates if not should_exclude(p, excludes)]

def fallback_search_content(pattern, base_path=None):
    base_path = base_path or get_search_root()
    excludes = get_excludes()
    results = []
    for root, dirs, files in os.walk(base_path):
        directories = [d for d in dirs if not should_exclude(os.path.join(root, d), excludes)]
        dirs[:] = directories

        for file in files:
            path = os.path.join(root, file)
            if should_exclude(path, excludes):
                continue
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

def open_in_editor(selection, editor=None):
    if not selection:
        return

    editor = editor or os.environ.get("SERENA_FZF_EDITOR", "code")
    parts = selection.split(":", 2)
    if len(parts) >= 2 and parts[1].isdigit():
        file_line = f"{parts[0]}:{parts[1]}"
        if len(parts) > 2 and parts[2].isdigit():
            file_line += f":{parts[2]}"
        os.system(f'{editor} --goto "{file_line}"')
    else:
        os.system(f'{editor} "{selection}"')