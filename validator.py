"""SEPA XML Validator - Validates SEPA payment files (pain.001, camt.053)."""
import sys, re
from pathlib import Path

try:
    from lxml import etree
except ImportError:
    print("pip install lxml"); sys.exit(1)

IBAN_PATTERN = re.compile(r'^[A-Z]{2}\d{2}[A-Z0-9]{4,30}$')
SEPA_NS = {'pain': 'urn:iso:std:iso:20022:tech:xsd:pain.001.003.03'}

def validate_iban(iban: str) -> bool:
    clean = iban.replace(' ', '').upper()
    return bool(IBAN_PATTERN.match(clean))

def validate_sepa_file(filepath: str) -> dict:
    results = {'file': filepath, 'errors': [], 'warnings': [], 'stats': {}}
    
    try:
        tree = etree.parse(filepath)
        root = tree.getroot()
    except etree.XMLSyntaxError as e:
        results['errors'].append(f'XML-Syntaxfehler: {e}')
        return results
    
    results['stats']['root_tag'] = root.tag
    
    # Find all IBANs
    ibans = root.iter()
    iban_count, iban_errors = 0, 0
    for elem in root.iter():
        if 'IBAN' in elem.tag and elem.text:
            iban_count += 1
            if not validate_iban(elem.text):
                iban_errors += 1
                results['errors'].append(f'Ungültige IBAN: {elem.text}')
    
    results['stats']['ibans_found'] = iban_count
    results['stats']['iban_errors'] = iban_errors
    
    # Check amounts
    total_amounts = []
    for elem in root.iter():
        if 'Amt' in elem.tag or 'InstdAmt' in elem.tag:
            try:
                amt = float(elem.text)
                total_amounts.append(amt)
                if amt <= 0:
                    results['warnings'].append(f'Betrag ≤ 0: {amt}')
            except (ValueError, TypeError):
                pass
    
    results['stats']['transactions'] = len(total_amounts)
    results['stats']['total_amount'] = sum(total_amounts)
    
    return results

def print_report(results: dict):
    print(f"\n{'='*50}")
    print(f"SEPA XML Validierungsbericht")
    print(f"{'='*50}")
    print(f"Datei: {results['file']}")
    print(f"Root-Element: {results['stats'].get('root_tag', 'N/A')}")
    print(f"Transaktionen: {results['stats'].get('transactions', 0)}")
    print(f"Gesamtbetrag: {results['stats'].get('total_amount', 0):,.2f} EUR")
    print(f"IBANs geprüft: {results['stats'].get('ibans_found', 0)}")
    
    if results['errors']:
        print(f"\n❌ {len(results['errors'])} Fehler:")
        for e in results['errors']:
            print(f"   • {e}")
    if results['warnings']:
        print(f"\n⚠️ {len(results['warnings'])} Warnungen:")
        for w in results['warnings']:
            print(f"   • {w}")
    if not results['errors'] and not results['warnings']:
        print("\n✅ Keine Fehler gefunden!")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Verwendung: python validator.py <sepa_file.xml>")
        sys.exit(1)
    results = validate_sepa_file(sys.argv[1])
    print_report(results)
