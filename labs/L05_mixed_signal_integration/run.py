#!/usr/bin/env python3
"""Run the digital integration lab with Python's standard library and Icarus.

Outputs are created only under this lab's run_results/ directory. No network or PDK
installation is needed. --negative-control generates an intentionally broken
copy in run_results/ and expects the checker to reject its broken data-hold behavior.
"""
from pathlib import Path
import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
CASES = {
    "fast_source": (7, 11, 3, 4369),
    "fast_readout": (13, 5, 1, 8738),
    "close_clocks": (10, 11, 4, 13107),
}
RESULT = re.compile(r"RESULT accepted=(\d+) delivered=(\d+) aborted=(\d+) rejected_busy=(\d+) min_latency_ns=([\d.]+) max_latency_ns=([\d.]+)")

def executable(value):
    found = shutil.which(value)
    if found:
        return str(Path(found).resolve())
    p = Path(value).expanduser()
    if p.is_file():
        return str(p.resolve())
    raise SystemExit(f"Tool not found: {value}. Install Icarus Verilog, or supply --iverilog and --vvp paths.")

def run(command, cwd):
    print("$ " + shlex.join([str(x) for x in command]))
    result = subprocess.run([str(x) for x in command], cwd=cwd, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            timeout=30, check=False)
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iverilog", default=os.environ.get("IVERILOG", "iverilog"))
    parser.add_argument("--vvp", default=os.environ.get("VVP", "vvp"))
    parser.add_argument("--case", choices=["all", *CASES], default="all")
    parser.add_argument("--waves", action="store_true", help="also generate a VCD per case")
    parser.add_argument("--negative-control", action="store_true", help="prove the checker catches a deliberately broken data hold")
    args = parser.parse_args()
    compiler, simulator = executable(args.iverilog), executable(args.vvp)
    build = ROOT / "run_results"
    build.mkdir(exist_ok=True)
    rtl = [ROOT / "rtl" / name for name in ["reset_release.sv", "sync_bit.sv", "mixed_signal_mailbox.sv"]]
    suffix = "_negative" if args.negative_control else ""
    if args.negative_control:
        text = rtl[-1].read_text()
        old = "            src_accept <= 1'b0;\n            src_reject"
        new = "            src_accept <= 1'b0;\n            mailbox_word <= src_word; // DELIBERATE BUG: overwrite while busy\n            src_reject"
        if text.count(old) != 1:
            raise SystemExit("Cannot safely construct the negative control; source marker changed.")
        broken = build / "mixed_signal_mailbox_broken.sv"
        broken.write_text(text.replace(old, new))
        rtl[-1] = broken
    program = build / ("mailbox" + suffix + ".vvp")
    compile_result = run([compiler, "-g2012", "-Wall", "-s", "tb_mixed_signal_integration", "-o", program,
                          *rtl, ROOT / "tb" / "tb_mixed_signal_integration.sv"], ROOT)
    (build / ("compile" + suffix + ".log")).write_text(compile_result.stdout)
    if compile_result.stdout:
        print(compile_result.stdout, end="")
    if compile_result.returncode:
        raise SystemExit("Compilation failed; see run_results/compile" + suffix + ".log")
    version = subprocess.run([compiler, "-V"], text=True, capture_output=True, check=False).stdout.splitlines()[0]
    chosen = CASES if args.case == "all" else {args.case: CASES[args.case]}
    observations = {"tool": version, "scope": "Digital event simulation; no analog metastability or physical timing model.",
                    "negative_control": args.negative_control, "cases": []}
    for name, values in chosen.items():
        work = build / (name + suffix)
        work.mkdir(exist_ok=True)
        command = [simulator, program]
        command += [f"+{key}={value}" for key, value in zip(["SRC_HALF_NS", "DST_HALF_NS", "DST_PHASE_NS", "SEED"], values)]
        if args.waves:
            command.append("+WAVES")
        result = run(command, work)
        (work / "observed.txt").write_text(result.stdout)
        print(result.stdout, end="")
        record = {"name": name, "source_period_ns": 2*values[0], "readout_period_ns": 2*values[1],
                  "readout_initial_phase_ns": values[2], "seed": values[3], "exit_code": result.returncode}
        if args.negative_control:
            expected_failure = result.returncode != 0 and "mailbox changed while busy" in result.stdout
            if not expected_failure:
                raise SystemExit(f"Negative control {name} did not fail for the intended data-hold violation.")
            record["observed"] = "Expected data-hold assertion failure detected."
            print("NEGATIVE CONTROL PASS: the broken mailbox was rejected for the intended reason.")
        else:
            match = RESULT.search(result.stdout)
            if result.returncode or match is None or "PASS: all digital protocol assertions" not in result.stdout:
                raise SystemExit(f"Case {name} failed; inspect {work / 'observed.txt'}")
            fields = ["accepted", "delivered", "aborted", "rejected_busy", "min_latency_ns", "max_latency_ns"]
            record.update({key: (int(value) if index < 4 else float(value))
                           for index, (key, value) in enumerate(zip(fields, match.groups()))})
            if record["accepted"] != record["delivered"] + record["aborted"]:
                raise SystemExit("Result accounting failed independently in the runner.")
            record["observed"] = "PASS"
        observations["cases"].append(record)
    output = build / ("observed" + suffix + ".json")
    output.write_text(json.dumps(observations, indent=2) + "\n")
    print("Recorded observations: " + str(output))

if __name__ == "__main__":
    main()
