from pathlib import Path
from textwrap import wrap


PROJECT_DIR = Path(__file__).resolve().parent
INPUT_FILE = PROJECT_DIR / "input.txt"
OUTPUT_FILE = PROJECT_DIR / "generated.pdf"


def pdf_text(value):
    encoded = value.encode("cp1252", errors="replace")
    return encoded.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")


def create_pdf(text):
    lines = []
    for line in text.splitlines():
        lines.extend(wrap(line, width=90) or [""])

    if not lines:
        lines = [""]

    pages = [lines[index:index + 50] for index in range(0, len(lines), 50)]
    objects = [b"", b"<< /Type /Catalog /Pages 2 0 R >>", b"", b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"]
    page_references = []

    for page_lines in pages:
        commands = [b"BT", b"/F1 11 Tf", b"50 742 Td", b"14 TL"]
        for index, line in enumerate(page_lines):
            if index:
                commands.append(b"T*")
            commands.append(b"(" + pdf_text(line) + b") Tj")
        commands.append(b"ET")
        stream = b"\n".join(commands)

        content_id = len(objects)
        objects.append(b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream")
        page_id = len(objects)
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents {content_id} 0 R >>".encode("ascii")
        )
        page_references.append(f"{page_id} 0 R")

    objects[2] = f"<< /Type /Pages /Kids [{' '.join(page_references)}] /Count {len(pages)} >>".encode("ascii")

    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for object_id, body in enumerate(objects[1:], start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{object_id} 0 obj\n".encode("ascii"))
        pdf.extend(body)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects)}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(f"trailer\n<< /Size {len(objects)} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii"))
    return pdf


def main():
    text = INPUT_FILE.read_text(encoding="utf-8")
    OUTPUT_FILE.write_bytes(create_pdf(text))
    print(f"Created {OUTPUT_FILE}")


