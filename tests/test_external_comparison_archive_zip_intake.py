import subprocess

def test_external_comparison_archive_zip_intake():
    subprocess.run(
        ["python3", "tools/verify_external_comparison_archive_zip_intake.py"],
        check=True,
    )
