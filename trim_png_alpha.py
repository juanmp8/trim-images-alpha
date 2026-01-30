"""
Recorte bordas transparentes de imagens PNG o mais próximo possível.

Uso:
python trim_png_alpha.py <input_path> [--out OUT_DIR] [--threshold A] [--padding P]
[--recursive] [--overwrite] [--keep-structure] [--dry-run]

Exemplos:
# Arquivo único
python trim_png_alpha.py "planta.png"

# Todos os PNGs em uma pasta (recursivamente), gravar em ./trimmed com preenchimento de 8px
python trim_png_alpha.py "./plantas" --recursive --padding 8
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageChops
import numpy as np


def compute_bbox_rgba(img: Image.Image, alpha_threshold: int) -> Optional[Tuple[int, int, int, int]]:
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    arr = np.asarray(img)  # H x W x 4
    alpha = arr[..., 3]
    mask = alpha > alpha_threshold
    if not mask.any():
        return None

    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]
    top, bottom = rows[0], rows[-1]
    left, right = cols[0], cols[-1]
    # Pillow crop box is (left, upper, right+1, lower+1)
    return (int(left), int(top), int(right) + 1, int(bottom) + 1)


def compute_bbox_no_alpha(img: Image.Image, bg_tolerance: int = 5) -> Optional[Tuple[int, int, int, int]]:
    """
    Fallback for images without alpha: assume near-white background and crop content.
    bg_tolerance: 0..255 (0 exact white; higher tolerates near-white).
    Returns crop box or None if cannot compute.
    """
    # Convert to RGB, compute difference from white, take bbox of non-zero
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    if img.mode == "RGB":
        # Distance from white per pixel (max over channels)
        arr = np.asarray(img, dtype=np.uint8)
        diff = 255 - arr  # how far from white
        max_diff = diff.max(axis=2)
    else:
        arr = np.asarray(img, dtype=np.uint8)
        max_diff = 255 - arr

    mask = max_diff > bg_tolerance
    if not mask.any():
        return None

    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]
    top, bottom = rows[0], rows[-1]
    left, right = cols[0], cols[-1]
    return (int(left), int(top), int(right) + 1, int(bottom) + 1)


def add_padding(box: Tuple[int, int, int, int], padding: int, width: int, height: int) -> Tuple[int, int, int, int]:
    if padding <= 0:
        return box
    l, t, r, b = box
    l = max(0, l - padding)
    t = max(0, t - padding)
    r = min(width, r + padding)
    b = min(height, b + padding)
    return (l, t, r, b)


def trim_image(path: Path, out_path: Path, alpha_threshold: int, padding: int, overwrite: bool) -> Tuple[bool, str]:
    try:
        with Image.open(path) as im:
            orig_mode = im.mode
            width, height = im.size
            info = im.info.copy()

            # Prefer alpha-based crop, else try heuristic
            box = None
            if "A" in Image.Image.getbands(im):
                box = compute_bbox_rgba(im, alpha_threshold)

            if box is None:
                box = compute_bbox_no_alpha(im, bg_tolerance=5)

            if box is None:
                return False, f"Skipped (no content detected): {path.name}"

            box = add_padding(box, padding, width, height)

            if box == (0, 0, width, height):
                # Nothing to crop
                if not overwrite and out_path.exists():
                    return True, f"No crop needed (already tight): {path.name}"
                # Save a copy anyway
                cropped = im.copy()
            else:
                cropped = im.crop(box)

            # Ensure PNG with alpha if original had it; preserve transparency where possible
            save_params = {}
            if orig_mode in ("RGBA", "LA") or ("transparency" in info):
                cropped = cropped.convert("RGBA")
            else:
                cropped = cropped.convert("RGB")

            # Preserve resolution/dpi if present
            if "dpi" in info:
                save_params["dpi"] = info["dpi"]

            out_path.parent.mkdir(parents=True, exist_ok=True)
            cropped.save(out_path, format="PNG", **save_params)
            return True, f"Cropped: {path.name} -> {out_path.relative_to(out_path.parent.parent) if out_path.parent.parent in out_path.parents else out_path.name}"
    except Exception as e:
        return False, f"Error {path.name}: {e}"


def gather_inputs(input_path: Path, recursive: bool) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    patterns = ["*.png", "*.PNG"]
    files = []
    if recursive:
        for pat in patterns:
            files.extend(input_path.rglob(pat))
    else:
        for pat in patterns:
            files.extend(input_path.glob(pat))
    return files


def main():
    parser = argparse.ArgumentParser(description="Trim transparent borders from PNGs.")
    parser.add_argument("input_path", type=str, help="Path to a PNG file or a directory containing PNGs.")
    parser.add_argument("--out", dest="out_dir", type=str, default=None,
                        help="Output directory. Defaults to '<input_dir>/trimmed' or '<file_dir>/trimmed'.")
    parser.add_argument("--threshold", type=int, default=0,
                        help="Alpha threshold (0..254). Pixels with alpha > threshold are considered content. Default: 0")
    parser.add_argument("--padding", type=int, default=0, help="Padding (pixels) to keep around content. Default: 0")
    parser.add_argument("--recursive", action="store_true", help="Recurse into subfolders when input is a directory.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite files in output if they exist.")
    parser.add_argument("--keep-structure", action="store_true",
                        help="If input is a directory, replicate subfolder structure into output.")
    parser.add_argument("--dry-run", action="store_true", help="Scan and show planned crops without writing files.")

    args = parser.parse_args()

    in_path = Path(args.input_path)
    if not in_path.exists():
        print(f"Input does not exist: {in_path}", file=sys.stderr)
        sys.exit(1)

    inputs = gather_inputs(in_path, args.recursive)
    if not inputs:
        print("No PNG files found.", file=sys.stderr)
        sys.exit(1)

    if args.out_dir is None:
        base = in_path if in_path.is_dir() else in_path.parent
        out_base = base / "trimmed"
    else:
        out_base = Path(args.out_dir)

    total = 0
    success = 0

    for src in inputs:
        total += 1
        if in_path.is_dir() and args.keep_structure:
            rel = src.relative_to(in_path)
            out_path = out_base / rel
        else:
            out_path = out_base / src.name

        if args.dry_run:
            try:
                with Image.open(src) as im:
                    width, height = im.size
                    box = None
                    if "A" in Image.Image.getbands(im):
                        box = compute_bbox_rgba(im, args.threshold)
                    if box is None:
                        box = compute_bbox_no_alpha(im, bg_tolerance=5)
                    if box is None:
                        print(f"[SKIP] {src} -> no content detected")
                        continue
                    box = add_padding(box, args.padding, width, height)
                    print(f"[PLAN] {src} -> crop box {box} (orig {width}x{height} -> new {box[2]-box[0]}x{box[3]-box[1]})")
                    success += 1
            except Exception as e:
                print(f"[ERR ] {src} -> {e}")
            continue

        ok, msg = trim_image(src, out_path, args.threshold, args.padding, args.overwrite)
        if ok:
            success += 1
            print("[ OK ]", msg)
        else:
            print("[FAIL]", msg)

    print(f"\nDone. {success}/{total} processed successfully.")


if __name__ == "__main__":
    main()
