# VFS Shell Emulator

## Описание

Эмулятор командной оболочки UNIX-подобной ОС.

Вариант №2, этап 1-3: REPL с командами-заглушками, поддержкой параметров
командной строки и виртуальной файловой системой (VFS).
Приложение реализовано в форме консольного интерфейса (CLI).
Приглашение к вводу содержит имя VFS.

## Функции

- `ls` - команда-заглушка, выводит своё имя и список аргументов.
- `cd` - команда-заглушка, выводит своё имя и список аргументов.
  Если передано больше одного аргумента - выводится сообщение об ошибке.
- `exit` - завершение работы эмулятора.
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
vfs$ ls -l /tmp
ls ['-l', '/tmp']
vfs$ cd $USERPROFILE
cd ['C:Usersbakul']
vfs$ ls "my file"
ls ['my file']
vfs$ cd a b
cd: слишком много аргументов
vfs$ foo
foo: команда не найдена
vfs$ "незакрытая кавычка
ошибка в строке 7 скрипта: ошибка разбора: No closing quotation
vfs$ exit

```