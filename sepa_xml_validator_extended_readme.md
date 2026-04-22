# SEPA XML Validator (Erweitert)

## Erweiterter Python-Code

```python
import sys
import re
from pathlib import Path
from datetime import datetime

try:
    from lxml import etree
except ImportError:
    print("pip install lxml"); sys.exit(1)

IBAN_PATTERN = re.compile(r'^[A-Z]{2}\d{2}[A-Z0-9]{4,30}$')
BIC_PATTERN = re.compile(r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$')

SEPA_NS = {
    'pain': 'urn:iso:std:iso:20022:tech:xsd:pain.001.003.03'
}

def validate_iban(iban: str) -> bool:
    clean = iban.replace(' ', '').upper()
    return bool(IBAN_PATTERN.match(clean))

def validate_bic(bic: str) -> bool:
    return bool(BIC_PATTERN.match(bic))

def validate_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except Exception:
        return False

def validate_sepa_file(filepath: str) -> dict:
    results = {'file': filepath, 'errors': [], 'warnings': [], 'stats': {}}
    
    try:
        tree = etree.parse(filepath)
        root = tree.getroot()
    except etree.XMLSyntaxError as e:
        results['errors'].append(f'XML-Syntaxfehler: {e}')
        return results

    results['stats']['root_tag'] = root.tag

    iban_count, iban_errors = 0, 0
    bic_errors = 0
    date_errors = 0
    currency_errors = 0
    
    total_amount = 0
    transaction_count = 0

    for elem in root.iter():
        tag = etree.QName(elem).localname

        # IBAN
        if tag == 'IBAN' and elem.text:
            iban_count += 1
            if not validate_iban(elem.text):
                iban_errors += 1
                results['errors'].append(f'Ungültige IBAN: {elem.text}')

        # BIC
        if tag == 'BIC' and elem.text:
            if not validate_bic(elem.text):
                bic_errors += 1
                results['errors'].append(f'Ungültiger BIC: {elem.text}')

        # Betrag
        if tag in ['InstdAmt', 'Amt'] and elem.text:
            transaction_count += 1
            try:
                amt = float(elem.text)
                total_amount += amt
                if amt <= 0:
                    results['warnings'].append(f'Betrag ≤ 0: {amt}')
            except ValueError:
                results['errors'].append(f'Ungültiger Betrag: {elem.text}')

            # Currency prüfen
            if 'Ccy' in elem.attrib:
                if elem.attrib['Ccy'] != 'EUR':
                    currency_errors += 1
                    results['warnings'].append(f'Nicht-EUR Währung: {elem.attrib["Ccy"]}')

        # Datum
        if tag in ['ReqdExctnDt', 'CreDtTm'] and elem.text:
            if not validate_date(elem.text[:10]):
                date_errors += 1
                results['errors'].append(f'Ungültiges Datum: {elem.text}')

    results['stats'].update({
        'ibans_found': iban_count,
        'iban_errors': iban_errors,
        'bic_errors': bic_errors,
        'date_errors': date_errors,
        'currency_warnings': currency_errors,
        'transactions': transaction_count,
        'total_amount': total_amount
    })

    return results


def print_report(results: dict):
    print("\n" + "="*50)
    print("SEPA XML Validierungsbericht")
    print("="*50)
    print(f"Datei: {results['file']}")
    print(f"Root-Element: {results['stats'].get('root_tag')}")
    print(f"Transaktionen: {results['stats'].get('transactions')}")
    print(f"Gesamtbetrag: {results['stats'].get('total_amount'):.2f} EUR")

    print("\n--- Statistik ---")
    for k, v in results['stats'].items():
        print(f"{k}: {v}")

    if results['errors']:
        print(f"\n❌ Fehler ({len(results['errors'])}):")
        for e in results['errors']:
            print(f"  • {e}")

    if results['warnings']:
        print(f"\n⚠️ Warnungen ({len(results['warnings'])}):")
        for w in results['warnings']:
            print(f"  • {w}")

    if not results['errors']:
        print("\n✅ Datei ist gültig (keine Fehler)")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python validator.py <file.xml>")
        sys.exit(1)

    results = validate_sepa_file(sys.argv[1])
    print_report(results)
```

---

# README.md

## Überblick

Dieses Projekt ist ein einfacher, aber erweiterbarer SEPA XML Validator für Dateien wie:

- pain.001 (Überweisungen)
- camt.053 (Kontoauszüge – eingeschränkt unterstützt)

Das Ziel ist es, typische Fehler in SEPA-Dateien frühzeitig zu erkennen.

---

## Features

Der Validator prüft:

### 1. XML-Struktur
- Ob die Datei gültiges XML ist
- Fehlerhafte Syntax wird direkt erkannt

### 2. IBAN Validierung
- Prüft Format (Regex-basiert)
- Erkennt ungültige oder fehlerhafte IBANs

### 3. BIC Validierung
- Prüft Struktur eines BIC Codes
- Optional (nicht immer in SEPA Pflicht)

### 4. Beträge
- Prüft, ob Beträge numerisch sind
- Warnt bei:
  - 0 oder negativen Beträgen

### 5. Währung
- Prüft Attribut `Ccy`
- Warnt bei Nicht-EUR

### 6. Datum
- Prüft Datumsfelder wie:
  - ReqdExctnDt
  - CreDtTm
- Erwartetes Format: YYYY-MM-DD

### 7. Statistiken
- Anzahl Transaktionen
- Gesamtbetrag
- Anzahl IBANs
- Fehler & Warnungen

---

## Verwendung

```bash
python validator.py beispiel.xml
```

---

## Beispiel-Ausgabe

```
==================================================
SEPA XML Validierungsbericht
==================================================
Datei: payment.xml
Transaktionen: 5
Gesamtbetrag: 1200.00 EUR

❌ Fehler (1):
  • Ungültige IBAN: XX123

⚠️ Warnungen (1):
  • Betrag ≤ 0: 0
```

---

## Grenzen des Validators

Dieser Validator ist **kein vollständiger ISO 20022 Validator**.

Was NICHT geprüft wird:
- XSD Schema Validierung
- Business Rules der Banken
- Duplicate Transactions
- Mandate (bei Lastschrift)

---

## Erweiterungsmöglichkeiten

Du kannst den Validator erweitern um:

- XSD Validierung (offizielle SEPA Schemas)
- Duplicate Detection
- Logging in Dateien
- Web API (Flask/FastAPI)
- GUI Oberfläche

---

## Fazit

Dieses Tool ist ideal für:

- Entwickler
- FinTech Projekte
- Test von SEPA Exporten

Es ist leichtgewichtig, verständlich und gut erweiterbar.

