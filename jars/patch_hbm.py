import zipfile, json

SRC = "ntm-patched-fix2.jar"
DST = "ntm-patched-fix3.jar"

# Что убрать из списков миксинов
REMOVE = {
    "hbm-common.mixins.json": {"MixinStorageTargets"},
    "hbm-neoforge.mixins.json": {
        "storage.MixinInventoryHandler",
        "storage.MixinStorageBlockEntity",
        "storage.MixinBackpackBlockEntity",
        "storage.MixinUpgradeHandler",
        "storage.MixinBackpackStorage",
        "storage.MixinItemContentsStorage",
        # Добавьте сюда миксин cursorChanged (AbstractContainerMenu), например:
        # "inventory.MixinAbstractContainerMenu",
    },
}

with zipfile.ZipFile(SRC) as zin, zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename in REMOVE:
            cfg = json.loads(data)
            for key in ("mixins", "server", "client"):
                if key in cfg:
                    before = len(cfg[key])
                    cfg[key] = [m for m in cfg[key] if m not in REMOVE[item.filename]]
                    print(f"{item.filename}: {key} {before} -> {len(cfg[key])}")
            data = json.dumps(cfg, indent=2).encode("utf-8")
        zout.writestr(item, data)

print("Готово:", DST)
