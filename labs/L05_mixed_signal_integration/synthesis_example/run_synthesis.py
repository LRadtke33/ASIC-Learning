#!/usr/bin/env python3
"""Reproduce lesson 45's small SKY130 mapping and Boolean equivalence check.

Needs Yosys with ABC. By default, uses the bundled reference Liberty offline.
--fetch-lib downloads another checksum-verified copy; --lib supplies an existing
byte-identical file. This is
logic synthesis and functional equivalence, not static timing or physical design.
"""
from pathlib import Path
import argparse
from collections import Counter
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parent
BUILD = ROOT.parent / "run_results" / "synthesis"
ORFS_REVISION = "c5310d7ffdd5f8a1eed83089697631548cc08a99"
LIB_URL = f"https://raw.githubusercontent.com/The-OpenROAD-Project/OpenROAD-flow-scripts/{ORFS_REVISION}/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"
LIB_SHA256 = "ec0e1067a35c8bf20b11e58d1e8ac53326067e4dac84a125cc1b917a3518d0d9"

def executable(value):
    found = shutil.which(value)
    if found:
        return str(Path(found).resolve())
    path = Path(value).expanduser()
    if path.is_file():
        return str(path.resolve())
    raise SystemExit("Tool not found: " + value)

def quoted(value):
    value = str(value)
    if "\n" in value or "\r" in value:
        raise SystemExit("Paths with newlines are not supported by this teaching script.")
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'

def run_yosys(yosys, text, name):
    script = BUILD / (name + ".ys")
    log = BUILD / (name + ".log")
    script.write_text(text)
    command = [yosys, "-Q", "-T", "-l", str(log), str(script)]
    print("$ " + shlex.join(command))
    result = subprocess.run(command, cwd=BUILD, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=90, check=False)
    (BUILD / (name + ".stdout")).write_text(result.stdout)
    if result.returncode:
        print(result.stdout[-8000:])
        raise SystemExit("Yosys failed; see " + str(log))
    return result.stdout

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--yosys", default=os.environ.get("YOSYS", "yosys"))
    parser.add_argument("--abc", default=os.environ.get("ABC"), help="optional ABC executable path")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--lib", type=Path, help="existing pinned Liberty file")
    source.add_argument("--fetch-lib", action="store_true", help="download pinned public Liberty file with SHA-256 verification")
    args = parser.parse_args()
    yosys = executable(args.yosys)
    abc = executable(args.abc) if args.abc else None
    BUILD.mkdir(parents=True, exist_ok=True)
    lib = args.lib.expanduser().resolve() if args.lib else (BUILD if args.fetch_lib else ROOT.parent / "reference") / "sky130_fd_sc_hd__tt_025C_1v80.lib"
    if args.fetch_lib and not lib.exists():
        print("Downloading the pinned public SKY130 Liberty file (12.8 MB).")
        with urllib.request.urlopen(LIB_URL, timeout=60) as response:
            content = response.read()
        if hashlib.sha256(content).hexdigest() != LIB_SHA256:
            raise SystemExit("Downloaded library checksum did not match; file was not installed.")
        lib.write_bytes(content)
    if not lib.is_file():
        raise SystemExit("Library not found: " + str(lib))
    digest = hashlib.sha256(lib.read_bytes()).hexdigest()
    if digest != LIB_SHA256:
        raise SystemExit("Library differs from the pinned lesson reference. Use --fetch-lib to reproduce this result; adapt a copy of the script for other libraries.")
    qlib, qrtl = quoted(lib), quoted(ROOT / "enabled_xor.v")
    mapped = BUILD / "mapped.v"
    mapping = f"""read_liberty -lib -ignore_miss_func {qlib}
read_verilog {qrtl}
hierarchy -check -top enabled_xor
synth -top enabled_xor -noabc
dfflibmap -liberty {qlib}
abc -liberty {qlib}{' -exe '+quoted(abc) if abc else ''}
clean
check
stat -liberty {qlib}
write_verilog -noattr {quoted(mapped)}
select -module enabled_xor
write_json -selected {quoted(BUILD / 'mapped.json')}
"""
    map_output = run_yosys(yosys, mapping, "map")
    verification = f"""read_liberty -ignore_miss_func {qlib}
read_verilog {quoted(mapped)}
hierarchy -top enabled_xor
flatten
rename enabled_xor gate
read_verilog {qrtl}
proc
rename enabled_xor gold
equiv_make gold gate equiv
hierarchy -top equiv
equiv_simple
equiv_induct -seq 4
equiv_status -assert
"""
    verify_output = run_yosys(yosys, verification, "verify")
    if "Equivalence successfully proven!" not in verify_output:
        raise SystemExit("Equivalence result was not recognized; inspect verify.log.")
    mapped_json = json.loads((BUILD / "mapped.json").read_text())
    cells = Counter(c["type"] for c in mapped_json["modules"]["enabled_xor"]["cells"].values())
    if any(name.startswith("$") for name in cells):
        raise SystemExit("Unmapped internal cells remain in the result.")
    match = re.search(r"Chip area for module .*?:\s*([0-9.]+)", map_output)
    version = subprocess.run([yosys, "-V"], text=True, capture_output=True, check=False).stdout.strip()
    result = {"tool": version, "library_url": LIB_URL, "library_sha256": digest,
              "mapping": dict(sorted(cells.items())), "total_cells": sum(cells.values()),
              "library_cell_area_sum": float(match.group(1)) if match else None,
              "equivalence": "PASS: two output bits proven against the Liberty Boolean/sequential model",
              "scope": "Executed synthesis and functional equivalence only. No SDC-driven optimization, STA, placement, routing, clock-tree, or power estimation was run."}
    (BUILD / "observed.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
