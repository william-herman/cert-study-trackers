#!/usr/bin/env python3
"""Build every data/*.yaml into docs/<slug>/index.html and refresh docs/index.html.

Usage: python3 scripts/build.py      (needs PyYAML: pip install pyyaml)
"""
import datetime as dt
import html
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA, TEMPLATE, DOCS = ROOT / "data", ROOT / "template", ROOT / "docs"
REPO = "https://github.com/william-herman/cert-study-trackers"

REQUIRED = ["slug", "code", "name", "issuer", "kind", "confidence", "blueprint", "last_checked", "summary", "sections", "sources"]
KINDS = {"exam", "path"}
TIERS = {"field-validated": "Field-validated", "source-traced": "Source-traced", "peer-reviewed": "Peer-reviewed"}


def validate(cert, path):
    errs = [f"missing field '{k}'" for k in REQUIRED if k not in cert]
    if errs:
        return errs
    if cert["slug"] != path.stem:
        errs.append(f"slug '{cert['slug']}' doesn't match file name '{path.stem}'")
    if cert["kind"] not in KINDS:
        errs.append(f"kind must be one of {sorted(KINDS)}")
    if cert["confidence"] not in TIERS:
        errs.append(f"confidence must be one of {sorted(TIERS)}")
    for k in ("title", "version"):
        if k not in cert["blueprint"]:
            errs.append(f"blueprint.{k} missing")
    try:
        dt.date.fromisoformat(str(cert["last_checked"]))
    except ValueError:
        errs.append("last_checked must be YYYY-MM-DD")
    if not cert["sources"]:
        errs.append("at least one source is required")
    seen, sec_ids = set(), set()
    domain_ids = {d["id"] for d in cert.get("domains", [])}
    for sec in cert["sections"]:
        if sec["id"] in sec_ids:
            errs.append(f"duplicate section id '{sec['id']}'")
        sec_ids.add(sec["id"])
        if "domain" in sec and sec["domain"] not in domain_ids:
            errs.append(f"section '{sec['id']}' points to unknown domain {sec['domain']}")
        for g in sec["groups"]:
            for it in g["items"]:
                if it["id"] in seen:
                    errs.append(f"duplicate item id '{it['id']}'")
                seen.add(it["id"])
    for o in (cert.get("objectives") or {}).get("items", []):
        oid = "ts-" + str(o["id"])
        if oid in seen:
            errs.append(f"duplicate objective id '{o['id']}'")
        seen.add(oid)
    if cert.get("domains"):
        total = sum(d["weight"] for d in cert["domains"])
        if total != 100:
            errs.append(f"domain weights add to {total}, not 100")
    return errs


def count(cert):
    n = sum(1 for s in cert["sections"] for g in s["groups"] for i in g["items"] if i.get("tag") != "optional")
    return n + len((cert.get("objectives") or {}).get("items", []))


def main():
    css = (TEMPLATE / "tracker.css").read_text(encoding="utf-8")
    page = (TEMPLATE / "tracker.html").read_text(encoding="utf-8")
    index_tpl = (TEMPLATE / "index.html").read_text(encoding="utf-8")
    certs, failed = [], False

    for path in sorted(DATA.glob("*.yaml")):
        cert = yaml.safe_load(path.read_text(encoding="utf-8"))
        cert["last_checked"] = str(cert.get("last_checked", ""))
        errs = validate(cert, path)
        if errs:
            failed = True
            print(f"ERROR {path.name}:\n  - " + "\n  - ".join(errs), file=sys.stderr)
            continue
        title = f"{cert['code']} Study Tracker"
        data = json.dumps(cert, ensure_ascii=False).replace("</", "<\\/")
        out = (page.replace("{{CSS}}", css)
                   .replace("{{TITLE}}", html.escape(title))
                   .replace("{{DESCRIPTION}}", html.escape(cert["summary"]))
                   .replace("{{REPO}}", REPO)
                   .replace("{{DATA}}", data))
        dest = DOCS / cert["slug"] / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(out, encoding="utf-8")
        certs.append(cert)
        print(f"OK {path.name} -> docs/{cert['slug']}/  ({count(cert)} checkable items)")

    cards = "".join(
        f'<a class="card" href="{html.escape(c["slug"])}/">'
        f'<span class="code">{html.escape(c["issuer"])} · {html.escape(c["code"])}</span>'
        f'<h2>{html.escape(c["name"])}</h2><p>{html.escape(c["summary"])}</p>'
        f'<span class="row"><span class="tier {c["confidence"]}">{TIERS[c["confidence"]]}</span>'
        f'<span>{count(c)} items · checked {html.escape(c["last_checked"])}</span></span></a>'
        for c in sorted(certs, key=lambda c: (c["issuer"], c["code"]))
    )
    (DOCS / "index.html").write_text(index_tpl.replace("{{CSS}}", css).replace("{{CARDS}}", cards).replace("{{REPO}}", REPO), encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print(f"OK docs/index.html ({len(certs)} trackers)")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()