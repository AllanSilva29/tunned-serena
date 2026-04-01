import os


def should_exclude(path, excludes):
    """Verifica se um caminho deve ser excluído baseado em padrões"""
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


def filter_excluded_dirs(dirs, root, excludes):
    """Filtra diretórios que devem ser excluídos durante traversal"""
    return [d for d in dirs if not should_exclude(os.path.join(root, d), excludes)]
