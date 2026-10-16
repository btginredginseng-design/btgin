"""Build cafe24/qr/index.html from index.src.html by embedding the logo.

Edit index.src.html (and img/btgin-logo.webp), then run:  python3 cafe24/qr/build.py
"""
import base64, pathlib

here = pathlib.Path(__file__).parent
logo = base64.b64encode((here / "img" / "btgin-logo.webp").read_bytes()).decode()
src = (here / "index.src.html").read_text(encoding="utf-8")
(here / "index.html").write_text(src.replace("{{LOGO}}", logo), encoding="utf-8")
print("wrote", here / "index.html")
