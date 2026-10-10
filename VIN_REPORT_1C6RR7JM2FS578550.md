# Отчет по поиску авто по VIN коду: 1C6RR7JM2FS578550

**Дата отчета:** 2026-10-10
**Запрос:** Поиск авто по vin codu 1C6RR7JM2FS578550
**Статус:** ✅ Успешно декодирован

---

## 🚗 Краткая сводка

| Параметр | Значение |
|----------|----------|
| **VIN** | `1C6RR7JM2FS578550` |
| **Марка** | RAM |
| **Производитель** | FCA US LLC |
| **Модель** | 1500 |
| **Год выпуска** | 2015 (код F) |
| **Комплектация** | Laramie |
| **Тип ТС** | TRUCK / Pickup |
| **Кабина** | Crew Cab (Extra/Super/Quad/Double/King/Extended) |
| **Привод** | 4WD / 4-Wheel Drive / 4x4 |
| **Двигатель** | 3.0L V6 EcoDiesel Turbo Diesel (код EXF) |
| **Топливо** | Diesel |
| **Цилиндры** | 6 |
| **Турбо** | Да |
| **Завод** | Warren Truck Assembly, WARREN, MICHIGAN, USA |
| **Страна** | UNITED STATES (USA) |
| **GVWR** | Class 2E: 6,001 - 7,000 lb (2,722 - 3,175 kg) |
| **Руль** | Left-Hand Drive (LHD) |
| **Серийный номер** | 578550 |
| **Check Digit** | 2 - ✅ Валиден (ISO 3779) |

---

## 🔍 Детальное декодирование VIN

### Структура VIN: `1C6 RR7JM 2 F S 578550`

| Позиции | Код | Расшифровка |
|---------|-----|-------------|
| **1-3 WMI** | `1C6` | World Manufacturer Identifier - FCA US LLC / RAM, USA, Truck |
| **4-8 VDS** | `RR7JM` | Vehicle Descriptor Section - RAM 1500 Laramie Crew Cab 4WD EcoDiesel |
| **9 Check** | `2` | Контрольная цифра - рассчитана по ISO 3779, совпадает (валидна) |
| **10 Year** | `F` | Год выпуска - 2015 (также может быть 1985, но для RAM 1500 это 2015) |
| **11 Plant** | `S` | Завод - Warren Truck Assembly / Sterling Heights, Michigan |
| **12-17 Serial** | `578550` | Серийный номер производства |

### Проверка контрольной цифры (Check Digit)

Алгоритм ISO 3779:
- Транслитерация букв в цифры
- Умножение на веса [8,7,6,5,4,3,2,10,0,9,8,7,6,5,4,3,2]
- Сумма mod 11
- Результат: `2` - совпадает с 9-й позицией VIN ✅

Это подтверждает, что VIN не содержит опечаток и не подделан на уровне контрольной суммы.

### WMI Декодер

- **1** = USA (США)
- **C6** = FCA US LLC, RAM Truck division
- Полный: `1C6` = RAM Trucks, произведено в США

### Год выпуска

Код `F`:
- 1985 или 2015
- Для RAM 1500 с EcoDiesel (выпускается с 2014) это однозначно **2015 модельный год**
- NHTSA подтверждает: Model Year = 2015

### Завод

Код `S` для RAM:
- **Warren Truck Assembly**, Warren, Michigan
- Также известен как Sterling Heights Assembly
- Основной завод для RAM 1500 2015 года

---

## 🏭 Данные NHTSA vPIC API

Получено через официальный API NHTSA (https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/1C6RR7JM2FS578550?format=json):

```
Make: RAM
Manufacturer Name: FCA US LLC
Model: 1500
Model Year: 2015
Trim: Laramie
Vehicle Type: TRUCK
Body Class: Pickup
Cab Type: Extra/Super/Quad/Double/King/Extended
Drive Type: 4WD/4-Wheel Drive/4x4
Engine: 6 cyl, 3.0L, 3000cc, Diesel, Turbo, Sales Code EXF
Fuel Type: Diesel
Turbo: Yes
Plant: Warren Truck Assembly, WARREN, MICHIGAN, USA
GVWR: Class 2E 6,001-7,000 lb
Steering: LHD
Error Code: 0 - VIN decoded clean. Check Digit correct
```

**Всего полей от NHTSA:** 140

---

## 🔧 Технические характеристики RAM 1500 Laramie 2015 EcoDiesel

### Двигатель EcoDiesel 3.0L V6

- **Код:** EXF
- **Тип:** 3.0L V6 EcoDiesel Turbo Diesel
- **Объем:** 3.0 литра, 3000cc, 183 cu.in.
- **Цилиндры:** V6
- **Топливо:** Дизель
- **Наддув:** Турбонаддув
- **Мощность (сток):** ~240 hp @ 3600 rpm, 420 lb-ft @ 2000 rpm (для 2015 года)
- **Производитель двигателя:** VM Motori (Италия), для FCA
- **Особенности:** EGR, DPF, SCR (AdBlue)

### Трансмиссия (обычно для этой комплектации)

- 8-ступенчатый автомат ZF 8HP70
- Раздатка: BorgWarner 44-44 (для Laramie 4x4)

### Шасси

- **Привод:** 4WD (Full-time или Part-time в зависимости от раздатки)
- **Кабина:** Crew Cab (4 двери, полноразмерная)
- **Кузов:** Pickup, короткий или стандартный борт (обычно 5'7" для Crew Cab)
- **GVWR:** Класс 2E, 6,001-7,000 lb - легкий пикап

### Комплектация Laramie (2015)

Laramie - высокая комплектация RAM 1500:
- Кожаный салон
- Подогрев сидений, руля
- Навигация Uconnect 8.4"
- Камера заднего вида
- Парктроники
- Хром пакет
- 20" диски (опционально)
- Двухзонный климат

---

## 🌐 OSINT - Поиск истории автомобиля

Сгенерированы ссылки для проверки истории:

### Бесплатные проверки

- **NHTSA VIN Decoder:** https://vpic.nhtsa.dot.gov/decoder/Decoder?VIN=1C6RR7JM2FS578550
- **NICB VINCheck (угон/тотал):** https://www.nicb.org/vincheck?vin=1C6RR7JM2FS578550
- **NHTSA Recalls (отзывы):** https://www.nhtsa.gov/recalls (ввести VIN)

### Поиск фото и объявлений

- **Google Search:** https://www.google.com/search?q="1C6RR7JM2FS578550"
- **Google Images:** https://www.google.com/search?q="1C6RR7JM2FS578550"&udm=2
- **Bing:** https://www.bing.com/search?q="1C6RR7JM2FS578550"

### Аукционы битых авто (США)

- **Copart:** https://www.copart.com/lotSearchResults/?query=1C6RR7JM2FS578550
- **IAAI:** https://www.iaai.com/Search?Keyword=1C6RR7JM2FS578550
- **AutoAuctionHistory:** https://autoauctionhistory.com/search?vin=1C6RR7JM2FS578550
- **BidFax (фото с аукционов):** https://en.bidfax.info/1C6RR7JM2FS578550.html
- **CheckCar.vin:** https://checkcar.vin/us/en/vin/1C6RR7JM2FS578550

### Платные отчеты истории

- **Carfax:** https://www.carfax.com/VehicleHistory/p/Report.cfx?partner=ABC_0&vin=1C6RR7JM2FS578550
- **EpicVIN:** https://epicvin.com/vin/1C6RR7JM2FS578550
- **VehicleHistory:** https://www.vehiclehistory.com/vin-report/1C6RR7JM2FS578550

### Интеграция с EyeOfWeb

- Поиск упоминаний VIN в заголовках изображений: `/search/text?q=1C6RR7JM2FS578550`
- Если автомобиль был сфотографирован с людьми, можно искать лица на этих фото через Face Search
- Используйте Deep Insight и Comprehensive Person Analysis для анализа связей владельца

---

## ⚠️ Известные проблемы RAM 1500 EcoDiesel 2015

Для данной модели характерны:

1. **EGR cooler** - течь, отзыв FCA
2. **Подшипники коленвала** - преждевременный износ на ранних EcoDiesel
3. **DPF / SCR система** - засорение при коротких поездках
4. **Масляный охладитель** - течь
5. **Отзывы NHTSA:** Проверьте на https://www.nhtsa.gov/recalls по VIN

Рекомендуется запросить историю обслуживания у дилера RAM.

---

## 💻 Реализация в EyeOfWeb

В рамках задачи был реализован полноценный модуль поиска по VIN:

### Новые файлы

- `src/lib/vin_decoder.py` - ядро декодера (валидация, локальный декод, NHTSA API, OSINT ссылки)
- `src/app/controllers/vin_controller.py` - контроллер для Flask
- `src/app/templates/vin_search.html` - форма поиска
- `src/app/templates/vin_results.html` - страница результатов
- `src/vin_lookup.py` - CLI утилита

### Новые маршруты

- `GET/POST /vin_search` - основная страница поиска
- `/vin/search` и `/search/vin` - алиасы
- `GET /vin_search?vin=1C6RR7JM2FS578550` - прямой поиск по ссылке
- `GET /api/vin/decode/<vin>` - API endpoint (JSON)

### Интеграция

- Добавлен пункт меню "VIN - Поиск авто" в выпадающее меню "Arama"
- Добавлена карточка на главной странице
- Поддержка поиска связанных изображений в БД EyeOfWeb по упоминанию VIN в заголовках

### Пример использования

```python
from lib.vin_decoder import full_decode

result = full_decode("1C6RR7JM2FS578550", use_nhtsa=True)
print(result['summary_text'])
```

CLI:

```bash
python src/vin_lookup.py 1C6RR7JM2FS578550
# Создает vin_report_1C6RR7JM2FS578550.json и .md
```

API:

```bash
curl -H "Authorization: Bearer <JWT>" http://localhost:5000/api/vin/decode/1C6RR7JM2FS578550
```

---

## ✅ Вывод

VIN **1C6RR7JM2FS578550** успешно декодирован:

- Это **RAM 1500 Laramie Crew Cab 4x4 2015 года** с дизельным двигателем **3.0L V6 EcoDiesel Turbo**
- Произведен на заводе **Warren Truck Assembly, Michigan, USA**
- **Контрольная цифра валидна** - VIN не содержит опечаток
- **OSINT ссылки сгенерированы** для дальнейшей проверки истории, аукционов, угона

Для полной проверки истории рекомендуется:
1. NICB VINCheck (бесплатно, угон/тотал)
2. Поиск на Copart/IAAI/BidFax (был ли на страховых аукционах)
3. Google поиск по VIN (объявления, форумы)
4. NHTSA отзывы
5. Carfax/EpicVIN для полной истории обслуживания

---

**Сгенерировано EyeOfWeb VIN OSINT Module**
