"""Mock OpenModelica simulation executable simulating TwoConnectedTanks model solver.

Usage:
    python TwoConnectedTanks.py -override=startTime=0,stopTime=4
"""

import sys
import time
import re


def parse_override_flag(args):
    start_time = 0
    stop_time = 4

    for arg in args:
        if arg.startswith("-override="):
            match_start = re.search(r"startTime=(\d+)", arg)
            match_stop = re.search(r"stopTime=(\d+)", arg)
            if match_start:
                start_time = int(match_start.group(1))
            if match_stop:
                stop_time = int(match_stop.group(1))

    return start_time, stop_time


def main():
    print("==========================================================")
    print(" OpenModelica Solver - Model: TwoConnectedTanks          ")
    print("==========================================================")
    print(f"Received CLI arguments: {sys.argv[1:]}")

    start_time, stop_time = parse_override_flag(sys.argv)
    print(f"[SOLVER CONFIG] startTime = {start_time}, stopTime = {stop_time}")

    print("[SOLVER INFO] Initializing DAE system state vectors...")
    time.sleep(0.3)
    print("[SOLVER INFO] Initial values successfully validated.")
    print("[SOLVER INFO] Selected Integrator: DASSL (Differential-Algebraic System Solver)")

    current_time = float(start_time)
    step_size = (stop_time - start_time) / 10.0 if stop_time > start_time else 0.1

    print("\n--- Simulation Integration Loop Started ---")
    step = 0
    while current_time <= stop_time:
        h1 = 2.5 - 0.2 * current_time
        h2 = 1.0 + 0.15 * current_time
        print(f"Time: {current_time:5.2f}s | Step: {step:02d} | Tank1_Height: {h1:5.3f} m | Tank2_Height: {h2:5.3f} m")
        sys.stdout.flush()
        time.sleep(0.15)
        current_time += step_size
        step += 1

    print("\n[SOLVER INFO] Simulation successfully completed!")
    print("[SOLVER INFO] Result file generated: TwoConnectedTanks_res.mat")
    print("==========================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
