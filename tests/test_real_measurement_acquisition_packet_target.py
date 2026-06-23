import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_real_measurement_acquisition_packet_target_verifier():
    result = subprocess.run(
        [sys.executable, "tools/verify_real_measurement_acquisition_packet_target.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    assert "REAL_MEASUREMENT_ACQUISITION_PACKET_TARGET_OK" in result.stdout
