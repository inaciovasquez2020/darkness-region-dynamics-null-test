import subprocess

def test_download_or_reference_external_comparison_dataset():
    subprocess.run(
        ["python3", "tools/verify_download_or_reference_external_comparison_dataset.py"],
        check=True,
    )
