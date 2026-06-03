import subprocess

def test_external_comparison_dataset_registry():
    subprocess.run(
        ["python3", "tools/verify_external_comparison_dataset_registry.py"],
        check=True,
    )
