# VFS Shell Emulator

## Описание

Эмулятор командной оболочки UNIX-подобной ОС.

Вариант №2, этап 1-5: REPL с основными командами, поддержкой параметров
командной строки, виртуальной файловой системой (VFS) и командой mv..
Приложение реализовано в форме консольного интерфейса (CLI).
Приглашение к вводу содержит имя VFS и текущий путь.
Все изменения VFS выполняются только в памяти.

## Функции

- `ls` - выводит содержимое каталога VFS.
- `cd` - меняет текущий каталог. Поддерживает абсолютные и относительные пути.
- `cat` - выводит содержимое файлов.
- `echo` - печатает аргументы через пробел.
- `exit` - завершение работы эмулятора.
- `cal` - календарь на месяц (по умолчанию текущий).
- `mv` - перемещает или переименовывает файл или каталог.
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
cat: /home: нет такого файла
vfs$ cal 2 2024
   February 2024
Su Mo Tu We Th Fr Sa
             1  2  3
 4  5  6  7  8  9 10
11 12 13 14 15 16 17
18 19 20 21 22 23 24
25 26 27 28 29
vfs$ cal 13 2024
cal: месяц должен быть от 1 до 12
vfs$ cal abc
cal: аргументы должны быть числами
vfs$ cal 1 2 3
cal: слишком много аргументов
vfs$ cd /home/user/docs
cd: /home/user/docs: нет такого каталога
vfs$ mv notes.txt renamed.txt
mv: notes.txt: нет такого файла или каталога
vfs$ ls
vfs$ cat renamed.txt
cat: renamed.txt: нет такого файла
vfs$ mv renamed.txt /etc
mv: renamed.txt: нет такого файла или каталога
vfs$ ls /etc
ls: /etc: нет такого файла или каталога
vfs$ mv /etc/renamed.txt /etc/renamed2.txt
mv: /etc/renamed.txt: нет такого файла или каталога
vfs$ ls /etc
ls: /etc: нет такого файла или каталога
vfs$ mv
mv: нужно указать источник и назначение
vfs$ mv notes.txt
mv: нужно указать источник и назначение
vfs$ mv nothing.txt dst.txt
mv: nothing.txt: нет такого файла или каталога
vfs$ mv /home /home/user
mv: /home: нет такого файла или каталога
vfs$ mv /etc/renamed2.txt /etc/renamed2.txt
mv: /etc/renamed2.txt: нет такого файла или каталога
vfs$ mv hello.bin /etc/renamed2.txt
mv: hello.bin: нет такого файла или каталога
vfs$ foo
foo: команда не найдена
vfs$ exit
```