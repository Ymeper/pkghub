#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["msgpack"]
# ///
"""
Convert all files under data/ into a single MessagePack file.

Directory structure:
  data/
    git/
      meta.json
      actions.json
      script/
        install_xxx.sh
        uninstall_xxx.sh
  ...

Output structure (dict keyed by package name):
  {
    "git": {
      "meta": { ... },
      "actions": { ... },
      "scripts": {
        "install_xxx.sh": "#!/bin/bash\n...",
        "uninstall_xxx.sh": "#!/bin/bash\n..."
      }
    }
  }

The output file is written to the project root as `pkghub.msgpack`.
"""

import json
import os
import sys
from pathlib import Path

try:
    import msgpack
except ImportError:
    print("Error: 'msgpack' package not installed. Run: pip install msgpack")
    sys.exit(1)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_FILE = Path(__file__).resolve().parent.parent / "pkghub.msgpack"

# Mapping from JSON filename (without extension) to key in output
JSON_KEYS = {
    "meta": "meta",
    "actions": "actions",
}


def load_package(pkg_dir: Path) -> dict | None:
    """Load all recognised JSON files from a package directory."""
    result = {}
    for json_name, key in JSON_KEYS.items():
        json_path = pkg_dir / f"{json_name}.json"
        if json_path.exists():
            with open(json_path, encoding="utf-8") as f:
                result[key] = json.load(f)
    return result if result else None


def load_scripts(pkg_dir: Path) -> dict[str, str]:
    """Load all script files from script/ subdirectory."""
    scripts = {}
    script_dir = pkg_dir / "script"
    if not script_dir.is_dir():
        return scripts
    for script_file in sorted(script_dir.iterdir()):
        if script_file.is_file():
            with open(script_file, encoding="utf-8") as f:
                scripts[script_file.name] = f.read()
    return scripts


def main() -> None:
    if not DATA_DIR.is_dir():
        print(f"Error: data directory not found at {DATA_DIR}")
        sys.exit(1)

    packages: dict[str, dict] = {}

    for entry in sorted(DATA_DIR.iterdir()):
        if entry.is_dir():
            pkg_data = load_package(entry)
            if pkg_data:
                # Load scripts
                scripts = load_scripts(entry)
                if scripts:
                    pkg_data["scripts"] = scripts
                packages[entry.name] = pkg_data
                print(f"  ✔ {entry.name}: {list(pkg_data.keys())} ({len(scripts)} scripts)")

    if not packages:
        print("Warning: No packages found under data/")
        sys.exit(1)

    # Write MessagePack
    with open(OUTPUT_FILE, "wb") as f:
        packed = msgpack.packb(packages, use_bin_type=True)
        f.write(packed)

    size_kb = OUTPUT_FILE.stat().st_size / 1024
    print(f"\n✅ Packed {len(packages)} package(s) → {OUTPUT_FILE.name} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    print("Packing data/ → pkghub.msgpack\n")
    main()
