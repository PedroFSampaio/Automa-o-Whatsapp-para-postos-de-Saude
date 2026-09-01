import re
from pathlib import Path

from .csv_importer import normalize_phone, is_valid_mobile


APPOINTMENT_RE = re.compile(r"(?m)^\s*(\d{2}:\d{2})\s+(.+?)\s*$")
PHONE_RE = re.compile(r"\(\d{2}\)\s*[\d\s-]+")
AGE_RE = re.compile(r"\d+\s+anos?\s+e\s+\d+\s+(?:m[eê]s|dias)", re.IGNORECASE)
DATE_RE = re.compile(r"Data[:\s]+(\d{2}/\d{2}/\d{4})", re.IGNORECASE)


def read_pdf(path: Path) -> list[dict[str, str]]:
    try:
        from pypdf import PdfReader
    except ImportError as error:
        raise RuntimeError("Para importar PDF, instale as dependencias com: pip install -r requirements.txt") from error

    text = "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
    return parse_agenda_text(text)


def parse_agenda_text(text: str) -> list[dict[str, str]]:
    # Extract date from document
    date_match = DATE_RE.search(text)
    consultation_date = date_match.group(1) if date_match else ""
    
    appointments = list(APPOINTMENT_RE.finditer(text))
    contacts: list[dict[str, str]] = []
    
    for index, appointment in enumerate(appointments):
        # Get text block from this appointment to the next
        block_start = appointment.end()
        block_end = appointments[index + 1].start() if index + 1 < len(appointments) else len(text)
        block = text[block_start:block_end]
        
        # Extract name (just the appointment group)
        name = appointment.group(2).strip()
        if not name or name.upper() == "DEMANDA":
            continue
        
        # Extract time
        time_slot = appointment.group(1)
        
        # Extract all phone numbers in this block
        phones = []
        for phone_match in PHONE_RE.finditer(block):
            phone = normalize_phone(phone_match.group())
            # Validar: apenas celulares (que começam com 9)
            if len(phone) >= 10 and is_valid_mobile(phone) and phone not in phones:
                phones.append(phone)
        
        # If no phones found, skip this entry
        if not phones:
            continue
        
        # Create one contact per phone number
        for phone in phones:
            contact = {"name": name, "phone": phone, "status": "Pendente"}
            if consultation_date:
                contact["data"] = consultation_date
            if time_slot:
                contact["horario"] = time_slot
            contacts.append(contact)
    
    return contacts
