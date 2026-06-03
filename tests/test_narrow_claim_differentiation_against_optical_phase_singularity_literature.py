import subprocess

def test_narrow_claim_differentiation_against_optical_phase_singularity_literature():
    subprocess.run(
        ["python3", "tools/verify_narrow_claim_differentiation_against_optical_phase_singularity_literature.py"],
        check=True,
    )
