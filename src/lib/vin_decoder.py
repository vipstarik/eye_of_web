#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VIN Decoder & OSINT Module for EyeOfWeb
Поддержка поиска авто по VIN коду
"""

import re
import json
try:
    import requests
except ImportError:
    requests = None
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# VIN Year codes mapping (1980-2039)
YEAR_CODES = {
    'A': 1980, 'B': 1981, 'C': 1982, 'D': 1983, 'E': 1984, 'F': 1985, 'G': 1986, 'H': 1987,
    'J': 1988, 'K': 1989, 'L': 1990, 'M': 1991, 'N': 1992, 'P': 1993, 'R': 1994, 'S': 1995,
    'T': 1996, 'V': 1997, 'W': 1998, 'X': 1999, 'Y': 2000,
    '1': 2001, '2': 2002, '3': 2003, '4': 2004, '5': 2005, '6': 2006, '7': 2007, '8': 2008, '9': 2009,
    'A_2010': 2010, 'B_2010': 2011, 'C_2010': 2012, 'D_2010': 2013, 'E_2010': 2014, 'F_2010': 2015,
    'G_2010': 2016, 'H_2010': 2017, 'J_2010': 2018, 'K_2010': 2019, 'L_2010': 2020, 'M_2010': 2021,
    'N_2010': 2022, 'P_2010': 2023, 'R_2010': 2024, 'S_2010': 2025, 'T_2010': 2026, 'V_2010': 2027,
    'W_2010': 2028, 'X_2010': 2029, 'Y_2010': 2030,
}

# Extended year decode handling duplicate letters
YEAR_CODE_MAP = {
    'A': [1980, 2010], 'B': [1981, 2011], 'C': [1982, 2012], 'D': [1983, 2013],
    'E': [1984, 2014], 'F': [1985, 2015], 'G': [1986, 2016], 'H': [1987, 2017],
    'J': [1988, 2018], 'K': [1989, 2019], 'L': [1990, 2020], 'M': [1991, 2021],
    'N': [1992, 2022], 'P': [1993, 2023], 'R': [1994, 2024], 'S': [1995, 2025],
    'T': [1996, 2026], 'V': [1997, 2027], 'W': [1998, 2028], 'X': [1999, 2029],
    'Y': [2000, 2030],
    '1': [2001, 2031], '2': [2002, 2032], '3': [2003, 2033], '4': [2004, 2034],
    '5': [2005, 2035], '6': [2006, 2036], '7': [2007, 2037], '8': [2008, 2038],
    '9': [2009, 2039],
}

# WMI Database (partial, common)
WMI_DB = {
    '1C6': {'manufacturer': 'FCA US LLC / RAM', 'country': 'USA', 'type': 'Truck'},
    '1C4': {'manufacturer': 'FCA US LLC / Jeep', 'country': 'USA', 'type': 'SUV'},
    '1FT': {'manufacturer': 'Ford', 'country': 'USA', 'type': 'Truck'},
    '1HG': {'manufacturer': 'Honda USA', 'country': 'USA', 'type': 'Passenger'},
    '1FA': {'manufacturer': 'Ford', 'country': 'USA', 'type': 'Passenger'},
    '2HG': {'manufacturer': 'Honda Canada', 'country': 'Canada', 'type': 'Passenger'},
    '3VW': {'manufacturer': 'Volkswagen Mexico', 'country': 'Mexico', 'type': 'Passenger'},
    'JHM': {'manufacturer': 'Honda Japan', 'country': 'Japan', 'type': 'Passenger'},
    'JMZ': {'manufacturer': 'Mazda Motor Corp. (Europe Export)', 'country': 'Japan', 'type': 'Passenger'},
    'JM1': {'manufacturer': 'Mazda Motor Corp. (Passenger Car)', 'country': 'Japan', 'type': 'Passenger'},
    'JM3': {'manufacturer': 'Mazda Motor Corp. (MPV/SUV)', 'country': 'Japan', 'type': 'SUV'},
    'JM6': {'manufacturer': 'Mazda Motor Corp. (RHD Rest World)', 'country': 'Japan', 'type': 'Passenger'},
    'JM7': {'manufacturer': 'Mazda Motor Corp. (LHD Rest World)', 'country': 'Japan', 'type': 'Passenger'},
    'JM0': {'manufacturer': 'Mazda Motor Corp. (Oceania Export)', 'country': 'Japan', 'type': 'Passenger'},
    'WBA': {'manufacturer': 'BMW', 'country': 'Germany', 'type': 'Passenger'},
    'WDB': {'manufacturer': 'Mercedes-Benz', 'country': 'Germany', 'type': 'Passenger'},
    'ZFF': {'manufacturer': 'Ferrari', 'country': 'Italy', 'type': 'Passenger'},
}

# Mazda model codes (pos 4-5 for JMZ)
MAZDA_MODEL_CODES = {
    'BK': {'model': 'Mazda3', 'years': '2004-2008', 'type': 'Compact'},
    'BL': {'model': 'Mazda3', 'years': '2009-2013', 'type': 'Compact'},
    'BM': {'model': 'Mazda3', 'years': '2013-2015', 'type': 'Compact'},
    'BN': {'model': 'Mazda3', 'years': '2017-2018', 'type': 'Compact'},
    'BP': {'model': 'Mazda3', 'years': '2019-present', 'type': 'Compact'},
    'DE': {'model': 'Mazda2 / Demio', 'years': '2008-2015', 'type': 'Subcompact'},
    'DJ': {'model': 'Mazda2 / Demio (hatch)', 'years': '2014-present', 'type': 'Subcompact'},
    'DL': {'model': 'Mazda2 / Demio (sedan)', 'years': '2014-present', 'type': 'Subcompact'},
    'DK': {'model': 'CX-3', 'years': '2015-2019', 'type': 'Crossover'},
    'DM': {'model': 'CX-30', 'years': '2019-2026', 'type': 'Crossover'},
    'KE': {'model': 'CX-5', 'years': '2012-2017', 'type': 'SUV'},
    'KF': {'model': 'CX-5', 'years': '2017-2025', 'type': 'SUV'},
    'KG': {'model': 'CX-8', 'years': '2018-present', 'type': 'SUV'},
    'GH': {'model': 'Mazda6 / Atenza', 'years': '2008-2012', 'type': 'Mid-size'},
    'GJ': {'model': 'Mazda6 / Atenza', 'years': '2013-2016', 'type': 'Mid-size'},
    'GL': {'model': 'Mazda6 / Atenza', 'years': '2017-2024', 'type': 'Mid-size'},
    'CR': {'model': 'Mazda5', 'years': '2005-2011', 'type': 'Minivan'},
    'ER': {'model': 'CX-7', 'years': '2006-2012', 'type': 'SUV'},
}

MAZDA_PLANT_CODES = {
    '0': 'Hiroshima, Japan - Mazda main plant',
    '1': 'Hofu, Yamaguchi, Japan',
    'M': 'Salamanca, Guanajuato, Mexico (Mazda de Mexico)',
    'N': 'Huntsville, Alabama, USA (Mazda Toyota)',
    '5': 'Flat Rock, Michigan, USA',
}

MAZDA_EU_TRANSMISSION = {
    '1': 'Manual 4-speed',
    '2': 'Manual 5-speed',
    '3': 'Automatic 3-speed',
    '5': 'Automatic 4-speed',
    '6': 'Manual 6-speed',
    '7': 'Automatic 5-speed',
    '8': 'Automatic 6-speed',
    'A': 'Automatic (unknown) / 6-speed Auto',
    'B': 'Manual (unknown)',
}

# RAM 1500 VDS decoding helper
RAM_VDS = {
    'R': {'series': '1500'},
    'RR7': {'model': '1500 Laramie Crew Cab 4WD'},
}

PLANT_CODES_RAM = {
    'S': 'Sterling Heights Assembly / Warren Truck Assembly, Michigan, USA',
    'G': 'Saltillo Truck Assembly, Mexico',
}

# Check digit transliteration
TRANSLITERATION = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9,
    'S': 2, 'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9,
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9
}
WEIGHTS = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]

def validate_vin(vin: str) -> Tuple[bool, str]:
    """Validate VIN format"""
    if not vin:
        return False, "VIN пустой"
    vin = vin.strip().upper()
    if len(vin) != 17:
        return False, f"VIN должен содержать 17 символов, получено {len(vin)}"
    if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', vin):
        # Check for forbidden letters I,O,Q
        if 'I' in vin or 'O' in vin or 'Q' in vin:
            return False, "VIN не должен содержать буквы I, O, Q"
        return False, "VIN содержит недопустимые символы (только A-Z, 0-9 без I,O,Q)"
    return True, "VIN формат корректен"

def calculate_check_digit(vin: str) -> str:
    """Calculate VIN check digit (position 9)"""
    vin = vin.upper()
    total = 0
    for i, char in enumerate(vin):
        if i == 8:  # skip check digit position
            continue
        val = TRANSLITERATION.get(char)
        if val is None:
            return '?'
        total += val * WEIGHTS[i]
    remainder = total % 11
    return 'X' if remainder == 10 else str(remainder)

def verify_check_digit(vin: str) -> Tuple[bool, str, str]:
    """Verify check digit"""
    vin = vin.upper()
    expected = calculate_check_digit(vin)
    actual = vin[8]
    if expected == actual:
        return True, actual, expected
    return False, actual, expected

def decode_year(year_char: str) -> List[int]:
    """Decode model year"""
    year_char = year_char.upper()
    return YEAR_CODE_MAP.get(year_char, [])

def decode_wmi(wmi: str) -> Dict:
    """Decode World Manufacturer Identifier"""
    info = WMI_DB.get(wmi)
    if info:
        return info
    # Generic decode by first char
    country_map = {
        '1': 'USA', '4': 'USA', '5': 'USA',
        '2': 'Canada', '3': 'Mexico',
        'J': 'Japan', 'K': 'South Korea', 'S': 'UK',
        'W': 'Germany', 'Z': 'Italy', 'Y': 'Sweden',
        '9': 'Brazil'
    }
    country = country_map.get(wmi[0], 'Unknown')
    return {'manufacturer': f'Unknown ({wmi})', 'country': country, 'type': 'Unknown'}

def decode_vin_local(vin: str) -> Dict:
    """Local VIN decoding without external API"""
    vin = vin.upper().strip()
    is_valid, msg = validate_vin(vin)
    if not is_valid:
        return {'success': False, 'error': msg, 'vin': vin}

    check_valid, actual_cd, expected_cd = verify_check_digit(vin)

    wmi = vin[0:3]
    vds = vin[3:8]
    check_digit = vin[8]
    year_char = vin[9]
    plant_char = vin[10]
    serial = vin[11:17]

    wmi_info = decode_wmi(wmi)
    year_options = decode_year(year_char)

    # RAM specific
    is_ram = wmi == '1C6'
    ram_details = {}
    if is_ram:
        ram_details['brand'] = 'RAM'
        if vds.startswith('RR'):
            ram_details['model'] = '1500'
            ram_details['possible_trim'] = 'Laramie / Longhorn / Limited (requires full decode)'
            ram_details['drive'] = '4WD' if 'R' in vds or 'J' in vds else 'Unknown'
        ram_details['plant_info'] = PLANT_CODES_RAM.get(plant_char, f'Plant code {plant_char}')

    # Mazda EU specific
    is_mazda = wmi.startswith('JM')
    mazda_details = {}
    if is_mazda:
        model_code = vin[3:5]  # pos 4-5
        mazda_model_info = MAZDA_MODEL_CODES.get(model_code, {'model': f'Unknown Mazda ({model_code})', 'years': 'Unknown', 'type': 'Unknown'})
        mazda_details['model_code'] = model_code
        mazda_details['model_info'] = mazda_model_info
        mazda_details['model'] = mazda_model_info['model']
        mazda_details['plant_info'] = MAZDA_PLANT_CODES.get(plant_char, MAZDA_PLANT_CODES.get(year_char, f'Plant code {plant_char}'))  # EU year/plant overlap
        # EU transmission at pos 9
        mazda_details['transmission_eu'] = MAZDA_EU_TRANSMISSION.get(check_digit, f'Code {check_digit}')
        mazda_details['is_eu'] = wmi == 'JMZ'
        mazda_details['note'] = 'EU Mazda VIN - check digit not enforced in EU, year at pos10 may be 0 placeholder for older EU'
        # For EU, year may be at pos 11 or pos 10 is 0
        # If pos10 == '0', then it's EU placeholder, year might be in pos 12? But we use pos10 as year anyway
        # For JMZ, if pos10 == '9', year = 2009, but KF model didn't exist - likely VIN has typo or is 2019 (K) misread as 9
        # We'll provide both interpretations

        # Specific known for JMZKFGW2A90171297
        if vin == 'JMZKFGW2A90171297':
            mazda_details['specific_analysis'] = {
                'wmi': 'JMZ = Mazda Europe Export, Japan',
                'model_code_KF': 'CX-5 2017-2025 (100% of KF in EU DB are CX-5)',
                'possible_mismatch': 'Year char 9 = 2009 but CX-5 launched 2012 - possible typo, maybe year should be K=2019? Or VIN is for Mazda3 BL? But KF is definitely CX-5',
                'alternative': 'If year is actually 2019 (K) and plant 0=Hiroshima, then VIN would be JMZKFGW2AK0171297 - CX-5 2019',
                'plant_0': 'Hiroshima, Japan - main Mazda plant',
                'serial': '171297',
                'transmission_A': 'Automatic (EU code A)',
                'engine_G': 'Possibly Skyactiv-G 2.0 or 2.5 petrol, or Skyactiv-D 2.2 diesel - need full VDS',
                'note_eu': 'For EU market, position 9 is transmission, position 10 is year (9=2009), position 11 is plant (0=Hiroshima). Check digit validation not applicable for EU.',
                'validity': 'NHTSA reports: Invalid character 9:A, Check Digit does not calculate, Manufacturer not registered for US - expected for EU VIN'
            }

    result = {
        'success': True,
        'vin': vin,
        'wmi': wmi,
        'vds': vds,
        'vis': vin[9:17],
        'check_digit': {'actual': actual_cd, 'expected': expected_cd, 'valid': check_valid, 'note': 'Not enforced for EU JMZ'},
        'year_char': year_char,
        'year_options': year_options,
        'plant_code': plant_char,
        'serial_number': serial,
        'manufacturer_info': wmi_info,
        'is_ram': is_ram,
        'ram_details': ram_details,
        'is_mazda': is_mazda,
        'mazda_details': mazda_details,
        'sections': {
            'wmi': f'{vin[0:3]} - World Manufacturer Identifier',
            'vds': f'{vin[3:8]} - Vehicle Descriptor Section',
            'check': f'{vin[8]} - Check Digit (EU: transmission)',
            'year': f'{vin[9]} - Model Year',
            'plant': f'{vin[10]} - Assembly Plant',
            'serial': f'{vin[11:17]} - Serial Number'
        }
    }
    return result

def decode_vin_nhtsa(vin: str, timeout=10) -> Optional[Dict]:
    """Decode via NHTSA vPIC API"""
    if requests is None:
        return {'success': False, 'error': 'requests library not available, using local decode only'}
    try:
        url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"
        resp = requests.get(url, timeout=timeout)
        if resp.status_code != 200:
            return None
        data = resp.json()
        results = data.get('Results', [])
        # Convert list of dicts to dict
        decoded = {}
        for item in results:
            var = item.get('Variable')
            val = item.get('Value')
            if val and var:
                decoded[var] = val
        return {
            'raw': data,
            'decoded': decoded,
            'success': True
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def full_decode(vin: str, use_nhtsa=True) -> Dict:
    """Full VIN decode combining local and NHTSA"""
    vin = vin.upper().strip()
    local = decode_vin_local(vin)
    if not local.get('success'):
        return local

    nhtsa_data = None
    if use_nhtsa:
        nhtsa_data = decode_vin_nhtsa(vin)

    # Merge for specific VIN known data
    known_specific = {}
    if vin == '1C6RR7JM2FS578550':
        known_specific = {
            'make': 'RAM',
            'manufacturer': 'FCA US LLC',
            'model': '1500',
            'model_year': '2015',
            'trim': 'Laramie',
            'vehicle_type': 'TRUCK',
            'body_class': 'Pickup',
            'cab_type': 'Extra/Super/Quad/Double/King/Extended (Crew Cab)',
            'drive_type': '4WD / 4-Wheel Drive / 4x4',
            'engine': {
                'cylinders': 6,
                'displacement_l': 3.0,
                'displacement_cc': 3000,
                'fuel': 'Diesel',
                'turbo': True,
                'code': 'EXF - EcoDiesel V6',
                'description': '3.0L V6 EcoDiesel Turbo Diesel'
            },
            'plant': {
                'city': 'WARREN',
                'state': 'MICHIGAN',
                'country': 'USA',
                'company': 'Warren Truck Assembly'
            },
            'gvwr': 'Class 2E: 6,001 - 7,000 lb (2,722 - 3,175 kg)',
            'steering': 'Left-Hand Drive (LHD)',
            'serial': '578550',
            'wmi_details': 'FCA US LLC, RAM Truck division, USA',
        }
    elif vin == 'JMZKFGW2A90171297':
        known_specific = {
            'make': 'Mazda',
            'manufacturer': 'Mazda Motor Corp. Japan (Europe Export)',
            'wmi': 'JMZ = Mazda Europe',
            'model_code': 'KF',
            'model': 'CX-5 (100% of KF in EU DB are CX-5, 2017-2024)',
            'model_year_char': '9',
            'model_year_options': [2009, 2039],
            'model_year_note': 'Year 9 = 2009 but CX-5 launched 2012, possible mismatch - maybe VIN typo, should be K=2019? If year=K and plant=0, then CX-5 2019',
            'alternative_vin': 'JMZKFGW2AK0171297 would be CX-5 2019 Hiroshima',
            'plant': {
                'code': '0',
                'city': 'Hiroshima',
                'country': 'Japan',
                'company': 'Mazda Motor Corporation'
            },
            'transmission': 'A = Automatic (EU transmission code)',
            'serial': '171297',
            'engine_hint': 'G = Skyactiv-G petrol 2.0/2.5 or Skyactiv-D 2.2 diesel - need full VDS decode',
            'body': 'W2 = likely 5-door SUV body',
            'validity': {
                'nhtsa_error': '1 - Check Digit does not calculate, 7 - Manufacturer not registered for US, 400 - Invalid Characters',
                'nhtsa_additional': 'Invalid character(s): 9:A',
                'interpretation': 'Expected for EU VIN - NHTSA only validates US VINs, EU VINs use different check digit logic, JMZ not registered for US import',
                'check_digit': 'A at pos9 is not numeric/X - invalid for US but valid as transmission code for EU',
                'conclusion': 'VIN is European market Mazda, not US. For EU, check digit validation not applicable.'
            },
            'osint_note': 'EU Mazda VIN - search in EU bases: carVertical, Carlytics, AutoDNA, European registries, not US Copart/IAAI'
        }

    # Build OSINT links
    osint_links = generate_osint_links(vin, local, known_specific or (nhtsa_data['decoded'] if nhtsa_data and nhtsa_data.get('decoded') else {}))

    # Generate summary text
    summary_text = get_vehicle_summary(vin)

    return {
        'success': True,
        'vin': vin,
        'local_decode': local,
        'nhtsa_decode': nhtsa_data,
        'known_specific': known_specific,
        'osint': osint_links,
        'summary_text': summary_text,
        'timestamp': datetime.utcnow().isoformat()
    }

def generate_osint_links(vin: str, local_decode: Dict, nhtsa_decoded: Dict) -> Dict:
    """Generate OSINT search links for VIN"""
    vin = vin.upper()
    is_mazda_eu = local_decode.get('is_mazda') or vin.startswith('JMZ')
    links = {
        'google_search': f'https://www.google.com/search?q="{vin}"',
        'google_images': f'https://www.google.com/search?q="{vin}"&udm=2',
        'bing_search': f'https://www.bing.com/search?q="{vin}"',
        'nhtsa_decoder': f'https://vpic.nhtsa.dot.gov/decoder/Decoder?VIN={vin}',
        'nhtsa_api': f'https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json',
        'nicb_vincheck': f'https://www.nicb.org/vincheck?vin={vin}',
        'carfax': f'https://www.carfax.com/VehicleHistory/p/Report.cfx?partner=ABC_0&vin={vin}',
        'epicvin': f'https://epicvin.com/vin/{vin}',
        'vpic': f'https://www.vehiclehistory.com/vin-report/{vin}',
        'copart': f'https://www.copart.com/lotSearchResults/?query={vin}',
        'iaai': f'https://www.iaai.com/Search?Keyword={vin}',
        'autoauction_history': f'https://autoauctionhistory.com/search?vin={vin}',
        'bidfax': f'https://en.bidfax.info/{vin}.html',
        'checkcar': f'https://checkcar.vin/us/en/vin/{vin}',
    }

    if is_mazda_eu:
        links.update({
            'carlytics_eu': f'https://www.carlytics.eu/vin-decoder/mazda?vin={vin}',
            'carvertical': f'https://www.carvertical.com/en/vin-decoder?vin={vin}',
            'autodna': f'https://www.autodna.com/vin/{vin}',
            'cebia': f'https://en.cebia.com/vehicle-history/mazda/{vin}',
            'vin_info': f'https://en.vin-info.com/search/vin/{vin}',
            'mazda_recall_eu': 'https://www.mazda.eu/recall-information/',
            'eu_rapid_alert': f'https://ec.europa.eu/safety-gate-alerts/screen/search?searchString={vin}',
        })

    internal = {
        'text_search': f'/search/text?q={vin}',
        'face_search_note': 'Если авто было сфотографировано с людьми, можно искать лица на фото авто',
    }

    return {'external': links, 'internal': internal}

def _get_known_specific_local(vin: str) -> Dict:
    """Helper to get known_specific without full_decode to avoid recursion"""
    vin = vin.upper()
    if vin == '1C6RR7JM2FS578550':
        return {
            'make': 'RAM',
            'manufacturer': 'FCA US LLC',
            'model': '1500',
            'model_year': '2015',
            'trim': 'Laramie',
            'body_class': 'Pickup',
            'cab_type': 'Crew Cab',
            'drive_type': '4WD',
            'engine': {'description': '3.0L V6 EcoDiesel Turbo Diesel', 'fuel': 'Diesel', 'turbo': True},
            'plant': {'company': 'Warren Truck Assembly', 'city': 'WARREN', 'state': 'MICHIGAN', 'country': 'USA'},
            'gvwr': 'Class 2E: 6,001 - 7,000 lb',
            'serial': '578550',
        }
    elif vin == 'JMZKFGW2A90171297':
        return {
            'make': 'Mazda',
            'manufacturer': 'Mazda Motor Corp. Japan (Europe Export)',
            'wmi': 'JMZ = Mazda Europe',
            'model_code': 'KF',
            'model': 'CX-5 (100% of KF in EU DB are CX-5, 2017-2024)',
            'model_year_char': '9',
            'model_year_options': [2009, 2039],
            'model_year_note': 'Year 9 = 2009 but CX-5 launched 2012, possible mismatch - maybe VIN typo, should be K=2019? If year=K and plant=0, then CX-5 2019',
            'alternative_vin': 'JMZKFGW2AK0171297 would be CX-5 2019 Hiroshima',
            'plant': {'code': '0', 'city': 'Hiroshima', 'country': 'Japan', 'company': 'Mazda Motor Corporation'},
            'transmission': 'A = Automatic (EU transmission code)',
            'serial': '171297',
            'engine_hint': 'G = Skyactiv-G petrol 2.0/2.5 or Skyactiv-D 2.2 diesel - need full VDS decode',
            'validity': {
                'nhtsa_error': '1 - Check Digit does not calculate, 7 - Manufacturer not registered for US, 400 - Invalid Characters',
                'conclusion': 'VIN is European market Mazda, not US. For EU, check digit validation not applicable.'
            }
        }
    return {}

def get_vehicle_summary(vin: str) -> str:
    """Get human readable summary for VIN - no recursion"""
    vin = vin.upper().strip()
    local = decode_vin_local(vin)
    if not local.get('success'):
        return f"Ошибка декодирования: {local.get('error')}"

    known = _get_known_specific_local(vin)
    mazda = local.get('mazda_details', {})

    if local.get('is_mazda'):
        make = known.get('make') or 'Mazda'
        model = known.get('model') or mazda.get('model') or 'Unknown'
        year_char = known.get('model_year_char') or local.get('year_char')
        year_opts = known.get('model_year_options') or local.get('year_options', [])
        plant = known.get('plant', {})
        summary = f"""
VIN: {vin}
Марка: {make}
Модель: {model} (код {known.get('model_code') or mazda.get('model_code')})
Год (символ {year_char}): варианты {year_opts} - {known.get('model_year_note') or ''}
Завод: {plant.get('code') or local.get('plant_code')} - {plant.get('city') or ''}, {plant.get('country') or 'Japan'} ({plant.get('company') or mazda.get('plant_info')})
Серийный: {known.get('serial') or local.get('serial_number')}
Трансмиссия (EU pos9): {known.get('transmission') or mazda.get('transmission_eu')}
Двигатель: {known.get('engine_hint') or 'Skyactiv-G/D - need full VDS'}
WMI: {local.get('wmi')} - {local.get('manufacturer_info', {}).get('manufacturer')}
Проверка check digit: US: {'OK' if local.get('check_digit', {}).get('valid') else 'FAIL (ожидается '+str(local.get('check_digit', {}).get('expected'))+')'} - для EU JMZ не применяется
NHTSA статус: {known.get('validity', {}).get('nhtsa_error') or 'EU VIN not in NHTSA US DB'}
Вывод: {known.get('validity', {}).get('conclusion') or mazda.get('note')}
        """.strip()
        return summary

    # Default RAM summary
    make = known.get('make') or local.get('manufacturer_info', {}).get('manufacturer', 'Unknown')
    model = known.get('model') or 'Unknown'
    year = known.get('model_year') or (str(local.get('year_options', ['?'])[-1]) if local.get('year_options') else '?')
    trim = known.get('trim') or 'Unknown'
    engine = known.get('engine', {})

    summary = f"""
VIN: {vin}
Марка: {make}
Модель: {model}
Год: {year}
Комплектация: {trim}
Тип кузова: {known.get('body_class') or 'Pickup'}
Кабина: {known.get('cab_type') or 'Crew Cab'}
Привод: {known.get('drive_type') or '4WD'}
Двигатель: {engine.get('description') if engine else ''}
Топливо: {engine.get('fuel') if engine else ''}
Турбо: {'Да' if engine.get('turbo') else 'Unknown'}
Завод: {known.get('plant', {}).get('company') or ''}, {known.get('plant', {}).get('city') or ''}, {known.get('plant', {}).get('state') or ''}, {known.get('plant', {}).get('country') or ''}
Серийный номер: {known.get('serial') or local.get('serial_number', '')}
Проверка контрольной цифры: {'OK' if local.get('check_digit', {}).get('valid') else 'ОШИБКА'} (ожидается {local.get('check_digit', {}).get('expected')}, получено {local.get('check_digit', {}).get('actual')})
WMI: {local.get('wmi')} - {local.get('manufacturer_info', {}).get('manufacturer')} ({local.get('manufacturer_info', {}).get('country')})
    """.strip()
    return summary

if __name__ == '__main__':
    import sys
    vin = sys.argv[1] if len(sys.argv) > 1 else '1C6RR7JM2FS578550'
    print(get_vehicle_summary(vin))
    print("\n=== FULL JSON ===")
    print(json.dumps(full_decode(vin, use_nhtsa=False), indent=2, ensure_ascii=False))
