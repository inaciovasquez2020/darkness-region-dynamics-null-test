import subprocess

def test_literature_novelty_review_or_external_validation_packet():
    subprocess.run(
        ["python3", "tools/verify_literature_novelty_review_or_external_validation_packet.py"],
        check=True,
    )
