import os
import json

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


def load_json_config(path="serena_fzf_config.json"):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def get_search_root():
    path = os.environ.get("SERENA_FZF_SEARCH_PATH")

    if not path:
        cfg = load_json_config()
        path = cfg.get("search_path")

    return path or "."


def get_excludes():
    env_value = os.environ.get("SERENA_FZF_EXCLUDE", "")
    cfg = load_json_config()
    cfg_excludes = cfg.get("exclude", []) or []

    if isinstance(cfg_excludes, str):
        cfg_excludes = [p.strip() for p in cfg_excludes.split(",") if p.strip()]

    env_list = [p.strip() for p in env_value.split(",") if p.strip()]
    return list(dict.fromkeys(cfg_excludes + env_list))


def get_max_depth():
    env_value = os.environ.get("SERENA_FZF_MAXDEPTH")
    
    if env_value:
        try:
            return int(env_value)
        except ValueError:
            pass
    
    cfg = load_json_config()
    maxdepth = cfg.get("maxdepth")
    if maxdepth:
        try:
            return int(maxdepth)
        except (ValueError, TypeError):
            pass
    
    return None  # Sem limite por padrão


def get_editor():
    return os.environ.get("SERENA_FZF_EDITOR", "code")
