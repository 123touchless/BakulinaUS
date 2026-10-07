import os
import shlex

VFS_NAME = "vfs"
MAX_CD_ARGS = 1


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


def main():
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


if __name__ == "__main__":
    main()
