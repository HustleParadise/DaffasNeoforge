"""
Собирает из ntm-patched-fix2.jar файлы, нужные для исправления краша
(Missing storage writes / Missing slot adapter), и упаковывает их в hbm_files.zip.

Запуск:  python collect_hbm_files.py
Или:     python collect_hbm_files.py путь/к/ntm-patched-fix2.jar
"""
import sys
import zipfile
from pathlib import Path

JAR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ntm-patched-fix2.jar")
OUT = Path("hbm_files.zip")

# Конфиги миксинов целиком
EXACT = {
    "hbm-common.mixins.json",
    "hbm-neoforge.mixins.json",
    "META-INF/neoforge.mods.toml",
}

# Папки и имена, которые берём целиком
PREFIXES = (
    "com/hbm/transform/",
)
NAME_PARTS = (
    "BlockStorage",
    "UnstableFuses",
    "StorageWrites",
    "MixinStorage",
)

# Классы, внутри которых встречаются эти строки, тоже берём
NEEDLES = (
    b"StorageWrites",
    b"LecternBlockEntity",
    b"Missing slot adapter",
    b"Missing storage writes",
)

if not JAR.exists():
    sys.exit(f"Не найден файл: {JAR}\nПоложите скрипт рядом с jar или передайте путь аргументом.")

picked = []
with zipfile.ZipFile(JAR) as zin:
    for info in zin.infolist():
        if info.is_dir():
            continue
        name = info.filename
        take = (
            name in EXACT
            or name.startswith(PREFIXES)
            or (name.startswith("com/hbm/") and any(p in name for p in NAME_PARTS))
            or name.endswith(".java")
        )
        if not take and name.endswith(".class") and name.startswith("com/hbm/"):
            data = zin.read(name)
            take = any(n in data for n in NEEDLES)
        if take:
            picked.append(name)

    if not picked:
        sys.exit("Ничего не найдено. Проверьте, что это правильный jar.")

    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
        for name in picked:
            zout.writestr(name, zin.read(name))

size_mb = OUT.stat().st_size / 1024 / 1024
print(f"Файлов собрано: {len(picked)}")
for n in picked[:60]:
    print("  ", n)
if len(picked) > 60:
    print(f"   ... и ещё {len(picked) - 60}")
print(f"\nГотово: {OUT.resolve()} ({size_mb:.2f} МБ)")
print("Пришлите этот файл сюда.")
