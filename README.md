# pdf-redaction
Python class that detects and redacts PII (personally identifiable information) in PDF files, replacing sensitive data with labeled placeholders

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Download the spaCy transformer model:
```bash
python -m spacy download en_core_web_trf
```

## Usage

Run the redaction tool on your PDF:
```bash
python redaction.py input.pdf -o output.pdf
```

### Example:
```bash
python redaction.py sample1.pdf -o redacted_sample1.pdf
```

## Sample Files

This repository includes 2 sample PDFs for testing:
- `sample1.pdf` - Contains various PII types for testing
- `sample2.pdf` - Additional test cases

## Detected PII Types

The tool automatically detects and redacts:
- **NRIC/FIN numbers** (e.g., S1234567A)
- **Phone numbers** (8-digit and international formats)
- **Email addresses**
- **Person names** (using NER)
- **Addresses** (using NER)
- **IP addresses** (IPv4 and IPv6)
- **Credit card numbers** (16 digits, spaced or unspaced)

## Output

Sensitive information will be replaced with labeled placeholders:
- `[NAME REDACTED]`
- `[EMAIL REDACTED]`
- `[PHONE REDACTED]`
- `[NRIC REDACTED]`
- etc.

