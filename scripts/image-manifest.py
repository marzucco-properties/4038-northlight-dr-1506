#!/usr/bin/env python3
"""Machine-readable before/after image manifest with hard byte ceilings."""
from __future__ import annotations
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
originals = root / "photos/original"
optimized = root / "photos/optimized"
items = []
violations = []
for original in sorted(originals.glob("*.jpg")):
    variants = {}
    widths = (480, 960, 1600, 1920) if original.stem == "mls-01" else (480, 960, 1600)
    for width in widths:
        variants[str(width)] = {}
        for extension in ("jpg", "webp"):
            derivative = optimized / f"{original.stem}-{width}.{extension}"
            size = derivative.stat().st_size
            ceiling = 120_000 if width == 480 else 400_000
            variants[str(width)][extension] = size
            if size >= ceiling:
                violations.append({"file": derivative.name, "bytes": size, "ceiling": ceiling})
    items.append({"name": original.name, "original_bytes": original.stat().st_size, "variants": variants})

manifest = {
    "ceilings_bytes": {"480": 120_000, "1600_and_hero_1920": 400_000},
    "original_count": len(items),
    "before_original_total_bytes": sum(item["original_bytes"] for item in items),
    "generated_variant_count": len(list(optimized.glob("*"))),
    "generated_variant_total_bytes": sum(path.stat().st_size for path in optimized.glob("*") if path.is_file()),
    "hero_before_bytes": (originals / "mls-01.jpg").stat().st_size,
    "hero_after_primary_1920_webp_bytes": (optimized / "mls-01-1920.webp").stat().st_size,
    "violations": violations,
    "images": items,
}
print(json.dumps(manifest, indent=2, sort_keys=True))
raise SystemExit(1 if violations else 0)
