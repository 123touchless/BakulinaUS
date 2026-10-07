import argparse
import os
import shlex
import sys

VFS_NAME = "vfs"
MAX_CD_ARGS = 1
COMMENT_PREFIX = "#"
NOT_SET = "(не задан)"
EXIT_ERROR = 1


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


def build_arg_parser():
    parser = argparse.ArgumentParser(
        description="Эмулятор оболочки UNIX-подобной ОС")
    parser.add_argument("--vfs", help="путь к физическому расположению VFS")
    parser.add_argument("--script", help="путь к стартовому скрипту")
    return parser


def print_debug(args):
    print("[debug] параметры запуска:")
    for name, value in sorted(vars(args).items()):
        shown = NOT_SET if value is None else value
        print(f"[debug]   {name} = {shown}")


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
    print_debug(args)

    running = True
    if args.script is not None:
        running = run_script(args.script)

    if running:
        repl()


if __name__ == "__main__":
    main()
