import os
from .config import get_editor


def open_in_editor(selection, editor=None):
    """Abre arquivo no editor, posicionando no cursor se linha especificada"""
    if not selection:
        return

    editor = editor or get_editor()
    parts = selection.split(":", 2)
    if len(parts) >= 2 and parts[1].isdigit():
        file_line = f"{parts[0]}:{parts[1]}"
        if len(parts) > 2 and parts[2].isdigit():
            file_line += f":{parts[2]}"
        os.system(f'{editor} --goto "{file_line}"')
    else:
        os.system(f'{editor} "{selection}"')
