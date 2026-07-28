"""Parse and apply snip region anchors."""

from __future__ import annotations

import re
from dataclasses import dataclass

# Comment prefix + >>> snip:id=NAME path=... ref=...
_BEGIN_RE = re.compile(
    r"^(?P<prefix>\s*(?:#|//|;|--)?\s*)"
    r">>>\s*snip:id=(?P<id>[^\s]+)"
    r"(?P<meta>(?:\s+\w+=\S+)*)\s*$"
)
_END_RE = re.compile(
    r"^(?P<prefix>\s*(?:#|//|;|--)?\s*)"
    r"<<<\s*snip:id=(?P<id>[^\s]+)\s*$"
)
_META_RE = re.compile(r"(\w+)=(\S+)")


@dataclass
class Anchor:
    id: str
    path: str | None
    ref: str | None
    start_line: int  # 0-based index of begin marker
    end_line: int  # 0-based index of end marker
    begin_text: str
    end_text: str
    prefix: str

    @property
    def body_lines(self) -> slice:
        return slice(self.start_line + 1, self.end_line)


def _parse_meta(meta: str) -> dict[str, str]:
    return {k: v for k, v in _META_RE.findall(meta or "")}


def parse_anchors(text: str) -> list[Anchor]:
    lines = text.splitlines(keepends=True)
    anchors: list[Anchor] = []
    open_anchor: dict | None = None

    for i, line in enumerate(lines):
        stripped = line.rstrip("\n")
        m_begin = _BEGIN_RE.match(stripped)
        if m_begin:
            meta = _parse_meta(m_begin.group("meta"))
            open_anchor = {
                "id": m_begin.group("id"),
                "path": meta.get("path"),
                "ref": meta.get("ref"),
                "start_line": i,
                "begin_text": line,
                "prefix": m_begin.group("prefix"),
            }
            continue
        m_end = _END_RE.match(stripped)
        if m_end and open_anchor and m_end.group("id") == open_anchor["id"]:
            anchors.append(
                Anchor(
                    id=open_anchor["id"],
                    path=open_anchor["path"],
                    ref=open_anchor["ref"],
                    start_line=open_anchor["start_line"],
                    end_line=i,
                    begin_text=open_anchor["begin_text"],
                    end_text=line,
                    prefix=open_anchor["prefix"],
                )
            )
            open_anchor = None
    return anchors


def get_body(text: str, anchor: Anchor) -> str:
    lines = text.splitlines(keepends=True)
    return "".join(lines[anchor.body_lines])


def replace_body(text: str, anchor: Anchor, new_body: str, *, new_ref: str | None = None) -> str:
    lines = text.splitlines(keepends=True)
    body = new_body
    if body and not body.endswith("\n"):
        body += "\n"
    begin = anchor.begin_text
    if new_ref is not None:
        begin = _bump_ref(begin, new_ref)
    if not begin.endswith("\n"):
        begin += "\n"
    body_lines = body.splitlines(keepends=True)
    new_lines = lines[: anchor.start_line] + [begin] + body_lines + lines[anchor.end_line :]
    return "".join(new_lines)


def _bump_ref(begin_line: str, new_ref: str) -> str:
    if re.search(r"\bref=", begin_line):
        return re.sub(r"\bref=\S+", f"ref={new_ref}", begin_line)
    # insert before EOL
    return begin_line.rstrip("\n") + f" ref={new_ref}\n"


@dataclass
class FileHeader:
    template_source: str | None = None
    curr_version: str | None = None


def parse_file_header(text: str) -> FileHeader:
    source = None
    version = None
    for line in text.splitlines()[:40]:
        if "Template source:" in line:
            source = line.split("Template source:", 1)[1].strip()
        if "curr_version:" in line:
            version = line.split("curr_version:", 1)[1].strip()
    return FileHeader(template_source=source, curr_version=version)
