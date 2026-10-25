"""
Точечный патч NTM (HBM) для краша на Youer:
  Mixin MixinStorageTargets FAILED during APPLY
  Missing storage writes: LecternBlockEntity$1 -> LecternBlockEntity.book

Что делает: заменяет цель "LecternBlockEntity$1" на несуществующую "LecternBlockEntity$9"
в двух классах (MixinStorageTargets и StorageLayouts). Остальные миксины остаются,
сундуки и прочее работают как раньше. Длина строк не меняется.

Запуск (нужен ИСХОДНЫЙ ntm-patched-fix2.jar, не fix3!):
    python patch_hbm_lectern.py
    python patch_hbm_lectern.py путь\\к\\ntm-patched-fix2.jar
Результат: ntm-patched-fix4.jar рядом со скриптом.
"""
import sys
import zipfile
from pathlib import Path

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ntm-patched-fix2.jar")
DST = Path("ntm-patched-fix4.jar")

OLD = b"net.minecraft.world.level.block.entity.LecternBlockEntity$1"
NEW = b"net.minecraft.world.level.block.entity.LecternBlockEntity$9"
FILES = {
    "com/hbm/mixin/MixinStorageTargets.class",
    "com/hbm/inventory/StorageLayouts.class",
}

if not SRC.exists():
    sys.exit(f"Не найден файл: {SRC}")

done = set()
with zipfile.ZipFile(SRC) as zin, zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename in FILES:
            if data.count(OLD) != 1:
                sys.exit(f"{item.filename}: ожидалась 1 замена, найдено {data.count(OLD)}. "
                         "Похоже, это не fix2 или он уже пропатчен.")
            data = data.replace(OLD, NEW)
            done.add(item.filename)
            print("патч:", item.filename)
        zout.writestr(item, data)

if done != FILES:
    DST.unlink(missing_ok=True)
    sys.exit("Не все файлы найдены в jar, результат удалён.")

print("Готово:", DST.resolve())
print("Положите его вместо старого jar и удалите ntm-patched-fix2.jar и fix3.")
