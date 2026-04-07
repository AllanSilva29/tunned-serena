import os
import glob
import subprocess
from datetime import datetime, timedelta
from .config import get_search_root, get_excludes, get_max_depth
from .filters import should_exclude


def _has_ripgrep():
    """Verifica se ripgrep está instalado"""
    try:
        subprocess.run(["rg", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _build_ripgrep_args(base_path, excludes, maxdepth):
    """Constrói argumentos para ripgrep"""
    args = ["rg", "--files", "--no-heading"]

    if maxdepth:
        args.extend(["--max-depth", str(maxdepth)])

    # Adicionar exclusões
    for ex in excludes:
        if not ex:
            continue
        ex = ex.rstrip("/")
        args.extend(["--glob", f"!{ex}", "--glob", f"!{ex}/**"])

    args.append(base_path)
    return args


def _has_grep():
    """Verifica se grep está instalado"""
    try:
        subprocess.run(["grep", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _build_grep_args(pattern, base_path, excludes, maxdepth):
    """Constrói argumentos para grep"""
    args = ["grep", "-F", "-R", "--line-number", "--no-color", "--binary-files=without-match", pattern, base_path]

    for ex in excludes:
        if not ex:
            continue
        ex = ex.rstrip("/")
        args.extend(["--exclude", ex, "--exclude-dir", ex])

    return args


def _parse_date_expression(value, is_before=False):
    if not value:
        return None

    value = value.strip()
    now = datetime.now()

    if value.endswith("d") or value.endswith("h"):
        try:
            amount = int(value[:-1])
        except ValueError:
            return None
        if value.endswith("d"):
            base = now - timedelta(days=amount)
        else:
            base = now - timedelta(hours=amount)
        return base.timestamp()

    try:
        if "T" in value or " " in value:
            dt = datetime.fromisoformat(value)
        else:
            dt = datetime.strptime(value, "%Y-%m-%d")
            if is_before:
                dt = dt.replace(hour=23, minute=59, second=59)
        return dt.timestamp()
    except ValueError:
        return None


def _parse_size_expression(value):
    if not value:
        return None

    value = value.strip().lower()
    multiplier = 1
    if value.endswith("kb"):
        multiplier = 1024
        value = value[:-2]
    elif value.endswith("k"):
        multiplier = 1024
        value = value[:-1]
    elif value.endswith("mb"):
        multiplier = 1024 ** 2
        value = value[:-2]
    elif value.endswith("m"):
        multiplier = 1024 ** 2
        value = value[:-1]
    elif value.endswith("gb"):
        multiplier = 1024 ** 3
        value = value[:-2]
    elif value.endswith("g"):
        multiplier = 1024 ** 3
        value = value[:-1]

    try:
        return int(float(value) * multiplier)
    except ValueError:
        return None


def fallback_find_modified_files(pattern="", before=None, after=None, order=None, base_path=None, maxdepth=None):
    base_path = base_path or get_search_root()
    excludes = get_excludes()
    maxdepth = maxdepth or get_max_depth()

    before_ts = _parse_date_expression(before, is_before=True)
    after_ts = _parse_date_expression(after, is_before=False)
    results = []

    for root, dirs, files in os.walk(base_path):
        depth = root.replace(base_path, "").count(os.sep)
        if maxdepth and depth >= maxdepth:
            dirs[:] = []
            continue

        directories = [d for d in dirs if not should_exclude(os.path.join(root, d), excludes)]
        dirs[:] = directories

        for file in files:
            path = os.path.join(root, file)
            if should_exclude(path, excludes):
                continue
            if pattern and pattern.lower() not in file.lower():
                continue

            try:
                mtime = os.path.getmtime(path)
            except OSError:
                continue

            if before_ts is not None and mtime > before_ts:
                continue
            if after_ts is not None and mtime < after_ts:
                continue

            date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            results.append((mtime, f"{path} | {date_str}"))

    if order == "asc":
        results.sort(key=lambda item: item[0])
    elif order == "desc":
        results.sort(key=lambda item: item[0], reverse=True)

    return [item[1] for item in results]


def fallback_find_size_files(pattern="", min_size=None, max_size=None, order=None, base_path=None, maxdepth=None):
    base_path = base_path or get_search_root()
    excludes = get_excludes()
    maxdepth = maxdepth or get_max_depth()

    min_bytes = _parse_size_expression(min_size)
    max_bytes = _parse_size_expression(max_size)
    results = []

    for root, dirs, files in os.walk(base_path):
        depth = root.replace(base_path, "").count(os.sep)
        if maxdepth and depth >= maxdepth:
            dirs[:] = []
            continue

        directories = [d for d in dirs if not should_exclude(os.path.join(root, d), excludes)]
        dirs[:] = directories

        for file in files:
            path = os.path.join(root, file)
            if should_exclude(path, excludes):
                continue
            if pattern and pattern.lower() not in file.lower():
                continue

            try:
                size = os.path.getsize(path)
            except OSError:
                continue

            if min_bytes is not None and size < min_bytes:
                continue
            if max_bytes is not None and size > max_bytes:
                continue

            size_str = _format_size(size)
            results.append((size, f"{path} | {size_str}"))

    if order == "asc":
        results.sort(key=lambda item: item[0])
    elif order == "desc":
        results.sort(key=lambda item: item[0], reverse=True)

    return [item[1] for item in results]


def _format_size(size):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024 or unit == "TB":
            return f"{size:.1f}{unit}"
        size /= 1024


def fallback_find_file(query, base_path=None, maxdepth=None):
    """Busca arquivos por nome, usando ripgrep se disponível"""
    base_path = base_path or get_search_root()
    excludes = get_excludes()
    maxdepth = maxdepth or get_max_depth()
    
    if _has_ripgrep():
        # Usar ripgrep - muito mais rápido
        args = _build_ripgrep_args(base_path, excludes, maxdepth)
        
        result = subprocess.run(args, capture_output=True, text=True, errors='replace', check=False)
        if result.returncode not in (0, 1):
            # Erro inesperado: fallback para os.walk
            pass
        else:
            files = result.stdout.strip().split('\n') if result.stdout else []
            return [f for f in files if query.lower() in os.path.basename(f).lower()]
    
    # Fallback para implementação original
    if maxdepth:
        # Com limite de profundidade, usar os.walk
        results = []
        for root, dirs, files in os.walk(base_path):
            # Calcular profundidade
            depth = root.replace(base_path, "").count(os.sep)
            if depth >= maxdepth:
                dirs[:] = []  # Não descer mais
                continue
            
            # Filtrar diretórios excluídos
            directories = [d for d in dirs if not should_exclude(os.path.join(root, d), excludes)]
            dirs[:] = directories
            
            # Procurar arquivos
            for file in files:
                if query.lower() in file.lower():
                    path = os.path.join(root, file)
                    if not should_exclude(path, excludes):
                        results.append(path)
        return results
    else:
        # Sem limite, usar glob (mais rápido)
        pattern = os.path.join(base_path, f"**/*{query}*")
        candidates = glob.glob(pattern, recursive=True)
        return [p for p in candidates if not should_exclude(p, excludes)]


def fallback_search_content(pattern, base_path=None, maxdepth=None):
    """Busca padrões no conteúdo de arquivos, usando ripgrep se disponível"""
    base_path = base_path or get_search_root()
    excludes = get_excludes()
    maxdepth = maxdepth or get_max_depth()
    
    if _has_ripgrep():
        # Usar ripgrep para busca de conteúdo - extremamente rápido
        args = ["rg", "-F", "--line-number", "--no-heading", pattern]

        if maxdepth:
            args.extend(["--max-depth", str(maxdepth)])

        for ex in excludes:
            if not ex:
                continue
            ex = ex.rstrip("/")
            args.extend(["--glob", f"!{ex}", "--glob", f"!{ex}/**"])

        args.append(base_path)

        result = subprocess.run(args, capture_output=True, text=True, errors='replace', check=False)
        if result.returncode not in (0, 1):
            pass
        else:
            lines = result.stdout.strip().split('\n') if result.stdout else []
            return [line for line in lines if line.strip()]
    elif _has_grep():
        args = _build_grep_args(pattern, base_path, excludes, maxdepth)
        try:
            result = subprocess.run(args, capture_output=True, text=True, errors='replace')
            lines = result.stdout.strip().split('\n') if result.stdout else []
            return [line for line in lines if line.strip()]
        except subprocess.CalledProcessError:
            pass
    
    # Fallback para implementação original
    results = []
    
    for root, dirs, files in os.walk(base_path):
        # Respeitar maxdepth
        if maxdepth:
            depth = root.replace(base_path, "").count(os.sep)
            if depth >= maxdepth:
                dirs[:] = []
                continue
        
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