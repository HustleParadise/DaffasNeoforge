#!/usr/bin/env python3
"""Убирает MixinRegistryLoadTask из hbm-common.mixins.json в jar NTM.
Использование: python3 patch_ntm.py входной.jar выходной.jar"""
import sys, zipfile, json
src, dst = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, 'w') as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == 'hbm-common.mixins.json':
            lines = data.decode('utf-8').split('\n')
            new = [l for l in lines if l.strip() != '"MixinRegistryLoadTask",']
            assert len(new) == len(lines) - 1, 'строка MixinRegistryLoadTask не найдена'
            data = '\n'.join(new).encode('utf-8')
            json.loads(data)  # проверка валидности JSON
        zout.writestr(item, data, compress_type=item.compress_type)
print('Готово:', dst)
