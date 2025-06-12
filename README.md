# Demerzel Project

This repository contains a small Flask application with a frontend that allows filling out RPG character sheets. Character data is written to PDFs by a Node.js script executed from the `/save-character` endpoint.

## Requirements

* Python 3 with the packages from `requirements.txt` (install with `pip install -r requirements.txt`)
* Node.js (v18 or later is recommended)
* The Node package `pdf-lib` used by `fill_pdf.js`

Install the Node dependency by running:

```bash
npm install pdf-lib
```

The `/save-character` feature relies on this package. Be sure to run the above
command before trying to save a character or the PDF generation will fail.

## Running

1. Ensure the `node` command is available and the `pdf-lib` package is installed as shown above.
2. Install the Python dependencies: `pip install -r requirements.txt`.
3. Start the Flask app:

```bash
python app.py
```

The `/save-character` endpoint expects a JSON payload with `name`, `template` and `fieldData`. The Node script `fill_pdf.js` fills the specified PDF template with the provided form data and writes the resulting PDF to `/mnt/data/<name>.pdf`.
