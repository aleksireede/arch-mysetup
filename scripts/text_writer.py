#!/usr/bin/env python3

import argparse
from pathlib import Path


def replacetext(file: Path, search_text: str, replace_text: str):
    data = file.read_text()

    if search_text not in data:
        print(f"Text not found: '{search_text}' — skipping.")
        return

    file.write_text(data.replace(search_text, replace_text))
    print(f"Text replaced: '{search_text}' -> '{replace_text}'")


def write_text(file: Path, text: str):
    data = file.read_text()
    file.write_text(data + "\n" + text)
    print(f"Text appended: '{text}'")


def main():
    parser = argparse.ArgumentParser(
        description="Replace text in a file or append text to a file"
    )
    parser.add_argument("file", help="Path to the file")
    parser.add_argument("arg1", help="Search text OR text to append")
    parser.add_argument("arg2", nargs="?", help="Replacement text (optional)")

    args = parser.parse_args()
    file_path = Path(args.file)

    if not file_path.exists():
        print(f"File not found: {file_path}")
        return

    if args.arg2 is None:
        # Only 2 arguments → write text
        write_text(file_path, args.arg1)
    else:
        # 3 arguments → replace text
        replacetext(file_path, args.arg1, args.arg2)


if __name__ == "__main__":
    main()
