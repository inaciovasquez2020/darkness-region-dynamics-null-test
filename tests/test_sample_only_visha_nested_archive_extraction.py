import subprocess

def test_sample_only_visha_nested_archive_extraction():
    subprocess.run(
        ["python3", "tools/verify_sample_only_visha_nested_archive_extraction.py"],
        check=True,
    )
