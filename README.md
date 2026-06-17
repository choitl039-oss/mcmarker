### Generating a Layout Automatically

For convenience there's a simple script in `scripts/create_layout.py` that
lets you draw bounding boxes over the blank PDF and then assign them to
questions/choices.  Example usage:

```powershell
# put your blank form in the project directory
python -m scripts.create_layout --pdf MC-blank.pdf --output layout.json
```

The script will display the first page of the PDF in a window; click and
drag to draw a rectangle around each bubble, then press **q** when you're
done.  After closing the window you'll be prompted for the question number
and choice label for each rectangle.  A JSON file suitable for passing to
``grade_mc.py --layout`` will be created.

The helper is intentionally minimal; you can also create layout files
manually if you prefer to measure coordinates in an image editor.
# MC Marker

This project reads scanned multiple choice answer sheets (PDF), grades them, and generates performance reports in Excel.

## Deployment Notes

This is a Python Streamlit app, not a static website.

- If you deploy with GitHub Pages, you will not get the app UI.
- GitHub Pages hosts static files and may show repository content or docs instead.
- Deploy this project using a Python app host such as Streamlit Community Cloud, Render, or Railway.

### Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Go to share.streamlit.io and connect your GitHub account.
3. Select this repository and set the main file to app_streamlit.py.
4. Deploy.

If deployment fails with missing system packages, check the Streamlit Cloud logs first. The repo only needs the minimal packages in [packages.txt](packages.txt): `tesseract-ocr` and `poppler-utils`.

## Requirements
- Python 3.8+
- Tesseract OCR installed

## Setup
```sh
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Poppler (required for PDF conversion)

On Windows `pdf2image` depends on the Poppler command‑line utilities
(`pdftoppm`, `pdfinfo`).  Install Poppler separately and add its `bin`
folder to your `PATH`.  With chocolatey you can run:

```powershell
choco install poppler
```

If Poppler is missing you will see errors like
"Unable to get page count. Is poppler installed and in PATH?" when
running `create_layout.py` or grading a PDF.

## Usage
```sh
python -m src.grade_mc --input sheets.pdf --key answer_key.json --output report.xlsx
```

## Answer Key Format

The answer key file should be a simple JSON object mapping question numbers (as strings) to the correct choice letter:

```json
{
	"1": "A",
	"2": "C",
	"3": "B",
	...
}
```

The detection routine is a placeholder and will need adjustment to match the layout of your specific scan form. See `src/grade_mc.py` comments for guidance.

## Template & Layout JSON

You can export or scan a **blank** version of your MC sheet and use it to
create a layout description.  A layout is just a JSON mapping each
question to its bubble coordinates on the page.  For example::

```json
{
	"1": {"A": [100,200,30,30], "B": [140,200,30,30], "C": [180,200,30,30], "D": [220,200,30,30]},
	"2": {"A": [100,240,30,30], "B": [140,240,30,30], "C": [180,240,30,30], "D": [220,240,30,30]},
	...
}
```

Coordinates are pixel values relative to the top-left corner of the
rendered PDF page (dpi‑dependent).  Use any image editor to inspect the
template and record the bounding box of each bubble.  Once you have a
layout file you can pass it to the CLI with `--layout layout.json`.

The script will then examine each region and pick the darkest bubble as
the student's answer.  This is far more reliable than the automatic
contour heuristic and is recommended for real use.
