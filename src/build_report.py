"""Inline report/data.json into report/template.html -> report/index.html."""
import pathlib
R = pathlib.Path(__file__).resolve().parents[1] / "report"
(R / "index.html").write_text((R / "template.html").read_text().replace("/*__DATA__*/null", (R / "data.json").read_text()))
print("wrote", R / "index.html")
