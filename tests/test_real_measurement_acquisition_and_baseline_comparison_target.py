import subprocess

def test_real_measurement_acquisition_and_baseline_comparison_target():
    subprocess.run(
        ["python3", "tools/verify_real_measurement_acquisition_and_baseline_comparison_target.py"],
        check=True,
    )
