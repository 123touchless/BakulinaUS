import argparse
import os
import shlex
import sys
import base64
import json
import calendar
import datetime
import posixpath

VFS_NAME = "vfs"
MAX_CD_ARGS = 1
MAX_LS_ARGS = 1
MAX_CAL_ARGS = 2
MIN_MONTH = 1
MAX_MONTH = 12
MIN_YEAR = 1
MAX_YEAR = 9999
COMMENT_PREFIX = "#"
NOT_SET = "(не задан)"
EXIT_ERROR = 1

class VfsError(Exception):
    pass


def parse(line):
    expanded = os.path.expandvars(line)
    return shlex.split(expanded)
def new_state(root=None):
    if root is None:
        root = {"type": "dir", "children": {}}
    return {"root": root, "cwd": "/"}

def prompt(state):
    return f"{VFS_NAME}:{state['cwd']}$ "

def abs_path(state, path):
    if not path.startswith("/"):
        path = state["cwd"] + "/" + path
    return "/" + posixpath.normpath(path).lstrip("/")

def find_node(root, path):
    node = root
    for part in path.split("/"):
        if not part:
            continue
        if node.get("type") != "dir":
            return None
        node = node.get("children", {}).get(part)
        if node is None:
            return None
    return node

def read_file(node):
    content = node.get("content", "")
    if node.get("encoding") == "base64":
        return base64.b64decode(content).decode("utf-8", errors="replace")
    return content

def cmd_ls(args, state):
    """ls [путь]: показывает содержимое каталога."""
    if len(args) > MAX_LS_ARGS:
        print("ls: слишком много аргументов")
        return
    target = args[0] if args else "."
    node = find_node(state["root"], abs_path(state, target))
    if node is None:
        print(f"ls: {target}: нет такого файла или каталога")
    elif node["type"] == "file":
        print(target)
    else:
        children = node.get("children", {})
        for name in sorted(children):
            suffix = "/" if children[name]["type"] == "dir" else ""
            print(name + suffix)

def cmd_cd(args, state):
    if len(args) > MAX_CD_ARGS:
        print("cd: слишком много аргументов")
        return
    target = args[0] if args else "/"
    path = abs_path(state, target)
    node = find_node(state["root"], path)
    if node is None:
        print(f"cd: {target}: нет такого каталога")
    elif node["type"] != "dir":
        print(f"cd: {target}: не каталог")
    else:
        state["cwd"] = path

def cmd_echo(args):
    print(" ".join(args))

def cmd_cat(args, state):
    if not args:
        print("cat: не указан файл")
        return
    for target in args:
        node = find_node(state["root"], abs_path(state, target))
        if node is None:
            print(f"cat: {target}: нет такого файла")
        elif node["type"] == "dir":
            print(f"cat: {target}: это каталог")
        else:
            print(read_file(node).rstrip("\n"))

def cmd_cal(args):
    if len(args) > MAX_CAL_ARGS:
        print("cal: слишком много аргументов")
        return
    try:
        numbers = [int(arg) for arg in args]
    except ValueError:
        print("cal: аргументы должны быть числами")
        return
    today = datetime.date.today()
    month = numbers[0] if numbers else today.month
    year = numbers[1] if len(numbers) > 1 else today.year
    if not MIN_MONTH <= month <= MAX_MONTH:
        print(f"cal: месяц должен быть от {MIN_MONTH} до {MAX_MONTH}")
    elif not MIN_YEAR <= year <= MAX_YEAR:
        print(f"cal: год должен быть от {MIN_YEAR} до {MAX_YEAR}")
    else:
        text = calendar.TextCalendar(calendar.SUNDAY)
        print(text.formatmonth(year, month).rstrip())

def run_command(name, args, state=None):
    if state is None:
        state = new_state()
    if name == "exit":
        return False
    if name == "cd":
        cmd_cd(args, state)
    elif name == "ls":
        cmd_ls(args, state)
    elif name == "echo":
        cmd_echo(args)
    elif name == "cal":
        cmd_cal(args)
    elif name == "cat":
        cmd_cat(args, state)
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
