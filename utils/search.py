import os
import glob
import subprocess
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
    args = ["rg", "--files", "--hidden", "--no-heading"]
    
    if maxdepth:
        args.extend(["--max-depth", str(maxdepth)])
    
    # Adicionar exclusões
    for ex in excludes:
        if ex:
            args.extend(["--glob", f"!{ex}"])
    
    args.append(base_path)
    return args


def fallback_find_file(query, base_path=None, maxdepth=None):
    """Busca arquivos por nome, usando ripgrep se disponível"""
    base_path = base_path or get_search_root()
    excludes = get_excludes()
    maxdepth = maxdepth or get_max_depth()
    
    if _has_ripgrep():
        # Usar ripgrep - muito mais rápido
        args = _build_ripgrep_args(base_path, excludes, maxdepth)
        
        try:
            result = subprocess.run(args, capture_output=True, text=True, errors='replace', check=True)
            files = result.stdout.strip().split('\n') if result.stdout else []
            
            # Filtrar por query (ripgrep lista todos os arquivos, precisamos filtrar)
            return [f for f in files if query.lower() in os.path.basename(f).lower()]
        except subprocess.CalledProcessError:
            # Fallback para os.walk se rg falhar
            pass
    
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
        args = ["rg", "--line-number", "--no-heading", "--hidden", pattern]
        
        if maxdepth:
            args.extend(["--max-depth", str(maxdepth)])
        
        # Adicionar exclusões
        for ex in excludes:
            if ex:
                args.extend(["--glob", f"!{ex}"])
        
        args.append(base_path)
        
        try:
            result = subprocess.run(args, capture_output=True, text=True, errors='replace', check=True)
            lines = result.stdout.strip().split('\n') if result.stdout else []
            return [line for line in lines if line.strip()]
        except subprocess.CalledProcessError:
            # Fallback se rg falhar
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