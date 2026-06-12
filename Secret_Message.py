"""
Secret Message

Goal: Create a function that takes in an argument that is a string containing a URL for a published Google Doc
    The information in the Google Doc will be a table of Unicode characters and their x and y positions.
    The x and y positions will be used to print out the characters (with 0,0 being the bottom left corner, positive x being right and positive y being up) in the correct order to reveal a secret message.
"""
from typing import Dict, Tuple
import re
import sys
import argparse

import requests
from bs4 import BeautifulSoup

DEBUG = False
DEFAULT_URL_FILE = "url_test.txt"


def get_doc_contents(url):
    # This function should take in the URL of the Google Doc and return the contents of the document as a string.
    resp = requests.get(url)
    resp.raise_for_status()
    if DEBUG:
        print(f"Fetched document content from {url} (length {len(resp.text)})")
        print("Content:")
        print(resp.text)
    return resp.text

def extract_table(contents):
    # This function should take in the contents of the Google Doc and return the table of Unicode characters and their x and y positions as a map from the tuple (x, y) to the Unicode character.
    soup = BeautifulSoup(contents, "html.parser")

    # Find the first table in the document
    table = soup.find("table")
    if table is None:
        return {}

    mapping: Dict[Tuple[int, int], str] = {}

    # Iterate rows; skip header if present
    for tr in table.find_all("tr"):
        cells = tr.find_all(["td", "th"])  # some published docs use th for header
        if len(cells) < 3:
            continue

        # Extract text for x, char, y
        x_text = cells[0].get_text(strip=True)
        char_text = cells[1].get_text()
        y_text = cells[2].get_text(strip=True)

        # Try to parse integers for x and y; skip header rows that aren't numeric
        m_x = re.search(r"-?\d+", x_text)
        m_y = re.search(r"-?\d+", y_text)
        if not m_x or not m_y:
            continue

        x = int(m_x.group(0))
        y = int(m_y.group(0))

        # Character cell: keep as-is but strip newlines; if empty, treat as space
        ch = char_text.strip() if char_text is not None else ""
        if ch == "":
            ch = " "

        # If character cell contains more than one character, keep the full string
        mapping[(x, y)] = ch

        if DEBUG:
            print(f"Extracted mapping: ({x}, {y}) -> '{ch}'")

    if DEBUG:
        print(f"Extracted total {len(mapping)} mappings from table.")
        print("Mappings:")
        for (x, y), ch in mapping.items():
            print(f"  ({x}, {y}) -> '{ch}'")

    return mapping

def print_secret_message(table):
    # This function should take in the table of Unicode characters and their x and y positions and print out the characters in the correct order to reveal the secret message.
    # Characters should be printed in order of their y position (top to bottom) and then by their x position (left to right).
    if not table:
        print("(no table data)")
        return

    xs = [coord[0] for coord in table.keys()]
    ys = [coord[1] for coord in table.keys()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    width = max_x - min_x + 1
    height = max_y - min_y + 1

    # Create grid filled with spaces
    grid = [[" " for _ in range(width)] for __ in range(height)]

    for (x, y), ch in table.items():
        gx = x - min_x
        gy = y - min_y
        # If multiple chars map to same cell, the last one will stay (document should avoid duplicates)
        if 0 <= gy < height and 0 <= gx < width:
            grid[gy][gx] = ch

    # Print rows in order of y decreasing (top to bottom). Within each row, print left to right (x increasing).
    for row in reversed(grid):
        line = "".join(row)
        # Write bytes using utf-8 to avoid Windows console encoding issues
        try:
            sys.stdout.buffer.write((line + "\n").encode("utf-8", errors="replace"))
        except Exception:
            # Fallback to print if anything unexpected happens
            print(line)

def main(url):
    contents = get_doc_contents(url)
    table = extract_table(contents)
    print_secret_message(table)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Print secret message from a published Google Doc table.")
    parser.add_argument("--url", "-u", help="Published Google Doc URL (overrides --file)")
    parser.add_argument("--file", "-f", default=f"{DEFAULT_URL_FILE}", help="Path to file containing the URL (default: url.txt)")
    args = parser.parse_args()

    url = args.url
    if not url:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                url = f.read().strip()
        except FileNotFoundError:
            print("url not provided and file not found. Provide --url or a URL file.")
            raise SystemExit(1)

    main(url)
