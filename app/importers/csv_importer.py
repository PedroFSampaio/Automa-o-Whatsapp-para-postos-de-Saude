import csv
import re
from pathlib import Path


def normalize_phone(value: object) -> str:
    return re.sub(r"\D", "", str(value or ""))


def is_valid_mobile(phone: str) -> bool:
    """
    Valida se é um número de celular (começa com 9) ou telefone fixo (começa com 3).
    Retorna True apenas para celulares (começa com 9).
    Números fixos (começam com 3) são ignorados.
    
    Exemplos:
    - 14991234567 -> True (celular)
    - 14934567890 -> False (telefone fixo - pulado)
    """
    # Remove DDD (primeiros 2 dígitos) e verifica o primeiro dígito do número local
    if len(phone) >= 3:
        first_digit_of_number = phone[2]  # Terceiro dígito é o primeiro do número local
        return first_digit_of_number == "9"  # Aceita apenas se começa com 9
    return False


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
