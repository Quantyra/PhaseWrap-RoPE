from __future__ import annotations

from pathlib import Path

from scripts.export_publication_paper import export_publication_paper, markdown_to_html


def test_markdown_to_html_handles_paper_structures() -> None:
    markdown = """# Title

![Alt text](figures/example.png)

| A | B |
| --- | ---: |
| `x` | **y** |

```text
code < value
```
"""

    html = markdown_to_html(markdown)

    assert '<h1 id="title">Title</h1>' in html
    assert '<img src="figures/example.png" alt="Alt text">' in html
    assert "<table>" in html
    assert "<code>x</code>" in html
    assert "<strong>y</strong>" in html
    assert "code &lt; value" in html


def test_export_publication_paper_writes_current_full_replacement_paper(tmp_path: Path) -> None:
    output = tmp_path / "qrope-paper-v1.html"

    export_publication_paper(output_path=output)

    html = output.read_text(encoding="utf-8")
    assert "<!doctype html>" in html
    assert "PhaseWrap-RoPE" in html
    assert "FULL_REPLACEMENT_HARDWARE_POSITIVE_PHASEWRAP_ADVANTAGE" in html
    assert "qrope-full-replacement-metrics-v1.png" in html
    assert "Production transformer improvement" in html
    assert "crn:v1" not in html
