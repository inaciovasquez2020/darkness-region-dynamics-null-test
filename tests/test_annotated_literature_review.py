import subprocess

def test_annotated_literature_review():
    subprocess.run(
        ["python3", "tools/verify_annotated_literature_review.py"],
        check=True,
    )
