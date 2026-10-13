# VFS Shell Emulator

## Описание

Эмулятор командной оболочки UNIX-подобной ОС.

Вариант №2, этап 1-4: REPL с командами-заглушками, поддержкой параметров
командной строки и виртуальной файловой системой (VFS).
Приложение реализовано в форме консольного интерфейса (CLI).
Приглашение к вводу содержит имя VFS.

## Функции

- `ls` - выводит содержимое каталога VFS.
- `cd` - меняет текущий каталог. Поддерживает абсолютные и относительные пути.
- `cat` - выводит содержимое файлов.
- `echo` - печатает аргументы через пробел.
- `exit` - завершение работы эмулятора.
- `cal` - календарь на месяц (по умолчанию текущий).
- Парсер поддерживает раскрытие переменных окружения реальной ОС
  (например, `$HOME`, `$PATH`) через `os.path.expandvars`.
- Парсер корректно обрабатывает аргументы в кавычках (через `shlex`).
- Обработка ошибок: неизвестная команда, неверные аргументы, ошибка разбора строки.
- `--vfs PATH` - путь к JSON-файлу VFS
- `--script PATH` - путь к стартовому скрипту
- type: "dir" - каталог с children
- type: "file" - файл с content
- encoding: "base64" - бинарные данные
- файл motd в корне выводится при старте

## Сборка и запуск

Запуск без параметров:

```bash
python src/main.py
```

Запуск с VFS:

```bash
python src/main.py --vfs vfs/deep.json
```

Запуск со стартовым скриптом:

```bash
python src/main.py --vfs vfs/few_files.json --script scripts/start.txt
```

## Запуск тестов

```bash
pytest
```

## Примеры использования

```text
python src/main.py --vfs vfs/few_files.json --script scripts/start.txt
[debug] параметры запуска:
[debug]   script = scripts/start.txt
[debug]   vfs = vfs/few_files.json
[debug]   vfs_name = few_files
Добро пожаловать в several!
vfs$ ls
vfs$ ls home
ls: home: нет такого файла или каталога
vfs$ ls /home/user/docs
ls: /home/user/docs: нет такого файла или каталога
vfs$ ls /etc/config.txt
ls: /etc/config.txt: нет такого файла или каталога
vfs$ ls nothing
ls: nothing: нет такого файла или каталога
vfs$ ls a b
ls: слишком много аргументов
vfs$ cd home/user
cd: home/user: нет такого каталога
vfs$ ls
vfs$ cd docs
cd: docs: нет такого каталога
vfs$ ls
vfs$ cd ..
vfs$ cd ../..
vfs$ cd /etc
cd: /etc: нет такого каталога
vfs$ cd
vfs$ cd nothing
cd: nothing: нет такого каталога
vfs$ cd /etc/config.txt
cd: /etc/config.txt: нет такого каталога
vfs$ cd a b
cd: слишком много аргументов
vfs$ echo Привет, мир
Привет, мир
vfs$ echo "много   пробелов" и $HOME
много   пробелов и $HOME
vfs$ echo

vfs$ cd /home/user/docs
cd: /home/user/docs: нет такого каталога
vfs$ cat notes.txt
cat: notes.txt: нет такого файла
vfs$ cat hello.bin
cat: hello.bin: нет такого файла
vfs$ cat notes.txt hello.bin
cat: notes.txt: нет такого файла
cat: hello.bin: нет такого файла
vfs$ cat /etc/config.txt
cat: /etc/config.txt: нет такого файла
vfs$ cat
cat: не указан файл
vfs$ cat nothing.txt
cat: nothing.txt: нет такого файла
vfs$ cat /home
cal: слишком много аргументов
vfs$ foo
foo: команда не найдена
vfs$ exit
```