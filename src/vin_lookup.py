#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI VIN Lookup tool - Поиск авто по VIN коду
Usage: python vin_lookup.py 1C6RR7JM2FS578550
"""

import sys
import json
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from lib.vin_decoder import full_decode, get_vehicle_summary, validate_vin

def main():
    vin = sys.argv[1] if len(sys.argv) > 1 else "1C6RR7JM2FS578550"
    print(f"=== Поиск авто по VIN коду: {vin} ===\n")

    is_valid, msg = validate_vin(vin)
    print(f"Валидация: {msg} - {'OK' if is_valid else 'FAIL'}")
    if not is_valid:
        print(f"Ошибка: {msg}")
        return 1

    print("\n--- Локальное декодирование ---")
    result = full_decode(vin, use_nhtsa=True)

    print("\n--- Краткое описание ---")
    print(result.get('summary_text', get_vehicle_summary(vin)))

    print("\n--- Локальные данные ---")
    local = result.get('local_decode', {})
    print(json.dumps(local, indent=2, ensure_ascii=False))

    if result.get('nhtsa_decode'):
        print("\n--- NHTSA vPIC данные ---")
        nhtsa = result['nhtsa_decode']
        if nhtsa.get('success') and nhtsa.get('decoded'):
            for k, v in nhtsa['decoded'].items():
                print(f"{k}: {v}")
        else:
            print(f"NHTSA error: {nhtsa.get('error')}")

    if result.get('known_specific'):
        print("\n--- Проверенные специфичные данные ---")
        print(json.dumps(result['known_specific'], indent=2, ensure_ascii=False))

    print("\n--- OSINT ссылки ---")
    osint = result.get('osint', {}).get('external', {})
    for name, url in osint.items():
        print(f"{name}: {url}")

    # Save JSON report
    report_path = os.path.join(os.path.dirname(__file__), f"vin_report_{vin}.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nОтчет сохранен: {report_path}")

    # Save markdown report
    md_path = os.path.join(os.path.dirname(__file__), f"vin_report_{vin}.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Отчет по VIN: {vin}\n\n")
        f.write(f"Дата: {result.get('timestamp')}\n\n")
        f.write(f"## Краткое описание\n\n```\n{result.get('summary_text')}\n```\n\n")
        f.write("## Локальное декодирование\n\n")
        f.write(f"```json\n{json.dumps(local, indent=2, ensure_ascii=False)}\n```\n\n")
        if result.get('known_specific'):
            f.write("## Проверенные данные\n\n")
            f.write(f"```json\n{json.dumps(result['known_specific'], indent=2, ensure_ascii=False)}\n```\n\n")
        f.write("## OSINT ссылки\n\n")
        for name, url in osint.items():
            f.write(f"- [{name}]({url})\n")
    print(f"Markdown отчет: {md_path}")

    return 0

if __name__ == '__main__':
    sys.exit(main())
