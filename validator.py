import sys
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
