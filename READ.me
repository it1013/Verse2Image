# Bible Verse Image Generator

A Python command-line application that extracts Bible verse text from an `nwt_S.epub` EPUB file and renders the requested passage as one or more styled **1920×1080 PNG images**.

The application accepts Bible references such as:

* `2 Samuel 21:3-6`
* `[2 Samuel 21:3-6]`
* `John 3:16`

It locates the appropriate book and chapter inside the EPUB, extracts the requested verses, formats the verse numbers, wraps the text into image-sized blocks, automatically determines an appropriate font size, and generates PNG images.

---

## Features

* Extracts Bible verses directly from an NWT EPUB.
* Supports Only Spanish, single verses and verse ranges.
* Supports Bible book names and EPUB abbreviations.
* Can run directly with Python or inside Docker.

---

## Requirements
### Python
The application requires Python 3 and the following packages:

```text
ebooklib
beautifulsoup4
Pillow
```

Install the dependencies with:

```bash
pip install ebooklib beautifulsoup4 Pillow
```

The project also uses a local `config.py` module for application configuration.

---

## Project Structure

A typical project directory can look like:

```text
.
├── verse2image.py
├── config.py
├── config.ini
├── nwt_S.epub
├── verse_images/
└── README.md
```

### Files

| File / Directory | Purpose                               |
| ---------------- | ------------------------------------- |
| `verse2image.py` | Main application                      |
| `config.py`      | Loads application configuration       |
| `config.ini`     | Runtime/image configuration           |
| `nwt_S.epub`     | Source EPUB containing the Bible text |
| `verse_images/`  | Generated PNG images                  |
| `README.md`      | Project documentation                 |

---

# Usage

## Basic Usage

Run the application by supplying a Bible reference:

```bash
python verse2image.py "2 Samuel 21:3-6"
```

A single verse can also be supplied:

```bash
python verse2image.py "John 3:16"
```

Brackets around the reference are supported:

```bash
python verse2image.py "[2 Samuel 21:3-6]"
```

The application removes surrounding brackets before parsing the reference.

---

## Specify the EPUB

The EPUB can be explicitly supplied with `--epub`:

```bash
python verse2image.py "John 3:16" \
    --epub nwt_S.epub
```

---

## Specify the Output Directory

Use `--output-dir` to control where generated images are saved:

```bash
python verse2image.py "John 3:16" \
    --epub nwt_S.epub \
    --output-dir verse_images
```

If the output directory does not exist, the application creates it automatically.

---

## Debug Mode

Use `--debug` to display detailed information about the extraction and image-generation process:

```bash
python verse2image.py "2 Samuel 21:3-6" \
    --debug
```

Debug mode can show information such as:

* Parsed book and chapter
* Requested verse range
* EPUB navigation resolution
* EPUB items being checked
* Located chapter file
* Detected verse markers
* Extracted verse text
* Text blocks created for images
* Font sizes being tested
* Image dimensions
* Generated output files

This is particularly useful when working with a different EPUB structure or troubleshooting a reference that cannot be located.

---

# Bible Reference Format

The application expects references in the following general format:

```text
BOOK CHAPTER:VERSE
```

or:

```text
BOOK CHAPTER:START-END
```

Examples:

```text
John 3:16
```

```text
2 Samuel 21:3-6
```

```text
3 John 1:1-14
```

Surrounding brackets are also accepted:

```text
[1 Kings 18:30-39]
```

The parser returns the reference as:

```python
{
    "book": "2 Samuel",
    "chapter": 21,
    "start_verse": 3,
    "end_verse": 6
}
```

If only one verse is supplied, the start and end verse are the same.

For example:

```text
John 3:16
```

becomes:

```python
{
    "book": "John",
    "chapter": 3,
    "start_verse": 16,
    "end_verse": 16
}
```

The parser validates that the ending verse is not lower than the starting verse.

---

# How It Works

The application is divided into six primary sections.

## 1. Configuration / Imports

The first section imports the libraries required to:

* Parse command-line arguments
* Process regular expressions
* Work with files and paths
* Decode HTML entities
* Read EPUB files
* Parse HTML with BeautifulSoup
* Generate images with Pillow
* Load application settings

The application loads its configuration through:

```python
config = Config()
```

The configuration controls settings such as:

* EPUB path
* Output directory
* Image dimensions
* Margins
* Font sizes
* Font candidates
* Line spacing
* Background color
* Text colors
* Citation positioning
* Text wrapping
* Centering
* Block separators

---

## 2. Parse the Reference String

The `parse_reference()` function converts the supplied Bible reference into structured data.

For example:

```text
2 Samuel 21:3-6
```

is converted into:

```python
{
    "book": "2 Samuel",
    "chapter": 21,
    "start_verse": 3,
    "end_verse": 6
}
```

The function:

1. Removes surrounding whitespace.
2. Removes surrounding `[]`, `()`, or quotation marks.
3. Identifies the book name.
4. Identifies the chapter.
5. Identifies the starting verse.
6. Identifies the optional ending verse.
7. Validates the verse range.

Invalid references generate a `ValueError`.

---

# 3. HTML → Text Helpers

The EPUB contains XHTML/HTML rather than plain text.

The application therefore provides several helper functions for converting the EPUB content into usable text.

### `strip_tags()`

Removes HTML tags while preserving useful paragraph boundaries.

Block-level closing tags such as:

```html
</p>
</div>
<section>
```

are converted into newline characters before the remaining HTML tags are removed.

### `decode_entities()`

Decodes HTML entities.

For example:

```text
&amp;
```

becomes:

```text
&
```

and:

```text
&#8212;
```

becomes:

```text
—
```

### `clean_text()`

Performs the complete cleanup process:

1. Strip HTML tags.
2. Decode HTML entities.
3. Normalize whitespace.
4. Collapse excessive blank lines.
5. Remove leading/trailing whitespace.

### `element_text()`

Converts a BeautifulSoup element into cleaned text while preserving paragraph boundaries.

### `get_verse_markers()`

Searches the HTML for elements identifying verse numbers.

The application supports several possible EPUB structures, including verse classes and IDs.

### `_try_verse_num()`

Attempts to determine the numerical value represented by a verse marker.

---

# 4. Locate & Extract Verses from the EPUB

This is the primary EPUB-processing section.

The application uses `ebooklib` to open the EPUB:

```python
doc = epub.read_epub(epub_path, options={"ignore_ncx": True})
```

It then resolves the requested book and chapter through the EPUB's navigation structure.

## EPUB Navigation

The application can navigate through an EPUB structure similar to:

```text
biblebooknav.xhtml
       │
       ├── 2 Sam.
       │
       └── biblechapternav10.xhtml
                    │
                    └── 21
                         │
                         └── chapter XHTML
```

The process is:

1. Locate the Bible book navigation page.
2. Match the requested Bible book.
3. Resolve the book's chapter-navigation page.
4. Locate the requested chapter.
5. Resolve the actual XHTML chapter file.
6. Locate the verse markers.
7. Extract only the requested verse range.

---

## Bible Book Mapping

Because the EPUB may use abbreviated book names, the application contains a book mapping.

For example:

```text
2 Samuel → 2 sam.
1 Kings  → 1 rey.
John     → juan
Romans   → rom.
```

This allows a user to enter a full Bible book name while the application searches for the abbreviation used by the EPUB.

The mapping includes both Hebrew and Greek Scripture books.

---

## EPUB Item Resolution

`find_epub_item()` resolves navigation links to the actual EPUB item.

It handles differences such as:

```text
biblechapternav10.xhtml
```

and:

```text
OEBPS/biblechapternav10.xhtml
```

It also normalizes:

* URL fragments
* Leading `./`
* Leading `/`
* Windows path separators
* EPUB directory paths

---

## Verse Extraction

`extract_verses_from_item()` locates verse markers such as:

```text
chapter21_verse1
chapter21_verse2
chapter21_verse3
```

The application then extracts the text belonging to each requested verse.

Elements that are not part of the displayed verse text are excluded, including:

* Navigation elements
* Page numbers
* Footnotes
* Footnote references
* Verse-number `<sup>` elements

The selected verses are then combined into a continuous string.

Verse numbers are converted to Unicode superscripts.

For example:

```text
3 David...
4 Los gabaonitas...
5 Ellos...
```

becomes conceptually:

```text
³ David...
⁴ Los gabaonitas...
⁵ Ellos...
```

---

## Verse Not Found

If the requested EPUB, chapter, or verse cannot be located, the application raises `VerseNotFoundError`.

The command-line application reports:

```text
verse not found
```

Possible causes include:

* EPUB file does not exist.
* Bible book cannot be located.
* Chapter cannot be located.
* Verse markers are missing.
* Requested verse range does not exist.
* EPUB structure differs from the expected NWT structure.

---

# 5. Text Wrapping & Image Generation

After the verse text has been extracted, it is passed to the image-generation pipeline.

The generated images are:

```text
1920 × 1080
```

## Image Design

The default visual design is based on the configuration loaded by the application.

The source code defines a design using:

* Dark background
* Light verse text
* Highlighted verse numbers
* Citation near the bottom of the image
* Configurable serif font
* Text shadow
* Centered text

The image colors and positioning are configurable rather than hard-coded into the image-generation workflow.

---

## Text Wrapping

`parse_verse_blocks()` converts the extracted verse text into lines based on the configured line length.

For example, a long verse passage is broken into multiple lines:

```text
³ Los primeros habitantes que regresaron a sus
propiedades en sus ciudades fueron algunos
israelitas, los sacerdotes, los levitas...
```

The lines are then grouped into image-sized blocks.

The maximum number of lines per image is configurable.

If the passage is too long for one image, additional images are automatically created.

---

## Automatic Font Sizing

`auto_fit_font()` determines the largest font size that will fit all generated blocks.

The function:

1. Determines the available image width.
2. Determines the available image height.
3. Starts at the configured font size.
4. Measures each text block.
5. Checks width and height.
6. Decreases the font size when necessary.
7. Selects the largest size that fits.

This allows short passages to use a larger font while longer passages can automatically scale down.

---

## Image Rendering

`render_pages()` creates one Pillow image for each text block.

Each image:

1. Creates a 1920×1080 canvas.
2. Applies the configured background color.
3. Positions each line.
4. Centers the text when configured.
5. Applies a text shadow.
6. Renders the verse text.
7. Adds the Bible citation.
8. Returns the generated Pillow image.

---

## Generated Files

The output filename is based on the Bible citation.

For example:

```text
2 Samuel 21:3-6
```

may produce:

```text
2_Samuel_21:3–6.png
```

For passages requiring multiple images, numbered files are generated:

```text
2_Samuel_21:3–6_00.png
2_Samuel_21:3–6_01.png
2_Samuel_21:3–6_02.png
```

The exact filename is sanitized to remove characters that are unsafe for filesystem filenames.

---

# 6. Main

The `main()` function provides the command-line interface.

The available arguments are:

```text
reference
--epub
--output-dir
--debug
```

Run:

```bash
python verse2image.py --help
```

to see the available command-line options.

### Reference

Required Bible reference:

```bash
python verse2image.py "John 3:16"
```

### `--epub`

Specifies the source EPUB:

```bash
--epub nwt_S.epub
```

### `--output-dir`

Specifies where generated PNG files are saved:

```bash
--output-dir verse_images
```

### `--debug`

Enables detailed diagnostic output:

```bash
--debug
```

---

# Complete Examples

## Example 1 — Verse Range

```bash
python verse2image.py "2 Samuel 21:3-6"
```

## Example 2 — Bracketed Reference

```bash
python verse2image.py "[2 Samuel 21:3-6]"
```

## Example 3 — Single Verse

```bash
python verse2image.py "John 3:16"
```

## Example 4 — Specify EPUB and Output Directory

```bash
python verse2image.py "John 3:16" \
    --epub nwt_S.epub \
    --output-dir verse_images
```

## Example 5 — Debug Mode

```bash
python verse2image.py "2 Samuel 21:3-6" \
    --debug
```

---

# Docker

The application can also be run inside Docker.

## Build the Image

```bash
docker build -t it1013/verse2image .
```

---

## Linux

Run the container from the project directory:

```bash
docker run --rm \
  -v "$(pwd)/verse_images:/app/verse_images" \
  -v "$(pwd)/config.ini:/app/config.ini" \
  -v "$(pwd)/nwt_S.epub:/app/nwt_S.epub:ro" \
  it1013/verse2image "2 Samuel 21:3-6"
```

### Linux — Debug Mode

```bash
docker run --rm \
  -v "$(pwd)/verse_images:/app/verse_images" \
  -v "$(pwd)/config.ini:/app/config.ini" \
  -v "$(pwd)/nwt_S.epub:/app/nwt_S.epub:ro" \
  it1013/verse2image "2 Samuel 21:3-6" \
  --debug
```

---

## Windows PowerShell

```powershell
docker run --rm `
  -v "${PWD}/verse_images:/app/verse_images" `
  -v "${PWD}/config.ini:/app/config.ini" `
  -v "${PWD}/nwt_S.epub:/app/nwt_S.epub:ro" `
  it1013/verse2image "2 Samuel 21:3-6"
```

### Windows PowerShell — Debug Mode

```powershell
docker run --rm `
  -v "${PWD}/verse_images:/app/verse_images" `
  -v "${PWD}/config.ini:/app/config.ini" `
  -v "${PWD}/nwt_S.epub:/app/nwt_S.epub:ro" `
  it1013/verse2image "2 Samuel 21:3-6" `
  --debug
```

The same command can also be written on one line:

```powershell
docker run --rm -v "${PWD}/verse_images:/app/verse_images" -v "${PWD}/config.ini:/app/config.ini" -v "${PWD}/nwt_S.epub:/app/nwt_S.epub:ro" it1013/verse2image "2 Samuel 21:3-6" --debug
```

---

# Docker Volume Mounts

The Docker commands mount three host resources into the container.

| Host            | Container           | Purpose                   |
| --------------- | ------------------- | ------------------------- |
| `verse_images/` | `/app/verse_images` | Stores generated images   |
| `config.ini`    | `/app/config.ini`   | Application configuration |
| `nwt_S.epub`    | `/app/nwt_S.epub`   | Source Bible EPUB         |

The EPUB is mounted read-only:

```text
:ro
```

This prevents the container from modifying the source EPUB.

---

# Configuration

The application uses a configuration object loaded from:

```python
from config import Config
```

and:

```python
config = Config()
```

Configuration controls the EPUB path, output directory, image dimensions, margins, fonts, colors, line spacing, and text layout.

Important image-related settings include concepts such as:

```text
Image width
Image height
Horizontal margins
Top/bottom margins
Font size
Minimum font size
Maximum font size
Font size step
Line spacing
Line length
Maximum lines per image
Background color
Text color
Shadow color
Citation positioning
```

Keeping these values in configuration allows the image appearance to be changed without modifying the extraction logic.

---

# Processing Flow

The complete application flow is:

```text
Command Line Reference
        │
        ▼
   parse_reference()
        │
        ▼
   Validate EPUB
        │
        ▼
    Open EPUB
        │
        ▼
 Locate Bible Book
        │
        ▼
 Locate Chapter
        │
        ▼
 Locate Verse Markers
        │
        ▼
 Extract Requested Verses
        │
        ▼
 Convert Verse Numbers
        │
        ▼
 Normalize Text
        │
        ▼
  parse_verse_blocks()
        │
        ▼
   auto_fit_font()
        │
        ▼
    render_pages()
        │
        ▼
   Generate PNG(s)
        │
        ▼
 Save to output directory
```

---

# Error Handling

The application handles several common errors.

### Invalid Bible Reference

```text
[error] Could not parse reference: ...
verse not found
```

### Missing EPUB

```text
[error] EPUB file not found: ...
verse not found
```

### Chapter Not Found

```text
[error] Could not locate ...
verse not found
```

### Verse Not Found

```text
[error] Verses ... not found ...
verse not found
```

### Image Generation Failure

If image generation fails, the application reports the error and exits with a non-zero status.

---

# Troubleshooting

## Enable Debug Mode

The first troubleshooting step should be to run:

```bash
python verse2image.py "2 Samuel 21:3-6" --debug
```

This provides detailed information about the EPUB navigation and extraction process.

---

## Verify the EPUB

Make sure the EPUB exists:

```bash
ls -l nwt_S.epub
```

On Windows PowerShell:

```powershell
Get-Item .\nwt_S.epub
```

---

## Verify Dependencies

Run:

```bash
pip install ebooklib beautifulsoup4 Pillow
```

If using a virtual environment, make sure it is activated before installing the packages.

---

## Verify Output Directory

The application automatically creates the configured output directory if it does not exist.

For example:

```text
verse_images/
```

---

# Development Notes

The application separates the workflow into distinct responsibilities:

```text
Reference parsing
        ↓
EPUB navigation
        ↓
Verse extraction
        ↓
Text processing
        ↓
Text wrapping
        ↓
Font fitting
        ↓
Image rendering
        ↓
File output
```

This separation makes it possible to modify the image design without changing the EPUB extraction logic, or modify EPUB extraction without changing the rendering pipeline.

---

# Dependencies

The project uses:

* **Python 3**
* **EbookLib** — EPUB reading
* **BeautifulSoup4** — XHTML/HTML parsing
* **Pillow** — image creation and text rendering

Install them with:

```bash
pip install ebooklib beautifulsoup4 Pillow
```

---

# License / Source Text

This application is a software tool for extracting and rendering text from an EPUB supplied by the user.

The `nwt_S.epub` file and the Bible text contained within it are separate from the application source code. Users are responsible for ensuring that their use and distribution of the EPUB and generated content complies with the applicable rights and terms associated with that material.

---

# Quick Start

For the shortest path from installation to generated image:

```bash
pip install ebooklib beautifulsoup4 Pillow
```

Place:

```text
verse2image.py
config.py
config.ini
nwt_S.epub
```

in the same project directory, then run:

```bash
python verse2image.py "2 Samuel 21:3-6"
```

Generated images will be written to the configured output directory.

For troubleshooting:

```bash
python verse2image.py "2 Samuel 21:3-6" --debug
```

Or run the application in Docker:

```bash
docker build -t it1013/verse2image .
```

```bash
docker run --rm \
  -v "$(pwd)/verse_images:/app/verse_images" \
  -v "$(pwd)/config.ini:/app/config.ini" \
  -v "$(pwd)/nwt_S.epub:/app/nwt_S.epub:ro" \
  it1013/verse2image "2 Samuel 21:3-6"
```
