# SEPA XML Validator
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

Dieses Tool ist ideal für:

- Entwickler
- FinTech Projekte
- Test von SEPA Exporten

Es ist leichtgewichtig, verständlich und gut erweiterbar.
