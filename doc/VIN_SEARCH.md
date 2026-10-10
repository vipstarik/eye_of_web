# VIN Search Module - Поиск авто по VIN коду

## Описание

Модуль для EyeOfWeb, позволяющий искать автомобили по VIN коду с использованием OSINT методов.

Реализовано для VIN `1C6RR7JM2FS578550` (RAM 1500 Laramie 2015 EcoDiesel) и `JMZKFGW2A90171297` (Mazda CX-5 KF 2017-2025 EU), но работает с любым 17-значным VIN.

Поддерживает US VIN (NHTSA) и EU Mazda VIN (JMZ) с особой логикой: позиция 9 = трансмиссия (не check digit), 11 = завод Hiroshima/Hofu.

## Возможности

- ✅ Валидация VIN (17 символов, без I,O,Q, проверка формата)
- ✅ Проверка контрольной цифры (9-я позиция) по алгоритму ISO 3779 (weighted modulus 11)
- ✅ Локальное декодирование WMI (производитель, страна), VDS, VIS
- ✅ Декодирование года выпуска (10-я позиция) и завода (11-я)
- ✅ Интеграция с NHTSA vPIC API (140+ полей)
- ✅ Генерация OSINT ссылок: Google, Copart, IAAI, NICB, Carfax, BidFax, и т.д.
- ✅ Поиск связанных изображений в БД EyeOfWeb по упоминанию VIN в заголовках
- ✅ Flask UI + API endpoint

## Файлы

- `src/lib/vin_decoder.py` - основная логика
- `src/app/controllers/vin_controller.py` - контроллер
- `src/app/templates/vin_search.html` - форма
- `src/app/templates/vin_results.html` - результаты
- `src/vin_lookup.py` - CLI
- `src/app/routes/web.py` - маршруты (добавлены)

## Маршруты

| Маршрут | Метод | Описание |
|---------|-------|----------|
| `/vin_search` | GET, POST | Форма и результаты |
| `/vin/search` | GET, POST | Алиас |
| `/search/vin` | GET, POST | Алиас |
| `/api/vin/decode/<vin>` | GET | JSON API |

## Использование

### Web UI

1. Войдите в EyeOfWeb
2. Перейдите в Arama -> VIN - Поиск авто
3. Введите VIN, например `1C6RR7JM2FS578550`
4. Получите полный отчет

### CLI

```bash
python src/vin_lookup.py 1C6RR7JM2FS578550
```

Создает `vin_report_1C6RR7JM2FS578550.json` и `.md`

### Python API

```python
from lib.vin_decoder import full_decode, validate_vin, get_vehicle_summary

vin = "1C6RR7JM2FS578550"
is_valid, msg = validate_vin(vin)
result = full_decode(vin, use_nhtsa=True)
print(result['summary_text'])
print(result['osint']['external'])
```

### HTTP API

```bash
curl -H "Authorization: Bearer <JWT>" \
     http://localhost:5000/api/vin/decode/1C6RR7JM2FS578550
```

## Пример результата для 1C6RR7JM2FS578550

```
VIN: 1C6RR7JM2FS578550
Марка: RAM
Модель: 1500
Год: 2015
Комплектация: Laramie
Тип: Pickup Crew Cab 4WD
Двигатель: 3.0L V6 EcoDiesel Turbo Diesel (EXF)
Топливо: Diesel
Завод: Warren Truck Assembly, Michigan, USA
Check Digit: OK
```

## OSINT ссылки

Генерируются автоматически:

- Google, Bing поиск
- NHTSA decoder
- NICB VINCheck (угон)
- Copart, IAAI, BidFax (аукционы битых авто)
- Carfax, EpicVIN (история)

## Интеграция с EyeOfWeb Face Search

Если автомобиль был сфотографирован с людьми:

1. Найдите фото авто через OSINT (Copart, Google Images)
2. Загрузите фото в EyeOfWeb Face Detection
3. Используйте Face Search для поиска владельца
4. Deep Insight / Comprehensive Analysis для анализа связей

## Безопасность

- Валидация входных данных (regex, без I,O,Q)
- CSRF защита (Flask-WTF)
- Rate limiting (30/minute)
- Login required

## Зависимости

- `requests` (опционально, для NHTSA API) - если нет, используется только локальный декодер
- Flask, Flask-JWT-Extended

## Тестирование

```bash
python -m lib.vin_decoder 1C6RR7JM2FS578550
python src/vin_lookup.py 1C6RR7JM2FS578550
```

## Лицензия

MIT, как и основной проект EyeOfWeb
