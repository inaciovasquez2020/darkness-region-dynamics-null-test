import subprocess

def test_visha_boundary_extraction_smoke_test_on_sample():
    subprocess.run(
        ["python3", "tools/verify_visha_boundary_extraction_smoke_test_on_sample.py"],
        check=True,
    )
