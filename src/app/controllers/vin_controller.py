#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.vin_decoder import full_decode, validate_vin, get_vehicle_summary, decode_vin_local
from flask import g
import traceback

class VinController:
    """VIN search controller for EyeOfWeb"""

    @staticmethod
    def search_by_vin(vin: str, use_nhtsa: bool = True):
        """Search vehicle by VIN"""
        if not vin:
            return False, "VIN код обязателен", None

        vin = vin.strip().upper()

        # Validate
        is_valid, msg = validate_vin(vin)
        if not is_valid:
            return False, f"Неверный VIN: {msg}", None

        try:
            result = full_decode(vin, use_nhtsa=use_nhtsa)
            if not result.get('success'):
                return False, result.get('error', 'Ошибка декодирования'), None

            # Try to find related images in DB that mention VIN in title or domain?
            related_images = []
            try:
                # Search in ImageTitleID for VIN mentions
                query = """
                SELECT i."ImageID", t."Title" as image_title, bd."Domain" as domain,
                       ip."Path" as image_path, id."Domain" as image_domain,
                       i."DetectionDate", i."RiskLevel"
                FROM "ImageBasedMain" i
                JOIN "ImageTitleID" t ON i."ImageTitleID" = t."ID"
                JOIN "BaseDomainID" bd ON i."BaseDomainID" = bd."ID"
                LEFT JOIN "BaseDomainID" id ON i."ImageDomainID" = id."ID"
                LEFT JOIN "ImageUrlPathID" ip ON i."ImagePathID" = ip."ID"
                WHERE LOWER(t."Title") LIKE %s
                LIMIT 20
                """
                # Use g.db_tools if available
                try:
                    search_results = g.db_tools.executeQuery(query, [f'%{vin.lower()}%'])
                    if search_results:
                        related_images = search_results
                except Exception as db_err:
                    print(f"[VIN Controller] DB search error: {db_err}")
                    related_images = []
            except Exception as e:
                print(f"[VIN Controller] related images error: {e}")
                traceback.print_exc()

            result['related_images'] = related_images
            result['summary_text'] = get_vehicle_summary(vin)

            return True, f"VIN {vin} успешно декодирован", result

        except Exception as e:
            print(f"[VIN Controller] Exception: {e}")
            traceback.print_exc()
            return False, f"Ошибка при поиске VIN: {str(e)}", None

    @staticmethod
    def quick_decode(vin: str):
        """Quick local decode without DB"""
        vin = vin.strip().upper()
        is_valid, msg = validate_vin(vin)
        if not is_valid:
            return False, msg, None
        try:
            local = decode_vin_local(vin)
            return True, "Декодирование успешно", local
        except Exception as e:
            return False, str(e), None
