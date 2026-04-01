import subprocess


def run_fzf(options):
    """Executa fzf como seletor fuzzy e retorna seleção"""
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
