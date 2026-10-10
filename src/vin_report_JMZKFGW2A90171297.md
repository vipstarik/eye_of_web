# Отчет по VIN: JMZKFGW2A90171297

Дата: 2026-10-10T18:29:28.487755

## Краткое описание

```
VIN: JMZKFGW2A90171297
Марка: Mazda
Модель: CX-5 (100% of KF in EU DB are CX-5, 2017-2024) (код KF)
Год (символ 9): варианты [2009, 2039] - Year 9 = 2009 but CX-5 launched 2012, possible mismatch - maybe VIN typo, should be K=2019? If year=K and plant=0, then CX-5 2019
Завод: 0 - Hiroshima, Japan (Mazda Motor Corporation)
Серийный: 171297
Трансмиссия (EU pos9): A = Automatic (EU transmission code)
Двигатель: G = Skyactiv-G petrol 2.0/2.5 or Skyactiv-D 2.2 diesel - need full VDS decode
WMI: JMZ - Mazda Motor Corp. (Europe Export)
Проверка check digit: US: FAIL (ожидается 9) - для EU JMZ не применяется
NHTSA статус: 1 - Check Digit does not calculate, 7 - Manufacturer not registered for US, 400 - Invalid Characters
Вывод: VIN is European market Mazda, not US. For EU, check digit validation not applicable.
```

## Локальное декодирование

```json
{
  "success": true,
  "vin": "JMZKFGW2A90171297",
  "wmi": "JMZ",
  "vds": "KFGW2",
  "vis": "90171297",
  "check_digit": {
    "actual": "A",
    "expected": "9",
    "valid": false,
    "note": "Not enforced for EU JMZ"
  },
  "year_char": "9",
  "year_options": [
    2009,
    2039
  ],
  "plant_code": "0",
  "serial_number": "171297",
  "manufacturer_info": {
    "manufacturer": "Mazda Motor Corp. (Europe Export)",
    "country": "Japan",
    "type": "Passenger"
  },
  "is_ram": false,
  "ram_details": {},
  "is_mazda": true,
  "mazda_details": {
    "model_code": "KF",
    "model_info": {
      "model": "CX-5",
      "years": "2017-2025",
      "type": "SUV"
    },
    "model": "CX-5",
    "plant_info": "Hiroshima, Japan - Mazda main plant",
    "transmission_eu": "Automatic (unknown) / 6-speed Auto",
    "is_eu": true,
    "note": "EU Mazda VIN - check digit not enforced in EU, year at pos10 may be 0 placeholder for older EU",
    "specific_analysis": {
      "wmi": "JMZ = Mazda Europe Export, Japan",
      "model_code_KF": "CX-5 2017-2025 (100% of KF in EU DB are CX-5)",
      "possible_mismatch": "Year char 9 = 2009 but CX-5 launched 2012 - possible typo, maybe year should be K=2019? Or VIN is for Mazda3 BL? But KF is definitely CX-5",
      "alternative": "If year is actually 2019 (K) and plant 0=Hiroshima, then VIN would be JMZKFGW2AK0171297 - CX-5 2019",
      "plant_0": "Hiroshima, Japan - main Mazda plant",
      "serial": "171297",
      "transmission_A": "Automatic (EU code A)",
      "engine_G": "Possibly Skyactiv-G 2.0 or 2.5 petrol, or Skyactiv-D 2.2 diesel - need full VDS",
      "note_eu": "For EU market, position 9 is transmission, position 10 is year (9=2009), position 11 is plant (0=Hiroshima). Check digit validation not applicable for EU.",
      "validity": "NHTSA reports: Invalid character 9:A, Check Digit does not calculate, Manufacturer not registered for US - expected for EU VIN"
    }
  },
  "sections": {
    "wmi": "JMZ - World Manufacturer Identifier",
    "vds": "KFGW2 - Vehicle Descriptor Section",
    "check": "A - Check Digit (EU: transmission)",
    "year": "9 - Model Year",
    "plant": "0 - Assembly Plant",
    "serial": "171297 - Serial Number"
  }
}
```

## Проверенные данные

```json
{
  "make": "Mazda",
  "manufacturer": "Mazda Motor Corp. Japan (Europe Export)",
  "wmi": "JMZ = Mazda Europe",
  "model_code": "KF",
  "model": "CX-5 (100% of KF in EU DB are CX-5, 2017-2024)",
  "model_year_char": "9",
  "model_year_options": [
    2009,
    2039
  ],
  "model_year_note": "Year 9 = 2009 but CX-5 launched 2012, possible mismatch - maybe VIN typo, should be K=2019? If year=K and plant=0, then CX-5 2019",
  "alternative_vin": "JMZKFGW2AK0171297 would be CX-5 2019 Hiroshima",
  "plant": {
    "code": "0",
    "city": "Hiroshima",
    "country": "Japan",
    "company": "Mazda Motor Corporation"
  },
  "transmission": "A = Automatic (EU transmission code)",
  "serial": "171297",
  "engine_hint": "G = Skyactiv-G petrol 2.0/2.5 or Skyactiv-D 2.2 diesel - need full VDS decode",
  "body": "W2 = likely 5-door SUV body",
  "validity": {
    "nhtsa_error": "1 - Check Digit does not calculate, 7 - Manufacturer not registered for US, 400 - Invalid Characters",
    "nhtsa_additional": "Invalid character(s): 9:A",
    "interpretation": "Expected for EU VIN - NHTSA only validates US VINs, EU VINs use different check digit logic, JMZ not registered for US import",
    "check_digit": "A at pos9 is not numeric/X - invalid for US but valid as transmission code for EU",
    "conclusion": "VIN is European market Mazda, not US. For EU, check digit validation not applicable."
  },
  "osint_note": "EU Mazda VIN - search in EU bases: carVertical, Carlytics, AutoDNA, European registries, not US Copart/IAAI"
}
```

## OSINT ссылки

- [google_search](https://www.google.com/search?q="JMZKFGW2A90171297")
- [google_images](https://www.google.com/search?q="JMZKFGW2A90171297"&udm=2)
- [bing_search](https://www.bing.com/search?q="JMZKFGW2A90171297")
- [nhtsa_decoder](https://vpic.nhtsa.dot.gov/decoder/Decoder?VIN=JMZKFGW2A90171297)
- [nhtsa_api](https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/JMZKFGW2A90171297?format=json)
- [nicb_vincheck](https://www.nicb.org/vincheck?vin=JMZKFGW2A90171297)
- [carfax](https://www.carfax.com/VehicleHistory/p/Report.cfx?partner=ABC_0&vin=JMZKFGW2A90171297)
- [epicvin](https://epicvin.com/vin/JMZKFGW2A90171297)
- [vpic](https://www.vehiclehistory.com/vin-report/JMZKFGW2A90171297)
- [copart](https://www.copart.com/lotSearchResults/?query=JMZKFGW2A90171297)
- [iaai](https://www.iaai.com/Search?Keyword=JMZKFGW2A90171297)
- [autoauction_history](https://autoauctionhistory.com/search?vin=JMZKFGW2A90171297)
- [bidfax](https://en.bidfax.info/JMZKFGW2A90171297.html)
- [checkcar](https://checkcar.vin/us/en/vin/JMZKFGW2A90171297)
- [carlytics_eu](https://www.carlytics.eu/vin-decoder/mazda?vin=JMZKFGW2A90171297)
- [carvertical](https://www.carvertical.com/en/vin-decoder?vin=JMZKFGW2A90171297)
- [autodna](https://www.autodna.com/vin/JMZKFGW2A90171297)
- [cebia](https://en.cebia.com/vehicle-history/mazda/JMZKFGW2A90171297)
- [vin_info](https://en.vin-info.com/search/vin/JMZKFGW2A90171297)
- [mazda_recall_eu](https://www.mazda.eu/recall-information/)
- [eu_rapid_alert](https://ec.europa.eu/safety-gate-alerts/screen/search?searchString=JMZKFGW2A90171297)
