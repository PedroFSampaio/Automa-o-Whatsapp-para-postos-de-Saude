import csv
import re
from pathlib import Path


def normalize_phone(value: object) -> str:
    if isinstance(value, float) and value.is_integer():
        value = int(value)

    digits = re.sub(r"\D", "", str(value or ""))
    if digits.startswith("00"):
        digits = digits[2:]
    if len(digits) in (12, 14) and digits.startswith("0"):
        digits = digits[1:]
    if len(digits) in (10, 11):
        digits = f"55{digits}"
    return digits


def is_valid_mobile(phone: str) -> bool:
    """
    Valida um celular brasileiro no formato DDI + DDD + numero.

    Exemplos:
    - 5514991234567 -> True (celular)
    - 551433331234 -> False (telefone fixo)
    """
    digits = re.sub(r"\D", "", str(phone or ""))
    if len(digits) == 13 and digits.startswith("55"):
        national_number = digits[2:]
    elif len(digits) == 11:
        national_number = digits
    else:
        return False

    ddd = national_number[:2]
    return ddd.isdigit() and 11 <= int(ddd) <= 99 and national_number[2] == "9"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        sample = file.read(2048)
        file.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        rows = csv.DictReader(file, dialect=dialect)
        return _clean_rows(rows)


def _clean_rows(rows: object) -> list[dict[str, str]]:
    contacts = []
    for row in rows:
        normalized = {str(key or "").strip().lower(): str(value or "").strip() for key, value in row.items()}
        name = normalized.get("nome", normalized.get("name", normalized.get("nome paciente", "")))
        phone = normalize_phone(normalized.get("telefone", normalized.get("phone", normalized.get("numero", ""))))
        message = normalized.get("mensagem", normalized.get("message", ""))
        # Validar: apenas celulares (que começam com 9)
        if phone and is_valid_mobile(phone):
            contact = {"name": name, "phone": phone, "status": "Pendente"}
            if message:
                contact["message"] = message
            contacts.append(contact)
    return contacts
