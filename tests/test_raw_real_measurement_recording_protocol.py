import subprocess

def test_raw_real_measurement_recording_protocol():
    subprocess.run(
        ["python3", "tools/verify_raw_real_measurement_recording_protocol.py"],
        check=True,
    )
