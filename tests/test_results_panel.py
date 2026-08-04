"""Unit tests for ResultsPanel log output parsing and plotting helper functions."""

import pytest
from src.ui.results_panel import parse_simulation_output


def test_parse_simulation_output_valid():
    sample_log = """
    ==========================================================
     OpenModelica Solver - Model: TwoConnectedTanks          
    ==========================================================
    Received CLI arguments: ['-override=startTime=0,stopTime=4']
    [SOLVER CONFIG] startTime = 0, stopTime = 4
    [SOLVER INFO] Initializing DAE system state vectors...

    --- Simulation Integration Loop Started ---
    Time:  0.00s | Step: 00 | Tank1_Height: 2.500 m | Tank2_Height: 1.000 m
    Time:  0.40s | Step: 01 | Tank1_Height: 2.420 m | Tank2_Height: 1.060 m
    Time:  0.80s | Step: 02 | Tank1_Height: 2.340 m | Tank2_Height: 1.120 m
    Time:  4.00s | Step: 10 | Tank1_Height: 1.700 m | Tank2_Height: 1.600 m

    [SOLVER INFO] Simulation successfully completed!
    """

    parsed = parse_simulation_output(sample_log)
    assert "Time" in parsed
    assert len(parsed["Time"]) == 4
    assert parsed["Time"][0] == 0.00
    assert parsed["Time"][-1] == 4.00

    assert len(parsed["Tank1_Height"]) == 4
    assert parsed["Tank1_Height"][0] == 2.500
    assert parsed["Tank1_Height"][-1] == 1.700

    assert len(parsed["Tank2_Height"]) == 4
    assert parsed["Tank2_Height"][0] == 1.000
    assert parsed["Tank2_Height"][-1] == 1.600


def test_parse_simulation_output_empty():
    parsed = parse_simulation_output("No valid solver lines here.")
    assert parsed["Time"] == []
    assert parsed["Tank1_Height"] == []
    assert parsed["Tank2_Height"] == []
