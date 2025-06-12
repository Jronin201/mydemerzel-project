const fs = require('fs');
const path = require('path');
const { PDFDocument } = require('pdf-lib');

async function main() {
  const [template, name] = process.argv.slice(2);
  if (!template || !name) {
    console.error('Usage: node fill_pdf.js <template> <name>');
    process.exit(1);
  }

  // The template name is validated by the Flask application, so we simply
  // resolve it within the bundled pdfs directory.
  // Allow template to be passed either as "dwarf.pdf" or "pdfs/dwarf.pdf".
  const templateName = template.startsWith('pdfs' + path.sep)
    ? template.slice(5)
    : template;
  const templatePath = path.join(__dirname, 'static', 'pdfjs', 'web', 'pdfs', templateName);
  const dataPath = path.join('/mnt/data', `${name}_fields.json`);
  const outputPath = path.join('/mnt/data', `${name}.pdf`);

  try {
    const fieldData = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    const pdfBytes = fs.readFileSync(templatePath);
    const pdfDoc = await PDFDocument.load(pdfBytes);
    const form = pdfDoc.getForm();

    for (const [key, value] of Object.entries(fieldData)) {
      let field;
      try {
        field = form.getField(key);
      } catch (err) {
        continue; // Skip missing fields
      }
      if (field.setText) {
        field.setText(String(value));
      } else if (field.select) {
        field.select(String(value));
      } else if (field.check) {
        if (value === true || value === 'Yes' || value === 'On') {
          field.check();
        } else {
          field.uncheck();
        }
      }
    }

    form.flatten();
    const outBytes = await pdfDoc.save();
    fs.writeFileSync(outputPath, outBytes);
  } catch (err) {
    console.error(err.message || err);
    process.exit(1);
  }
}

main();
