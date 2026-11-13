import hashlib
import os
import shutil
import sys


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as image_file:
        for chunk in iter(lambda: image_file.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(message):
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def image_dimensions(path, signature):
    with open(path, "rb") as image_file:
        data = image_file.read()

    if signature.startswith(b"\x89PNG\r\n\x1a\n"):
        if len(data) < 24 or data[12:16] != b"IHDR":
            raise ValueError("PNG image has no valid IHDR header")
        return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")

    position = 2
    sof_markers = {
        0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
        0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF,
    }
    while position < len(data):
        if data[position] != 0xFF:
            raise ValueError("JPEG image has an invalid marker")
        while position < len(data) and data[position] == 0xFF:
            position += 1
        if position >= len(data):
            break
        marker = data[position]
        position += 1
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7 or marker == 0x01:
            continue
        if position + 2 > len(data):
            break
        segment_length = int.from_bytes(data[position:position + 2], "big")
        if segment_length < 2 or position + segment_length > len(data):
            raise ValueError("JPEG image has an invalid segment")
        if marker in sof_markers:
            if segment_length < 7:
                raise ValueError("JPEG image has an incomplete SOF segment")
            height = int.from_bytes(data[position + 3:position + 5], "big")
            width = int.from_bytes(data[position + 5:position + 7], "big")
            return width, height
        position += segment_length
    raise ValueError("JPEG image has no supported SOF dimensions")


def main():
    source_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    output_path = os.path.join(output_dir, "entry.png")

    try:
        source_size = os.path.getsize(source_path)
    except OSError as error:
        fail(f"cannot access source image {source_path}: {error}")

    if source_size > 1048576:
        fail(f"source image is larger than 1048576 bytes ({source_size} bytes)")

    try:
        os.makedirs(output_dir, exist_ok=True)
        shutil.copyfile(source_path, output_path)
    except OSError as error:
        fail(f"could not copy image to {output_path}: {error}")

    try:
        copied_size = os.path.getsize(output_path)
        source_sha256 = sha256_file(source_path)
        copied_sha256 = sha256_file(output_path)
    except OSError as error:
        fail(f"could not verify copied image: {error}")

    if copied_size != source_size or copied_sha256 != source_sha256:
        fail("copied image does not match the source")

    try:
        with open(output_path, "rb") as image_file:
            signature = image_file.read(8)
    except OSError as error:
        fail(f"could not read copied image {output_path}: {error}")

    if not (signature.startswith(b"\x89PNG\r\n\x1a\n") or signature.startswith(b"\xff\xd8\xff")):
        fail("copied image has an unsupported file signature")

    try:
        width, height = image_dimensions(output_path, signature)
    except (OSError, ValueError) as error:
        fail(f"could not read image dimensions: {error}")

    if width > 1024 or height > 1024:
        fail(f"image dimensions exceed 1024 pixels ({width}x{height})")

    print(f"Wrote {output_path} ({copied_size} bytes, sha256 {copied_sha256})")


if __name__ == "__main__":
    main()
