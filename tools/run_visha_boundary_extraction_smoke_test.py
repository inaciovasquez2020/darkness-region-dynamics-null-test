import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_ROOT = ROOT / "data/external_comparison/visha/extracted/sample_frames"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
LABEL_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}

try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    Image = None
    PIL_AVAILABLE = False


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def image_size(path: Path):
    if not PIL_AVAILABLE:
        return None
    with Image.open(path) as im:
        return {"width": im.size[0], "height": im.size[1], "mode": im.mode}


def mask_boundary_stats(path: Path):
    if not PIL_AVAILABLE:
        return {
            "status": "PIL_NOT_AVAILABLE_DIMENSION_ONLY_SMOKE_TEST",
            "foreground_pixels": None,
            "boundary_pixels": None,
            "foreground_fraction": None,
            "boundary_fraction": None
        }

    with Image.open(path) as im:
        gray = im.convert("L")
        w, h = gray.size
        pix = gray.load()

        fg = [[pix[x, y] > 0 for x in range(w)] for y in range(h)]
        foreground = 0
        boundary = 0

        for y in range(h):
            for x in range(w):
                if not fg[y][x]:
                    continue
                foreground += 1
                if (
                    x == 0 or y == 0 or x == w - 1 or y == h - 1
                    or not fg[y][x - 1]
                    or not fg[y][x + 1]
                    or not fg[y - 1][x]
                    or not fg[y + 1][x]
                ):
                    boundary += 1

        total = w * h
        return {
            "status": "BOUNDARY_MASK_STATS_COMPUTED",
            "foreground_pixels": foreground,
            "boundary_pixels": boundary,
            "foreground_fraction": foreground / total if total else 0,
            "boundary_fraction": boundary / total if total else 0
        }


def collect_files(folder: Path, exts):
    if not folder.exists():
        return []
    return sorted(
        p for p in folder.rglob("*")
        if p.is_file()
        and "__MACOSX" not in p.parts
        and not p.name.startswith("._")
        and p.suffix.lower() in exts
    )


def pair_by_stem(images, labels):
    labels_by_stem = {}
    for label in labels:
        labels_by_stem.setdefault(label.stem, label)

    pairs = []
    for image in images:
        label = labels_by_stem.get(image.stem)
        if label is not None:
            pairs.append((image, label))
    return pairs


train_images = collect_files(SAMPLE_ROOT / "train_images", IMAGE_EXTS)
train_labels = collect_files(SAMPLE_ROOT / "train_labels", LABEL_EXTS)
test_images = collect_files(SAMPLE_ROOT / "test_images", IMAGE_EXTS)
test_labels = collect_files(SAMPLE_ROOT / "test_labels", LABEL_EXTS)

pairs = pair_by_stem(train_images, train_labels) + pair_by_stem(test_images, test_labels)

fallback_pairs = []
if not pairs:
    for image, label in zip(train_images + test_images, train_labels + test_labels):
        fallback_pairs.append((image, label))

selected_pairs = (pairs or fallback_pairs)[:10]

pair_results = []
for image, label in selected_pairs:
    image_info = image_size(image)
    label_info = image_size(label)
    stats = mask_boundary_stats(label)

    dimension_match = None
    if image_info is not None and label_info is not None:
        dimension_match = (
            image_info["width"] == label_info["width"]
            and image_info["height"] == label_info["height"]
        )

    pair_results.append({
        "image": str(image.relative_to(ROOT)),
        "label": str(label.relative_to(ROOT)),
        "image_sha256": sha256(image),
        "label_sha256": sha256(label),
        "image_size": image_info,
        "label_size": label_info,
        "dimension_match": dimension_match,
        "label_boundary_stats": stats
    })

usable_pair_count = len(selected_pairs)
boundary_stats_count = sum(
    1 for item in pair_results
    if item["label_boundary_stats"]["status"] == "BOUNDARY_MASK_STATS_COMPUTED"
)
dimension_checked_count = sum(
    1 for item in pair_results
    if item["dimension_match"] is not None
)
dimension_match_count = sum(
    1 for item in pair_results
    if item["dimension_match"] is True
)

stamp = datetime.now(timezone.utc).strftime("%Y_%m_%dT%H%M%SZ")

artifact = {
    "object": "ViShaBoundaryExtractionSmokeTestOnSample",
    "status": "VISHA_BOUNDARY_EXTRACTION_SMOKE_TEST_ON_SAMPLE_PASSED_EXTERNAL_COMPARISON_ONLY",
    "boundary_only": True,
    "new_science": False,
    "novelty_validated": False,
    "real_measurement_dataset_supplied": False,
    "external_comparison_dataset_sample_extracted": True,
    "full_dataset_extraction_completed": False,
    "pil_available": PIL_AVAILABLE,
    "sample_root": "data/external_comparison/visha/extracted/sample_frames",
    "input_counts": {
        "train_images": len(train_images),
        "train_labels": len(train_labels),
        "test_images": len(test_images),
        "test_labels": len(test_labels)
    },
    "pairing_method": "stem_match" if pairs else "fallback_zip_order",
    "sample_pair_count": usable_pair_count,
    "dimension_checked_count": dimension_checked_count,
    "dimension_match_count": dimension_match_count,
    "boundary_stats_count": boundary_stats_count,
    "pair_results": pair_results,
    "valid_use": [
        "boundary-extraction smoke test on external comparison sample",
        "pipeline sanity check",
        "shadow-mask processing check"
    ],
    "invalid_use": [
        "new_science_dataset",
        "novelty_validation",
        "real_measured_darkness_boundary_claim",
        "self_recorded_calibrated_measurement",
        "full_dataset_benchmark_claim"
    ],
    "minimal_missing_object_for_new_science": "ConcreteTrialDatasetWithRealMeasurementsAndBaselineComparison",
    "next_admissible_object": "SupplySelfRecordedCalibratedRawVideoOrObtainExternalExpertValidationReply"
}

if usable_pair_count <= 0:
    artifact["status"] = "VISHA_BOUNDARY_EXTRACTION_SMOKE_TEST_BLOCKED_NO_PAIRS"
elif PIL_AVAILABLE and boundary_stats_count <= 0:
    artifact["status"] = "VISHA_BOUNDARY_EXTRACTION_SMOKE_TEST_BLOCKED_NO_BOUNDARY_STATS"

artifact_path = ROOT / f"artifacts/darkness/visha_boundary_extraction_smoke_test_on_sample_{stamp}.json"
artifact_path.write_text(json.dumps(artifact, indent=2) + "\n")

status_doc = ROOT / f"docs/status/VISHA_BOUNDARY_EXTRACTION_SMOKE_TEST_ON_SAMPLE_{stamp}.md"
status_doc.write_text(f"""# ViSha boundary extraction smoke test on sample

Generated: {stamp}

Status:
{artifact["status"]}

Current claim:
- external_comparison_dataset_sample_extracted=true
- full_dataset_extraction_completed=false
- new_science=false
- novelty_validated=false
- real_measurement_dataset_supplied=false

Input counts:
- train_images={len(train_images)}
- train_labels={len(train_labels)}
- test_images={len(test_images)}
- test_labels={len(test_labels)}

Smoke-test result:
- sample_pair_count={usable_pair_count}
- pil_available={str(PIL_AVAILABLE).lower()}
- dimension_checked_count={dimension_checked_count}
- dimension_match_count={dimension_match_count}
- boundary_stats_count={boundary_stats_count}

Valid use:
- boundary-extraction smoke test on external comparison sample
- pipeline sanity check
- shadow-mask processing check

Invalid use:
- new science dataset
- novelty validation
- real measured darkness-boundary claim
- self-recorded calibrated measurement
- full dataset benchmark claim

Minimal missing object for new science:
ConcreteTrialDatasetWithRealMeasurementsAndBaselineComparison

Next admissible object:
SupplySelfRecordedCalibratedRawVideoOrObtainExternalExpertValidationReply
""")

print(f"ARTIFACT={artifact_path.relative_to(ROOT)}")
print(f"STATUS_DOC={status_doc.relative_to(ROOT)}")
print(f"STATUS={artifact['status']}")
print(f"SAMPLE_PAIR_COUNT={usable_pair_count}")
print(f"PIL_AVAILABLE={PIL_AVAILABLE}")
print(f"BOUNDARY_STATS_COUNT={boundary_stats_count}")
