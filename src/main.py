import argparse
import os
import shlex
import sys
import base64
import json

VFS_NAME = "vfs"
MAX_CD_ARGS = 1
COMMENT_PREFIX = "#"
NOT_SET = "(не задан)"
EXIT_ERROR = 1

class VfsError(Exception):
    pass


def parse(line):
    expanded = os.path.expandvars(line)
    return shlex.split(expanded)


def run_command(name, args):
    if name == "exit":
        return False
    if name == "cd":
        if len(args) > MAX_CD_ARGS:
            print("cd: слишком много аргументов")
        else:
            print(f"cd {args}")
    elif name == "ls":
        print(f"ls {args}")
    else:
        print(f"{name}: команда не найдена")
    return True

def vfs_name_from_path(path):
    base = os.path.basename(path)
    name, _ = os.path.splitext(base)
    return name


def load_vfs(path):
    if not os.path.isfile(path):
        raise VfsError(f"VFS-файл не найден: {path}")

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as err:
        raise VfsError(f"неверный формат JSON: {err}") from err
    except OSError as err:
        raise VfsError(f"не удалось прочитать файл: {err}") from err

    if not isinstance(data, dict) or data.get("type") != "dir":
        raise VfsError("корень VFS должен быть каталогом (type=dir)")

    return _validate_node(data, name="/")


def _validate_node(node, name):
    if not isinstance(node, dict):
        raise VfsError(f"узел '{name}': должен быть объектом")

    node_type = node.get("type")

    if node_type == "dir":
        children = node.get("children", {})
        if not isinstance(children, dict):
            raise VfsError(
                f"узел '{name}': children должен быть объектом")
        for child_name, child in children.items():
            child_path = f"{name.rstrip('/')}/{child_name}"
            _validate_node(child, name=child_path)
        return node

    if node_type == "file":
        content = node.get("content", "")
        if node.get("encoding") == "base64":
            try:
                base64.b64decode(content, validate=True)
            except Exception as err:
                raise VfsError(
                    f"файл '{name}': ошибка base64: {err}") from err
        return node

    raise VfsError(f"узел '{name}': неизвестный тип '{node_type}'")


def get_motd(root):
    if not isinstance(root, dict):
        return None
    children = root.get("children") or {}
    motd = children.get("motd")
    if not isinstance(motd, dict) or motd.get("type") != "file":
        return None

    content = motd.get("content", "")
    if motd.get("encoding") == "base64":
        try:
            raw = base64.b64decode(content, validate=True)
        except Exception:
            return None
        return raw.decode("utf-8", errors="replace")
    return content


def build_arg_parser():
    parser = argparse.ArgumentParser(
        description="Эмулятор оболочки UNIX-подобной ОС")
    parser.add_argument("--vfs", help="путь к физическому расположению VFS")
    parser.add_argument("--script", help="путь к стартовому скрипту")
    return parser


def print_debug(args, vfs_name=None):
    print("[debug] параметры запуска:")
    for name, value in sorted(vars(args).items()):
        shown = NOT_SET if value is None else value
        print(f"[debug]   {name} = {shown}")
    print(f"[debug]   vfs_name = {vfs_name or NOT_SET}")


def is_skipped(line):
    stripped = line.strip()
    return not stripped or stripped.startswith(COMMENT_PREFIX)


def read_script(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read().splitlines()


def run_script(path):
    try:
        lines = read_script(path)
    except OSError as err:
        print(f"ошибка: не удалось прочитать скрипт '{path}': {err}")
        sys.exit(EXIT_ERROR)

    running = True
    for number, line in enumerate(lines, start=1):
        if is_skipped(line):
            continue
        print(f"{VFS_NAME}$ {line}")
        try:
            words = parse(line)
        except ValueError as err:
            print(f"ошибка в строке {number} скрипта: ошибка разбора: {err}")
            continue
        if words:
            running = run_command(words[0], words[1:])
        if not running:
            break
    return running


def repl():
    running = True
    while running:
        try:
            line = input(f"{VFS_NAME}$ ")
        except EOFError:
            print()
            break

        try:
            words = parse(line)
        except ValueError as err:
            print(f"ошибка разбора: {err}")
            continue

        if words:
            running = run_command(words[0], words[1:])


def main():
    args = build_arg_parser().parse_args()

    vfs_root = None
    vfs_name = None
    if args.vfs is not None:
        try:
            vfs_root = load_vfs(args.vfs)
            vfs_name = vfs_name_from_path(args.vfs)
        except VfsError as err:
            print(f"ошибка загрузки VFS: {err}")
            sys.exit(EXIT_ERROR)

    print_debug(args, vfs_name)

    if vfs_root is not None:
        motd = get_motd(vfs_root)
        if motd:
            print(motd.rstrip("\n"))

    running = True
    if args.script is not None:
        running = run_script(args.script)

    if running:
        repl()


if __name__ == "__main__":
    main()
