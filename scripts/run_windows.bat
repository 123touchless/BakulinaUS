@echo off

echo === 1. Minimal VFS ===
python src\main.py --vfs .\vfs\minimal.json --script .\scripts\start.txt

echo.
echo === 2. Few files VFS ===
python src\main.py --vfs .\vfs\few_files.json --script .\scripts\start.txt

echo.
echo === 3. Deep VFS ===
python src\main.py --vfs .\vfs\deep.json --script .\scripts\start.txt

echo.
echo === 4. Oshibka: fajl ne najden ===
python src\main.py --vfs .\vfs\no_such.json --script .\scripts\start.txt

echo.
echo === 5. Oshibka: nevernyj format ===
python src\main.py --vfs .\README.md --script .\scripts\start.txt