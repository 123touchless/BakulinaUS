@echo off
echo === 1. Bez parametrov (REPL) ===
python src\main.py

echo === 2. Tolko --vfs ===
python src\main.py --vfs .\vfs_data

echo === 3. Tolko --script ===
python src\main.py --script .\scripts\start.txt

echo === 4. Oba parametra ===
python src\main.py --vfs .\vfs_data --script .\scripts\start.txt