from __future__ import annotations

import html
import re
from pathlib import Path


DEFAULT_INPUT = Path("docs") / "publication" / "qrope-paper-v1.md"
DEFAULT_OUTPUT = Path("docs") / "publication" / "qrope-paper-v1.html"

_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
_BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
_CODE_RE = re.compile(r"`([^`]+)`")


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "section"


def _inline(text: str) -> str:
    placeholders: list[str] = []

    def stash(value: str) -> str:
        placeholders.append(value)
        return f"\u0000{len(placeholders) - 1}\u0000"

    escaped = html.escape(text, quote=False)
    escaped = _IMAGE_RE.sub(lambda match: stash(f'<img src="{html.escape(match.group(2), quote=True)}" alt="{html.escape(match.group(1), quote=True)}">'), escaped)
    escaped = _LINK_RE.sub(lambda match: stash(f'<a href="{html.escape(match.group(2), quote=True)}">{match.group(1)}</a>'), escaped)
    escaped = _BOLD_RE.sub(lambda match: f"<strong>{match.group(1)}</strong>", escaped)
    escaped = _CODE_RE.sub(lambda match: f"<code>{match.group(1)}</code>", escaped)
    for index, value in enumerate(placeholders):
        escaped = escaped.replace(f"\u0000{index}\u0000", value)
    return escaped


def _table_html(rows: list[str]) -> str:
    parsed = [[cell.strip() for cell in row.strip().strip("|").split("|")] for row in rows]
    if len(parsed) < 2:
        return "\n".join(f"<p>{_inline(row)}</p>" for row in rows)
    header = parsed[0]
    body = parsed[2:] if all(set(cell) <= {"-", ":"} and "-" in cell for cell in parsed[1]) else parsed[1:]
    parts = ["<table>", "<thead><tr>"]
    parts.extend(f"<th>{_inline(cell)}</th>" for cell in header)
    parts.append("</tr></thead>")
    parts.append("<tbody>")
    for row in body:
        parts.append("<tr>")
        parts.extend(f"<td>{_inline(cell)}</td>" for cell in row)
        parts.append("</tr>")
    parts.append("</tbody></table>")
    return "\n".join(parts)


def markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    output: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    table_rows: list[str] = []
    in_code = False
    code_language = ""
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            output.append(f"<p>{_inline(' '.join(part.strip() for part in paragraph))}</p>")
            paragraph.clear()

    def flush_list() -> None:
        if list_items:
            output.append("<ul>")
            output.extend(f"<li>{_inline(item)}</li>" for item in list_items)
            output.append("</ul>")
            list_items.clear()

    def flush_table() -> None:
        if table_rows:
            output.append(_table_html(table_rows))
            table_rows.clear()

    for line in lines:
        if line.startswith("```"):
            if in_code:
                output.append(f'<pre><code class="language-{html.escape(code_language, quote=True)}">{html.escape(chr(10).join(code_lines))}</code></pre>')
                in_code = False
                code_language = ""
                code_lines.clear()
            else:
                flush_paragraph()
                flush_list()
                flush_table()
                in_code = True
                code_language = line.removeprefix("```").strip()
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line.strip():
            flush_paragraph()
            flush_list()
            flush_table()
            continue
        if line.lstrip().startswith("|") and line.rstrip().endswith("|"):
            flush_paragraph()
            flush_list()
            table_rows.append(line)
            continue
        flush_table()
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            flush_list()
            level = len(heading.group(1))
            text = heading.group(2).strip()
            output.append(f'<h{level} id="{_slug(text)}">{_inline(text)}</h{level}>')
            continue
        unordered = re.match(r"^\s*-\s+(.+)$", line)
        if unordered:
            flush_paragraph()
            list_items.append(unordered.group(1).strip())
            continue
        paragraph.append(line)

    flush_paragraph()
    flush_list()
    flush_table()
    if in_code:
        output.append(f'<pre><code class="language-{html.escape(code_language, quote=True)}">{html.escape(chr(10).join(code_lines))}</code></pre>')
    return "\n".join(output)


def export_publication_paper(input_path: Path = DEFAULT_INPUT, output_path: Path = DEFAULT_OUTPUT) -> Path:
    markdown = input_path.read_text(encoding="utf-8")
    body = markdown_to_html(markdown)
    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PhaseWrap-RoPE Paper</title>
  <style>
    :root {{ color-scheme: light; }}
    body {{
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.55;
      color: #1b1f23;
      background: #ffffff;
      margin: 0 auto;
      max-width: 980px;
      padding: 40px 28px 72px;
    }}
    h1, h2, h3, h4 {{ line-height: 1.2; margin-top: 1.7em; }}
    h1 {{ font-size: 2rem; margin-top: 0; }}
    h2 {{ border-bottom: 1px solid #d8dee4; padding-bottom: 0.25rem; }}
    p, li {{ font-size: 1rem; }}
    a {{ color: #0969da; }}
    code {{
      background: #f6f8fa;
      border-radius: 4px;
      padding: 0.1rem 0.25rem;
      font-family: Consolas, Monaco, monospace;
      font-size: 0.92em;
    }}
    pre {{
      background: #f6f8fa;
      overflow-x: auto;
      padding: 1rem;
      border-radius: 6px;
      border: 1px solid #d8dee4;
    }}
    pre code {{ background: transparent; padding: 0; }}
    table {{
      border-collapse: collapse;
      width: 100%;
      margin: 1rem 0 1.4rem;
      font-size: 0.9rem;
    }}
    th, td {{ border: 1px solid #d8dee4; padding: 0.45rem 0.55rem; vertical-align: top; }}
    th {{ background: #f6f8fa; text-align: left; }}
    img {{ max-width: 100%; height: auto; display: block; margin: 1rem auto; }}
    @media print {{
      body {{ max-width: none; padding: 24px; }}
      a {{ color: #1b1f23; text-decoration: none; }}
      h2 {{ break-after: avoid; }}
      table, pre, img {{ break-inside: avoid; }}
    }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding="utf-8")
    return output_path


def main() -> None:
    path = export_publication_paper()
    print(path.as_posix())


if __name__ == "__main__":
    main()
