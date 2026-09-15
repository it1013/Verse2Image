#!/usr/bin/env python3
"""
Bible Verse Image Generator
Extracts verse text from nwt_S.epub and renders styled 1920x1080 PNG images.

RUN:
    Examples:
        python verse2image.py "2 Samuel 21:3-6"
        python verse2image.py "[2 Samuel 21:3-6]"
        python verse2image.py "John 3:16" \
            --epub nwt_S.epub \
            --output-dir verse_images

REG:
pip install ebooklib beautifulsoup4 Pillow

sections of code:
1. Configuration / Imports
2. Parse the reference string
3. HTML → text helpers  (strip tags, decode entities)
4. Locate & extract verses from the EPUB
5. Text-wrapping & image generation
6. Main
"""


"""
# Section 1 - Configuration / Imports
# 
# bs4 / ebooklib / html / re used to import and parse through the epub
# to extract the requested verses. PIL (Pillow) is used to generate 
# the image. os / sys / pathlib used to manage the loading, creation, 
# and manipulation of the files.
# 
"""

import re
import os
import sys
from pathlib import Path
from html import unescape
from config import Config

import ebooklib
from bs4.element import AttributeValueList
from ebooklib import epub
from bs4 import BeautifulSoup, Tag
import PIL
from PIL.Image import Image
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont, ImageFont


# Configuration
config = Config()

# Spanish NWT book abbreviations
BOOK_MAP = {
    # Hebrew Scriptures
    "génesis": "gén.",
    "genesis": "gén.",
    "éxodo": "éx.",
    "exodo": "éx.",
    "levítico": "lev.",
    "levitico": "lev.",
    "números": "núm.",
    "numeros": "núm.",
    "deuteronomio": "deut.",
    "josué": "jos.",
    "josue": "jos.",
    "jueces": "juec.",
    "rut": "rut",
    "1 samuel": "1 sam.",
    "1samuel": "1 sam.",
    "2 samuel": "2 sam.",
    "2samuel": "2 sam.",
    "1 reyes": "1 rey.",
    "1reyes": "1 rey.",
    "2 reyes": "2 rey.",
    "2reyes": "2 rey.",
    "1 crónicas": "1 crón.",
    "1 cronicas": "1 crón.",
    "2 crónicas": "2 crón.",
    "2 cronicas": "2 crón.",
    "esdras": "esd.",
    "nehemías": "neh.",
    "nehemias": "neh.",
    "ester": "est.",
    "job": "job",
    "salmos": "sal.",
    "salmo": "sal.",
    "proverbios": "prov.",
    "eclesiastés": "ecl.",
    "eclesiastes": "ecl.",
    "cantar de los cantares": "cant.",
    "isaías": "is.",
    "isaias": "is.",
    "jeremías": "jer.",
    "jeremias": "jer.",
    "lamentaciones": "lam.",
    "ezequiel": "ezeq.",
    "daniel": "dan.",
    "oseas": "os.",
    "joel": "joel",
    "amós": "amós",
    "amos": "amós",
    "abdías": "abd.",
    "abdias": "abd.",
    "jonás": "jon.",
    "jonas": "jon.",
    "miqueas": "miq.",
    "nahúm": "nah.",
    "nahum": "nah.",
    "habacuc": "hab.",
    "sofonías": "sof.",
    "sofonias": "sof.",
    "ageo": "ageo",
    "zacarías": "zac.",
    "zacarias": "zac.",
    "malaquías": "mal.",
    "malaquias": "mal.",

    # Greek Scriptures
    "mateo": "mat.",
    "marcos": "mar.",
    "lucas": "luc.",
    "juan": "juan",
    "hechos": "hech.",
    "romanos": "rom.",
    "1 corintios": "1 cor.",
    "1corintios": "1 cor.",
    "2 corintios": "2 cor.",
    "2corintios": "2 cor.",
    "gálatas": "gál.",
    "galatas": "gál.",
    "efesios": "efes.",
    "filipenses": "filip.",
    "colosenses": "col.",
    "1 tesalonicenses": "1 tes.",
    "1tesalonicenses": "1 tes.",
    "2 tesalonicenses": "2 tes.",
    "2tesalonicenses": "2 tes.",
    "1 timoteo": "1 tim.",
    "1timoteo": "1 tim.",
    "2 timoteo": "2 tim.",
    "2timoteo": "2 tim.",
    "tito": "tito",
    "filemón": "filem.",
    "filemon": "filem.",
    "hebreos": "heb.",
    "santiago": "sant.",
    "1 pedro": "1 ped.",
    "1pedro": "1 ped.",
    "2 pedro": "2 ped.",
    "2pedro": "2 ped.",
    "1 juan": "1 juan",
    "1juan": "1 juan",
    "2 juan": "2 juan",
    "2juan": "2 juan",
    "3 juan": "3 juan",
    "3juan": "3 juan",
    "judas": "jud.",
    "apocalipsis": "apoc.",
}

"""
# Section 2 - Parse the reference string
# Bible reference
#        │
#        ▼
# parse_reference()
#        ├── book = "2 Samuel"
#        ├── chapter = 21
#        └── verses = 3-6
#        │
#        ▼
# HANDOFF to Section 3 Code
# 
#
# Parse a Bible verse reference string.
# **Example output when tested:**
# Handles:           → Returns:
# 2 Samuel 21:3-6    → {'book': '2 Samuel', 'chapter': 21, 'start_verse': 3, 'end_verse': 6}
# John 3:16          → {'book': 'John', 'chapter': 3, 'start_verse': 16, 'end_verse': 16}
# [1 Kings 18:30-39] → {'book': '1 Kings', 'chapter': 18, 'start_verse': 30, 'end_verse': 39}
# 3 John 1:1-14      → {'book': '3 John', 'chapter': 1, 'start_verse': 1, 'end_verse': 14}
#
# Raises:
#     ValueError: if the reference cannot be parsed.
#
# Strip surrounding brackets / whitespace
"""
def parse_reference(ref: str) -> dict:

    ref = ref.strip().strip("[]()\"'")
    # Pattern: This one was ripped from Ollama, god help anyone that can generate that regex _||_
    #   ^
    #   (?P<book>[\w\s]+?)        book name (may include digits + spaces)
    #   \s+                        whitespace
    #   (?P<chapter>\d+)          chapter number
    #   :                          colon
    #   (?P<start>\d+)            start verse
    #   (?:-(?P<end>\d+))?       optional end verse
    #   $
    pattern = re.compile(r"^\s*"r"(?P<book>[\w\s]+?)"r"\s+"r"(?P<chapter>\d+)"r"[:]"r"(?P<start>\d+)"r"(?:-(?P<end>\d+))?"r"\s*$")

    m = pattern.match(ref)
    if not m:
        raise ValueError(f"Could not parse reference: {ref!r}")

    book        = m.group("book").strip()
    chapter     = int(m.group("chapter"))
    start_verse = int(m.group("start"))
    end_verse   = int(m.group("end")) if m.group("end") else start_verse

    # Sanity: end must be >= start and same chapter (single-chapter refs only)
    if end_verse < start_verse:
        raise ValueError(f"End verse {end_verse} < start verse {start_verse}")

    return {
        "book":        book,
        "chapter":     chapter,
        "start_verse": start_verse,
        "end_verse":   end_verse,
    }

"""
# Section 3 - HTML → text helpers  (strip tags, decode entities)
# | Helper | Purpose |
# |--------|---------|
# | `strip_tags` | Remove HTML, preserve paragraph breaks |
# | `decode_entities` | `&amp;` → `&`, `&#8212;` → `—` |
# | `clean_text` | Full pipeline (strip + decode + normalize) |
# | `element_text` | BS4 element → clean string |
# | `get_verse_markers` | Find verse-number spans within a chapter |
# | `_try_verse_num` | Extract the int from a marker element |
"""
"""strip_tags
Remove all HTML tags from a string, keeping only visible text.
Replaces block-level closing tags with newlines so we don't
accidentally join paragraphs together.
"""
"""decode_entities
Decode HTML entities (&amp; → &, &#8212; → —, etc.)
"""
"""
Full cleanup pipeline:
  1. Strip tags
  2. Decode entities
  3. Normalize whitespace (collapse runs of spaces/tabs)
  4. Collapse 3+ newlines to 2
"""
"""
Scan a BeautifulSoup element for verse-number markers.
NWT epubs typically mark verses with one of these patterns:
  <span class="verse" id="...">3</span>
  <span id="verse-3">3</span>
  <strong class="verse">3</strong>

Returns a list of (element, verse_number_int) tuples
in document order.
"""
"""
Get clean text from a BeautifulSoup element.
Preserves paragraph boundaries as newlines.
"""
"""
Try to extract a verse number from a marker element.
Looks at the element's own text (not children) or its first text node.
"""
"""
Locate the XHTML item in the EPUB that corresponds to
the given book + chapter.

Strategy:
  1. Match on item name / title (fast, no content decode)
  2. Fallback: scan item content (slower, but reliable)

Returns an ebooklib Item or None.
"""
"""
Walk a chapter's HTML and produce an ordered list of
(verse_number, verse_text) pairs.

Logic:
  • Find all verse markers in document order.
  • For each marker, the verse text is the content from
    that marker up to (but not including) the next marker.
  • The last verse runs to the end of the parent container.
"""
def strip_tags(html: str) -> str:
    # Convert block-level closers to newlines before stripping
    html = re.sub(r"</(p|div|section|h[1-6]|li|blockquote)>", "\n", html, flags=re.I)
    # Remove all remaining tags
    html = re.sub(r"<[^>]+>", "", html)
    return html

def decode_entities(text: str) -> str:
    return unescape(text)

def clean_text(text: str) -> str:
    text = strip_tags(text)
    text = decode_entities(text)
    text = re.sub(r"[ \t]+", " ", text)       # horizontal whitespace
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)  # collapse blank-line runs
    return text.strip()

def element_text(soup_element) -> str:
    if soup_element is None:
        return ""
    # get_text with separator to keep blocks separated
    raw = soup_element.get_text(separator="\n")
    return clean_text(raw)

def get_verse_markers(soup_element) -> list:
    markers = []

    # Strategy 1: elements with class containing "verse"
    for el in soup_element.find_all(class_=re.compile(r"verse", re.I)):
        num = _try_verse_num(el)
        if num is not None:
            markers.append((el, num))

    # Strategy 2: elements whose id looks like "verse-NN" or "vNN"
    if not markers:
        for el in soup_element.find_all(id=True):
            id_str = el.get("id", "")
            m = re.match(r"(?:verse[-_]?|v)(\d+)", id_str, re.I)
            if m:
                markers.append((el, int(m.group(1))))

    # Sort by document position (use a stable index via find_all order)
    # find_all already returns in document order, so we're good.
    return markers

def _try_verse_num(el) -> int | None:
    # Get direct text (excluding child elements)
    direct_text = ""
    for child in el.children:
        if getattr(child, "name", None) is None:  # NavigableString
            direct_text += str(child)

    direct_text = direct_text.strip()

    # The number should be the first token
    m = re.match(r"^(\d+)", direct_text)
    if m:
        return int(m.group(1))

    # Fallback: whole element text (might just be a number)
    full = el.get_text().strip()
    m = re.match(r"^(\d+)", full)
    if m:
        return int(m.group(1))

    return None

def find_chapter_item(doc, book: str, chapter: int):
    book_key = _normalize_book(book)          # e.g. "samuel"
    docs = [it for it in doc.get_items()
            if it.get_type() == ebooklib.ITEM_DOCUMENT]

    # ── Pass 1: name / title match ──
    for item in docs:
        name  = (item.get_name()  or "").lower()
        title = (item.get_title() or "").lower()
        hay   = f"{name} {title}"

        if book_key in hay and re.search(rf"\b{chapter}\b", hay):
            return item

    # ── Pass 2: content scan ──
    for item in docs:
        try:
            raw = item.get_content().decode("utf-8", errors="ignore")
        except Exception:
            continue

        # Must contain the book keyword somewhere
        if book_key not in raw.lower():
            continue

        # Must contain the chapter number near the top (heading area)
        head = raw[:800].lower()
        if re.search(rf"\b{chapter}\b", head):
            return item

    return None

def flatten_verses(soup: BeautifulSoup) -> list[tuple[int, str]]:
    markers = get_verse_markers(soup)
    if not markers:
        return []

    # We need the text of each marker element AND the text that
    # follows it until the next marker.

    results: list[tuple[int, str]] = []
    current_num: int | None = None
    buffer: list[str] = []

    marker_set = {id(el): num for el, num in markers}

    def walk(el):
        nonlocal current_num, buffer

        # Check if this element is a verse marker
        if id(el) in marker_set:
            # Flush previous
            if current_num is not None:
                text = " ".join(buffer).strip()
                if text:
                    results.append((current_num, text))
            current_num = marker_set[id(el)]
            buffer = []
            return

        # Recurse into children
        for child in el.children:
            if getattr(child, "name", None) is not None:
                walk(child)
            else:
                # Text node
                t = str(child).strip()
                if t:
                    buffer.append(t)

    # Walk the body (or the whole soup)
    root = soup.body if soup.body else soup
    walk(root)

    # Flush last verse
    if current_num is not None:
        text = " ".join(buffer).strip()
        if text:
            results.append((current_num, text))

    return results
"""
# Section 4 – Locate chapter & extract verse range from EPUB
#
# EPUB structure:
#   META-INF/container.xml   → standard EPUB container
#   biblebooknav.xhtml       → top-level book/chapter index
#   [chapter files]          → actual verse content
"""
"""
High-level: open EPUB → find chapter → extract verse range.

Returns the verse text as a single string, or raises
VerseNotFoundError.

# 4a. Find the navigation item
# 4b. Parse the nav page → resolve to a chapter item

extract_verses:
    given all the normalized data and epub_path to search for the 
    verses and return a long string of all the verses 
find_nav_item:    
    Locate 'biblebooknav.xhtml' among the EPUB items.
_normalize_book: taking the input to normalize the book name for searching
    '2 Samuel'   → 'samuel'
    'The Psalms' → 'psalms'
    '1 Kings'    → 'kings'

"""
def extract_verses(epub_path: str, book: str, chapter: int, start_verse: int, end_verse: int) -> str:
    class VerseNotFoundError(Exception):
        pass

    if not os.path.isfile(epub_path):
        raise VerseNotFoundError(f"EPUB file not found: {epub_path}")

    doc = epub.read_epub(epub_path, options={"ignore_ncx": True})
    item = find_chapter_item(doc, book, chapter)

    if item is None:
        raise VerseNotFoundError(
            f"Could not locate {book} {chapter} in {epub_path}"
        )

    html = item.get_content().decode("utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    verses = flatten_verses(soup)

    if not verses:
        raise VerseNotFoundError(
            f"No verse markers found in {book} {chapter}"
        )

    # Filter to requested range
    selected = [(num, txt) for num, txt in verses
                if start_verse <= num <= end_verse]

    if not selected:
        raise VerseNotFoundError(
            f"Verses {start_verse}-{end_verse} not found in "
            f"{book} {chapter} "
            f"(available: {verses[0][0]}–{verses[-1][0]})"
        )

    # Join: "3 text... 4 text..."
    parts = []
    for num, txt in selected:
        parts.append(f"[{num}] {txt}")
    return "  ".join(parts)

def find_nav_item(doc):
    for item in doc.get_items():
        name = (item.get_name() or "").lower()
        if "biblebooknav" in name:
            return item
    return None

def _normalize_book(name: str) -> str:
    name = name.lower().strip()
    name = re.sub(r"^\d+\s*", "", name)
    name = re.sub(r"^the\s+", "", name)
    return name.strip()

"""
Resolve a Bible book navigation href from the NWT EPUB navigation page.
The supplied nav_soup contains book links such as:
    <a href="biblechapternav10.xhtml">2 Sam.</a>
For example:
    book = "2 Samuel"
    chapter = 21
resolves to:
    "biblechapternav10.xhtml"
NOTE:
    This navigation page contains BOOK links, not individual chapter
    links. The returned href is therefore the chapter-navigation page for the requested book.
"""
def resolve_chapter_href(nav_soup: BeautifulSoup,book: str,chapter: int,debug:bool = False) -> str | AttributeValueList | None:
    # Normalize input
    book_input = " ".join(book.lower().strip().split())
    # Try direct mapping first
    expected_abbreviation = BOOK_MAP.get(book_input)
    # If the input wasn't found in the map, normalize it and compare
    # against the visible text in the navigation.
    if expected_abbreviation:
        expected_abbreviation = expected_abbreviation.lower()
    if debug:
        print(f"Book requested: {book}")
        print(f"Chapter requested: {chapter}")
        print(f"Expected abbreviation: {expected_abbreviation}")

    # Search book navigation links
    for a in nav_soup.find_all("a", href=True):
        # Get the visible link text.
        link_text = a.get_text(" ", strip=True).lower()
        # Normalize whitespace.
        link_text = " ".join(link_text.split())
        if debug: print(f"Checking book: '{link_text}' -> {a.get('href')}")
        # Primary match: mapped abbreviation
        if expected_abbreviation:
            if link_text == expected_abbreviation:
                return a["href"]

        # Secondary match: normalized input equals link text
        # This allows calls such as: book="Rut"
        if link_text == book_input:
            return a["href"]
    # Fallback matching
    # Useful if the abbreviation map doesn't contain a book or if the
    # EPUB changes its capitalization/punctuation.
    if expected_abbreviation:
        abbreviation_base = expected_abbreviation.rstrip(".").strip()
        for a in nav_soup.find_all("a", href=True):
            link_text = " ".join(a.get_text(" ", strip=True).lower().split())
            link_base = link_text.rstrip(".").strip()
            if link_base == abbreviation_base:
                return a["href"]

    # If we got here verse Not found
    return None

"""
Normalize an EPUB href for comparison.

Removes:
  - URL fragments
  - leading './'
  - Windows path separators
  - leading '/'
"""
def normalize_href(href: str) -> str:

    href = (href or "").strip()

    # Remove fragment
    href = href.split("#", 1)[0]

    # Normalize path separators
    href = href.replace("\\", "/")

    # Remove leading ./ and /
    href = re.sub(r"^(\./)+", "", href)
    href = href.lstrip("/")

    return href.lower()

"""
Find the actual EpubItem in the EPUB matching an href.

Examples:
    biblechapternav10.xhtml
    1001061114-split21.xhtml
    OEBPS/1001061114-split21.xhtml
"""
def find_epub_item(doc: epub.EpubBook,href: str,debug: bool = False) -> epub.EpubItem | None:
    target = normalize_href(href)
    if debug:
        print(f"Looking for EPUB item: {target}")
    for item in doc.get_items():
        # Only XHTML/HTML documents are relevant here.
        if item.get_type() not in (ebooklib.ITEM_DOCUMENT,ebooklib.ITEM_NAVIGATION,):
            continue

        item_name = normalize_href(item.get_name())

        if debug:
            print(f"  Checking: {item_name}")

        # Exact match
        if item_name == target:
            return item

        # Handle hrefs where one contains the EPUB directory path.
        if item_name.endswith("/" + target):
            return item

        if target.endswith("/" + item_name):
            return item

        # Last path component fallback
        if item_name.split("/")[-1] == target.split("/")[-1]:
            return item

    return None

"""
Resolve a Bible book + chapter to the actual EpubItem
containing the chapter text.

Example:
    book = "2 Samuel"
    chapter = 21

Navigation:
    biblebooknav.xhtml
        |
        +-- 2 Sam.
              |
              +-- biblechapternav10.xhtml
                          |
                          +-- 21
                              |
                              +-- 1001061114-split21.xhtml

Returns:
    epub.EpubItem for 1001061114-split21.xhtml
"""
def resolve_chapter_item(doc: epub.EpubBook,book_nav_item: epub.EpubItem,book: str,chapter: int,debug: bool = False) -> epub.EpubItem | None:
    book_key = " ".join(book.lower().strip().split())

    # Convert English/full name to the abbreviation used by the EPUB.
    expected_book = BOOK_MAP.get(book_key, book_key)
    if debug:
        print("=" * 70)
        print("RESOLVE CHAPTER")
        print(f"Book:              {book}")
        print(f"Normalized book:   {book_key}")
        print(f"EPUB abbreviation: {expected_book}")
        print(f"Chapter:           {chapter}")
        print("=" * 70)
    # STEP 1
    #   book_nav_item should be biblebooknav.xhtml
    # Find:
    #   <a href="biblechapternav10.xhtml">2 Sam.</a>
    book_nav_html = book_nav_item.get_content()
    book_nav_soup = BeautifulSoup(book_nav_html, "html.parser")
    chapter_nav_href = None
    for a in book_nav_soup.find_all("a", href=True):
        link_text = " ".join(a.get_text(" ", strip=True).lower().split())
        if debug: print(f"BOOK NAV: '{link_text}' -> {a.get('href')}")
        if link_text == expected_book:
            chapter_nav_href = a["href"]
            break

    if not chapter_nav_href:
        if debug:
            print(f"ERROR: Could not find book '{book}' ('{expected_book}')")
        return None
    if debug:
        print(f"Book navigation href: {chapter_nav_href}")

    # STEP 2
    # Resolve biblechapternav10.xhtml to its EpubItem.
    chapter_nav_item = find_epub_item(doc,chapter_nav_href,debug=debug)

    if chapter_nav_item is None:
        if debug: print(f"ERROR: Could not resolve {chapter_nav_href}")
        return None

    if debug: print(f"Chapter navigation item: {chapter_nav_item.get_name()}")

    # STEP 3
    # Parse biblechapternav10.xhtml and
    # Find:
    #     <a href="1001061114-split21.xhtml">21</a>

    chapter_nav_html = chapter_nav_item.get_content()
    chapter_nav_soup = BeautifulSoup(chapter_nav_html,"html.parser")
    chapter_href = None

    for a in chapter_nav_soup.find_all("a", href=True):
        link_text = a.get_text(" ", strip=True)
        if debug:
            print(f"CHAPTER NAV: '{link_text}' -> {a.get('href')}")
        if link_text == str(chapter):
            chapter_href = a["href"]
            break
    if not chapter_href:
        if debug: print(f"ERROR: Could not find chapter {chapter}")
        return None
    if debug: print(f"Chapter href: {chapter_href}")

    # STEP 4
    # Resolve:
    #     1001061114-split21.xhtml
    # to the ACTUAL EpubItem in the EPUB.

    chapter_item = find_epub_item(doc,chapter_href,debug=debug)

    if chapter_item is None:
        if debug: print(f"ERROR: Could not resolve chapter item: {chapter_href}")
        return None

    if debug:
        print("=" * 70)
        print(f"CHAPTER ITEM FOUND: {chapter_item.get_name()}")
        print("=" * 70)

    return chapter_item


"""
# 4c. Fallback: brute-force content scan

If nav resolution fails, scan all document items
for one whose heading area mentions the book + chapter.
"""
def fallback_find_chapter(doc, book: str, chapter: int):

    book_key = _normalize_book(book)

    for item in doc.get_items():
        if item.get_type() != ebooklib.ITEM_DOCUMENT:
            continue
        try:
            raw = item.get_content().decode("utf-8", errors="ignore")
        except Exception:
            continue

        head = raw[:1000].lower()
        if book_key in head and re.search(rf"\b{chapter}\b", head):
            return item

    return None

"""
# 4d. Extract the verse range
Extract verses from an NWT EPUB chapter EpubItem.

Returns one continuous string with Unicode superscript verse
numbers inserted between verses.

Example:
    ³ David les dijo a los gabaonitas...
    ⁴ Los gabaonitas le contestaron...
    ⁵ Ellos le dijeron al rey...

Actual return value is continuous text:
    ³ David les dijo... ⁴ Los gabaonitas... ⁵ Ellos...

Footnotes, page numbers, navigation elements, and footnote
references are excluded.
"""
def extract_verses_from_item(item,start_verse: int,end_verse: int,debug: bool = False) -> str:
    if start_verse < 1:
        raise ValueError("start_verse must be >= 1")

    if end_verse < start_verse:
        raise ValueError("end_verse must be >= start_verse")
    # Unicode superscript conversion
    superscript_map = str.maketrans("0123456789","⁰¹²³⁴⁵⁶⁷⁸⁹")
    def superscript(number: int) -> str:
        return str(number).translate(superscript_map)
    # Load XHTML
    content = item.get_content()
    if isinstance(content, bytes):
        content = content.decode("utf-8",errors="ignore")

    soup = BeautifulSoup(content,"html.parser")

    if debug:
        print("=" * 70)
        print("EXTRACT VERSES")
        print(f"Item: {item.get_name()}")
        print(f"Requested verses: {start_verse}-{end_verse}")
        print("=" * 70)

    # Remove elements that are not part of the verse text.
    for selector in ("p.w_navigation", ".pageNum", ".groupFootnote", "aside[epub\\:type='footnote']", "[epub\\:type='noteref']",):
        for element in soup.select(selector):
            element.decompose()

    # Find verse markers:
    # chapter21_verse1
    # chapter21_verse2
    # chapter21_verse3
    # ...
    verse_markers = {}

    for span in soup.find_all("span", id=re.compile(r"^chapter\d+_verse\d+$")):
        match = re.match(r"^chapter\d+_verse(\d+)$",span.get("id", ""))
        if match:
            verse_number = int(match.group(1))
            verse_markers[verse_number] = span
    if debug:
        print("Found verses:",sorted(verse_markers.keys()))

    if not verse_markers:
        raise VerseNotFoundError("No verse markers found in chapter.")

    available = sorted(verse_markers.keys())

    selected_numbers = [
        number
        for number in available
        if start_verse <= number <= end_verse
    ]

    if not selected_numbers:
        raise VerseNotFoundError(f"Verses {start_verse}–{end_verse} not found (chapter has {available[0]}–{available[-1]})")

    # Determine whether an element is a verse marker.

    def is_verse_marker(element) -> bool:
        if not isinstance(element, Tag):
            return False
        return bool(
            re.match(r"^chapter\d+_verse\d+$",element.get("id", "")))

    # Extract the text belonging to one verse.
    def extract_verse_text(marker: Tag) -> str:
        text_parts = []
        for element in marker.next_elements:
            # Stop at the next verse marker.
            if is_verse_marker(element):
                break
            if isinstance(element, Tag):
                element_id = element.get("id", "")
                element_class = element.get("class",[])

                # Ignore page numbers.
                if "pageNum" in element_class or element_id.startswith("page"):
                    continue

                # Ignore footnotes and footnote references.
                epub_type = element.get("epub:type","")

                if epub_type in ("noteref","footnote",):
                    continue

                # Ignore the actual verse-number <sup>.
                if element.name == "sup":
                    continue

            # Collect text nodes.
            if not isinstance(element, Tag):
                text_parts.append(str(element))

        text = "".join(text_parts)

        # Normalize whitespace.
        text = text.replace("\xa0", " ")
        text = text.replace("\u202f", " ")
        text = text.replace("\u2009", " ")
        text = text[2:]
        text = re.sub(r"\s+"," ",text).strip()
        return text

    # Build one continuous string.
    parts = []

    for verse_number in selected_numbers:
        marker = verse_markers[verse_number]
        verse_text = extract_verse_text(marker)
        if not verse_text:
            continue
        # Add superscript verse number.
        parts.append(f"{superscript(verse_number)} {verse_text}")

        if debug:
            print(f"Verse {verse_number}: {verse_text}")

    if not parts:
        raise VerseNotFoundError(f"Verses {start_verse}–{end_verse} were found, but contained no text.")

    # One continuous text string.
    return " ".join(parts)


# 4e. Public entry point
class VerseNotFoundError(Exception):
    pass
"""
One-call interface.
    extract_verse("nwtb.epub", "2 Samuel 21:3-6")
    → "[3] And the men of Gath... [4] ..."
Raises VerseNotFoundError on failure.
"""
def extract_verse(epub_path: str, reference: str,debug: bool = False) -> str:

    ref = parse_reference(reference)
    book = ref["book"]
    chapter = ref["chapter"]
    v_start = ref["start_verse"]
    v_end = ref["end_verse"]

    if not os.path.isfile(epub_path):
        raise VerseNotFoundError(f"EPUB not found: {epub_path}")

    doc = epub.read_epub(epub_path, options={"ignore_ncx": True})
    if debug: print(f"Reading {epub_path} : read : {doc}" )
    # ── Locate the chapter item ──
    item = None

    nav_item = find_nav_item(doc)
    if nav_item is not None:
        nav_html = nav_item.get_content().decode("utf-8", errors="ignore")
        nav_soup = BeautifulSoup(nav_html, "html.parser")
        href = resolve_chapter_href(nav_soup, book, chapter,debug)
        if href:
            if debug:
                print("href_to_item called")
                print(doc)
                print(href)
                print(f"nav_item: {nav_item}")
            item = resolve_chapter_item(doc, nav_item, book, chapter)
            #item = href_to_item(doc, href, nav_item)
        if debug: print("Resolved resolve_chapter_href correctly for item")

    if item is None:
        if debug: print("item got to NONE in extract_verse")
        item = fallback_find_chapter(doc, book, chapter)

    if item is None:
        if debug: print("fallback got to NONE too in extract_verse")
        raise VerseNotFoundError(
            f"Could not locate {book} ch.{chapter} in the EPUB."
        )

    # ── Extract ──
    return extract_verses_from_item(item, v_start, v_end, debug)

"""
# Section 5 – Render verse text to 1920×1080 PNG(s)
#
# Dependencies:
#   pip install Pillow
#
# Visual design:
#   • Dark background  #3c3c3c
#   • Verse text       #E5E7EB
#   • Verse numbers    #F59E0B  (amber)
#   • Citation         #9CA3AF  (gray), centered, bottom
#   • Font             serif (configurable)
"""

"""
# 5a. Font loading
Load a TTF at the given size; fall back to Pillow default.
Try for a bold variant; fall back to regular.
"""
def load_font(size: int, debug: bool = False) -> FreeTypeFont | ImageFont:

    for path in config.font_candidates:
        try:
            if debug: print(f"last load_font attempt, loading {path} \n\n")
            return PIL.ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    # Last resort – Pillow built-in (bitmap, no FreeType)
    if debug: print("load_font failed, loading default font Pillow built-in \n\n")
    return PIL.ImageFont.load_default(size)

def load_font_bold(size: int, debug: bool = False) -> FreeTypeFont | ImageFont:
    if debug: print(f"::::::::{config.font_candidates[1]}")
    for path in config.font_candidates[1]:
        try:
            return PIL.ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    return load_font(size,debug)

"""
Split verse text into image-sized text blocks.
Returns a list of dictionaries. Each dictionary represents one image
    and contains the lines that should be rendered on that image.
Example:
    Input:
        "² Los primeros habitantes que regresaron a sus propiedades
         en sus ciudades fueron algunos israelitas, los sacerdotes,
         los levitas y los siervos del templo."

    Output:
        [
        {"num": 1, "text": "² Los primeros habitantes que regresaron a sus"},
        {"num": 2, "text": "propiedades en sus ciudades fueron algunos israelitas, los"},
        {"num": 3, "text": "sacerdotes, los levitas y los siervos del templo."}
        ]
# parse_verse_blocks to split incoming text into appropriate
# blocks for the image process. Implement a standard string length
# for each line number, max number of lines before needing another
# image. Continue to build images until all the verses are graphed
# onto images. Use the End_Block = '....' to denote the end of the
# block, an additional image is needed, and a new block will follow.
# 5b. Parse verse text into structured blocks
"""
def parse_verse_blocks(text: str, line_length: int = 80, max_lines: int = 8, debug: bool = False) -> list[dict]:


    if not text or not text.strip(): return []
    if line_length < 1: raise ValueError("line_length must be greater than 0")
    if max_lines < 1: raise ValueError("max_lines must be greater than 0")

    # Normalize whitespace.
    text = re.sub(r"\s+", " ", text).strip()
    # Constructing the lines by splitting all the words, then adding
    # them word by word until line_length
    words = text.split(" ")
    if debug: print(f"words: {words}")
    lines = []
    current_line = ""
    for word in words:
        # If adding this word exceeds the line length,
        # finish the current line.
        if current_line:
            candidate = f"{current_line} {word}"
        else:
            candidate = word
        if len(candidate) <= line_length:
            current_line = candidate
        else:
            if current_line:
                # if greater than line_length, append to lines
                if debug: print(f"Reached line limit ADDING current_line: {current_line}")
                lines.append(current_line)
            # Handle an individual word longer than line_length, will return nothing if we don't
            if len(word) > line_length:
                while len(word) > line_length:
                    lines.append(word[:line_length])
                    word = word[line_length:]
                current_line = word
            else:
                current_line = word

        if debug: print(f"Building current_line: {current_line}")
    # Appending last current_line to dict lines to then add the completed lines to blocks
    if current_line:
        lines.append(current_line)
        if debug: print(f"Adding last current_line: {current_line}")

    # Convert the lines into blocks of text, divided for each image.
    blocks = []
    # Adding END_BLOCK to the end of the last, to all blocks except the first
    for image_start in range(0, len(lines), max_lines):
        if image_start != 0:
            lines[image_start - 1] += config.end_block
    # Constructing the blocks, adding line one by one until
    for image_start in range(0, len(lines), max_lines):
        if debug:
            print(f"######image_start: {image_start}")
            print(f"######lines: {lines}")
        # Adding END_BLOCK to the beginning of the line if not the first block
        if image_start != 0:
            if debug:
                print("at last line if block")
                print(f"LINES -1: {lines[image_start-1]}")
            lines[image_start] = config.end_block + lines[image_start]
        image_lines = lines[image_start:image_start + max_lines]
        blocks.append({ "num": len(blocks) + 1, "text": "\n".join(image_lines) })
        if debug:
            print(f"Image start: {image_start}")
            print(f"image_lines: {image_lines}")
            print(f"Future Sight: {len(lines[image_start + max_lines:image_start + (max_lines*2)])}")
        # If the next block is only one line long, add it to this block instead
        if len(lines[image_start + max_lines:image_start + (max_lines*2)]) == 1:
            blocks.pop()
            image_lines = lines[image_start:image_start + (max_lines*2)]
            blocks.append({ "num": len(blocks) + 1, "text": "\n".join(image_lines) })
            if debug:
                print(f"Image start: {image_start}")
                print(f"image_lines: {image_lines}")
            break


    if debug:
        print("=" * 70)
        print("PARSED IMAGE BLOCKS")
        print(f"Line length : {line_length}")
        print(f"Max lines   : {max_lines}")
        print(f"Total lines : {len(lines)}")
        print(f"Images      : {len(blocks)}")
        print("=" * 70)

        for block in blocks:
            print(f"\nImage {block['num']}:")
            print(block["text"])

    return blocks

"""
Determine the largest font size that allows all parsed verse blocks
to fit within the available image dimensions.
Returns:
    int: Font size to pass to load_font(size).
Raises:
    ValueError: If blocks is empty or no font size fits.
"""
def auto_fit_font(blocks: list[dict], debug: bool = False):
    if not blocks: raise ValueError("blocks cannot be empty")

    # Maximum area available for the verse text.
    max_width = config.img_width - (2 * config.margin_x)
    max_height = config.img_height - config.margin_top - config.margin_bot # extra room for citation was built into MARGIN_BOT

    if max_width <= 0: raise ValueError("Invalid horizontal margins")
    if max_height <= 0: raise ValueError("Invalid vertical margins")

    # Start at the configured maximum/start size, whichever is smaller.
    start_size = max(config.font_size_start, config.font_size_max)
    if debug:
        print("Maxs before starting:")
        print(f"Max width : {max_width}")
        print(f"Max height : {max_height}")
        print(f"Start size : {start_size}")
        print(f"Values out of config.ini:"
              f"STEP {config.font_size_step}"
              f":SIZEMIN {config.font_size_min}"
              f":SIZEMAX {config.font_size_max}"
              f":START_SIZE {config.font_size_start}")
    # Pillow's multiline_text spacing is measured in pixels.
    # calculate the actual line spacing from the font.
    for size in range(start_size, config.font_size_min - 1, -config.font_size_step):
        font = load_font(size,debug)
        fits = True
        if debug:
            print("=" * 70)
            print(f"Testing font size: {size}")
            print(f"Maximum width : {max_width}")
            print(f"Maximum height: {max_height}")
            print(f"Start font size : {start_size}, given to load_font {size}")

        for block in blocks:
            block_text = block.get("text", "")
            if not block_text:
                continue # break out of the block loop if no text lines remain
            line_count = len(block_text.splitlines()) # Number of lines in this block.
            # Get the font's normal line height. font.getbbox("Ag") method in Python's
            # Pillow library returns the bounding box of the text "Ag" as
            # a tuple of four values: (left, top, right, bottom)
            bbox = font.getbbox("Ag") # this is not working when run in docker
            font_height = bbox[3] - bbox[1]
            if debug:
                print(f"font_height: {font_height} = {bbox[3]} - {bbox[1]}")
                print(f"bbox: {bbox}")
            # Apply LINE_SPACING.
            line_height = int(font_height * config.line_spacing)
            # Pillow multiline_textbbox requires the actual spacing
            # between lines, rather than the total line height.
            spacing = max(0, line_height - font_height)
            # Use multiline_textbbox if available.
            # This correctly handles the newline characters in blocks.
            dummy_draw = ImageDraw.Draw(Image.new("RGB", (0,0)))
            #draw.text((x, y), line, font=font, fill=VERSE_NUM_COLOR)
            left, top, right, bottom = dummy_draw.multiline_textbbox((0, 0),block_text,font=font,spacing=spacing)

            text_width = right - left
            text_height = bottom - top

            if debug:
                print(f"Block {block['num']}: ")
                print(f"text width x height: {text_width} x {text_height}")
                print(f"({line_count} lines)")
            # Check width.
            if text_width > max_width:
                fits = False
                if debug:
                    print(f"  DOES NOT FIT WIDTH: ")
                    print(f"{text_width} > {max_width}")
                break
            # Check height.
            if text_height > max_height:
                fits = False
                if debug:
                    print(f"  DOES NOT FIT HEIGHT: ")
                    print(f"{text_height} > {max_height}")
                break

        # If every block fits, this is the largest usable font size.
        if fits:
            if debug:
                print("-" * 70)
                print(f"SELECTED FONT SIZE: {size}")
                print(f"Maximum width : {max_width}")
                print(f"Maximum height : {max_height}")
                print("=" * 70)

            return size

    # Nothing between FONT_SIZE_START and FONT_SIZE_MIN fit.
    raise ValueError(f"No font size from start {start_size} down to {config.font_size_min} fits the supplied blocks.")

"""
Convert verse text into one image per verse block.
Example:
    [3] First Block...
    [4] Second Block...
    [5] Third Block...
produces:
    Image 1 -> Block 3
    Image 2 -> Block 4
    Image 3 -> Block 5
render_page to accept the blocks from parse_verse_blocks correctly
# and not the lines it is currently accepting, rendering with this logic:
#   for block in blocks:
#       for lines in block:
#           print(f"\nImage {block['num']}:")
#           print(block["text"])
# onto the number of images determined by the number of blocks
# 5e. Render a single page image
"""
def render_pages(blocks: dict, citation: str, font: FreeTypeFont, font_num: FreeTypeFont, debug: bool = False) -> list[Image.Image]:
    # Parse the extracted verse text
    if not blocks: raise ValueError("No verse blocks found in text.")

    if debug:
        print("GOT TO FUNCTION render_page")
        print(f"Found {len(blocks)} blocks.")
        print(f"FONT sizes handed to render_page: {font.size}:{font_num.size}")
        for block in blocks:
            print(f"\nImage {block['num']}:")
            print(block["text"])
    # Create one image per verse block
    images = []
    line_h = int(font.size * config.line_spacing)

    for num_str, block in enumerate(blocks, start=1):
        if not config.centered:
            x = config.margin_x
        y = config.margin_top
        img = Image.new("RGB", (config.img_width, config.img_height), config.bg_color)
        draw = ImageDraw.Draw(img)
        if num_str:
            lines = block["text"].split('\n')
            if debug:
                print("IN blocks FOR LOOP")
                print(f"Lines: {lines}")
                print(f"\nImage {block['num']}:")
                print(block["text"])
                print(f"At current number of verse block: {num_str}")
            for line in lines:
                if config.centered:
                    text_width = draw.textlength(line,font=font)
                    x = (config.img_width - text_width) // 2
                shadow_position = (x + config.shadow_x_offset, y + config.shadow_y_offset)
                draw.text(shadow_position, line, font=font, fill=config.shadow_color)
                draw.text((x, y), line, font=font, fill=config.verse_num_color)
                y += line_h
                if debug:
                    print("IN lines FOR LOOP")
                    print(f"Adding \'{line}\' to image")
                    print("")
                    print(f"Line length: {len(line)}")
                    print(f"Line length: {draw.textlength(line,font=font)}")
                    print(f"Line length: {(len(line) + config.margin_x)}")
                    print(x)
            if debug: print(f"CITATION_X: {config.img_width - config.citation_x_offset}, CITATION_Y: {config.img_height - config.citation_y_offset}")
            draw.text((config.img_width - config.citation_x_offset, config.img_height - config.citation_y_offset), citation, font=font_num, fill=config.verse_num_color)
        images.append(img)
    if debug:
        print("\nGOT TO end FUNCTION render_pages")
        print(f"returning {len(images)} images.")
        print(images)

    return images


"""
Takes the verse string from Section 4 and returns
one or more 1920×1080 PNG images.

    images = generate_images(verse_text, "2 Samuel 21:3–6")
    images[0].save("out.png")
# 5g. Public entry point
"""
def generate_images(verse_text: str, citation: str,debug: bool = False) -> list[Image.Image]:

    blocks = parse_verse_blocks(verse_text, config.line_length, config.max_lines)
    if debug:
        print(f"verse text: {verse_text}")
        print(f"citation: {citation}")
        print(f"blocks: {blocks}")

    if not blocks:
        raise ValueError("No verse blocks found in text.")
    if debug:
        print("GOT INTO fit on one page with a good font size")
    # determine the font size to give to load_font(size), so that font can be given
    # to the render_page to generate the image,
    size =  auto_fit_font(blocks,debug)

    font = load_font(size,debug)
    font_num = load_font_bold(size - (size // 4),debug)
    if debug: print(f"font_num before being passed to render_page: {font_num}")
    if debug: print(f"font before being passed to render_page: {font}")

    return render_pages(blocks, citation, font, font_num, debug)

# TEST Block
"""
if __name__ == "__main__":
    epub = "nwtb.epub"
    ref  = "2 Samuel 21:3-6"

    verse_text = extract_verse(epub, ref)
    print(verse_text)
    print("=" * 50)

    images = generate_images(verse_text, ref)

    for i, img in enumerate(images):
        path = f"output_{i}.png" if i else "output.png"
        img.save(path)
        print(f"Saved: {path}  ({img.size[0]}×{img.size[1]})")
"""

"""
# Section 6 – Main and Input Checks
"""
def main():
    """
    Command-line entry point.
    """

    import argparse
    parser = argparse.ArgumentParser(description="Extract a Bible verse from an NWT EPUB and generate one or more 1920x1080 PNG images.")
    parser.add_argument("reference",help='Bible verse reference, e.g. "2 Samuel 21:3-6"')
    parser.add_argument("--epub",default=config.epub_path,help=f"Path to the NWT EPUB file (default: {config.epub_path})")
    parser.add_argument("--output-dir",default=config.output_dir,help=f"Directory where PNG images will be saved (default: {config.output_dir})")
    parser.add_argument("--debug",action="store_true",help=f"Enable debug mode (default: {False}) ")
    args = parser.parse_args()

    # Parse reference
    try:
        reference = args.reference.strip()
        # Validate the reference before attempting EPUB extraction.
        parsed = parse_reference(reference)
        # Normalize citation format.
        citation = (f"{parsed['book']} " f"{parsed['chapter']}:" f"{parsed['start_verse']}"
        )

        if parsed["start_verse"] != parsed["end_verse"]:
            citation += f"–{parsed['end_verse']}"

    except ValueError as e:
        print(f"[error] {e}", file=sys.stderr)
        print("verse not found")
        return 1

    # Check EPUB
    if not os.path.isfile(args.epub):
        print(f"[error] EPUB file not found: {args.epub}",file=sys.stderr)
        print("verse not found")
        return 1

    # Extract verse text
    try:
        verse_text = extract_verse(args.epub,reference,args.debug)

    except VerseNotFoundError as e:
        print(f"[error] {e}", file=sys.stderr)
        print("verse not found")
        return 1

    except Exception as e:
        print(f"[error] Unable to extract verse: {e}",file=sys.stderr)
        print("verse not found")
        return 1

    if not verse_text or not verse_text.strip():
        print("verse not found")
        return 1

    # Display extracted text
    print()
    print(f"Reference: {citation}")
    print("-" * 60)
    print(verse_text)
    print("-" * 60)

    # Generate images

    try:
        images = generate_images(verse_text,citation,args.debug)
        #images = generate_images(verse_text,citation,True)
        if args.debug: print(f"Got images: {images}")
    except Exception as e:
        print(f"[error] Unable to generate images: {e}",file=sys.stderr)
        return 1
    if not images:
        print("[error] No images were generated.", file=sys.stderr)
        return 1

    # Create output directory
    output_dir = Path(args.output_dir)

    try:
        output_dir.mkdir(parents=True,exist_ok=True)
    except OSError as e:
        print(f"[error] Could not create output directory: {e}",file=sys.stderr)
        return 1

    # Create a filesystem-safe filename
    safe_citation = re.sub(r'[<>:"/\\|?*\[\]]',"",citation)
    safe_citation = re.sub(r"\s+","_",safe_citation)

    # Save generated images
    saved_files = []
    #image: list[Image.Image]
    if args.debug: print(f"image from images: {images} len {len(images)}")
    for index, image in enumerate(images, start=0):
        if args.debug:
            print(f"index from images: {index}")
            print(f"image from images: {image}")
        if len(images) == 1:
            if args.debug: print("images got ONED")
            filename = f"{safe_citation}.png"
        else:
            filename = f"{safe_citation}_{index:02d}.png"

        output_path = output_dir / filename

        try:
            image.save(output_path,format="PNG")
            saved_files.append(output_path)
            if args.debug: print(f"Saved: {output_path} ({image.width}x{image.height})")
        except OSError as e:
            print(f"[error] Could not save {output_path}: {e}",file=sys.stderr)
            return 1
        except Exception as e:
            print(f"[error] Could not save for generic error {output_path}: {e}",file=sys.stderr)
            return 1

    # Summary
    print()
    print(
        f"Generated {len(saved_files)} "
        f"image{'s' if len(saved_files) != 1 else ''}."
    )

    return 0



# Script entry point
if __name__ == "__main__":
    sys.exit(main())


"""
Bible reference
       │
       ▼
parse_reference()
       │
       ├── book = "2 Samuel"
       ├── chapter = 21
       └── verses = 3-6
       │
       ▼
biblebooknav.xhtml
       │
       ▼
"2 Sam."
       │
       ▼
biblechapternav10.xhtml
       │
       ▼
"21"
       │
       ▼
1001061114-split21.xhtml
       │
       ▼
EpubItem
       │
       ▼
<body>
       │
       ▼
extract verses 3-6
       │
       ▼
verse text
       │
       ▼
generate image
"""