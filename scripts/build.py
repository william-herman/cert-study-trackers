#!/usr/bin/env python3
"""Build every data/*.yaml into docs/<slug>/index.html and refresh docs/index.html.

Usage: python3 scripts/build.py      (needs PyYAML: pip install pyyaml)
"""
import datetime as dt
import html
import json
import urllib.parse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA, TEMPLATE, DOCS = ROOT / "data", ROOT / "template", ROOT / "docs"
REPO = "https://github.com/william-herman/cert-study-trackers"
SITE = "william-herman.github.io/cert-study-trackers"

REQUIRED = ["slug", "code", "name", "issuer", "category", "kind", "confidence", "blueprint", "last_checked", "summary", "sections", "sources"]
KINDS = {"exam", "path"}
# Index tabs, in display order (an "All" tab is always added first).
CATEGORIES = {"project-management": "Project Management", "ai": "AI", "cybersecurity": "Cybersecurity & Networking"}
TIERS = {"field-validated": "Field-validated", "source-traced": "Source-traced", "peer-reviewed": "Peer-reviewed"}


def validate(cert, path):
    errs = [f"missing field '{k}'" for k in REQUIRED if k not in cert]
    if errs:
        return errs
    if cert["slug"] != path.stem:
        errs.append(f"slug '{cert['slug']}' doesn't match file name '{path.stem}'")
    if cert["category"] not in CATEGORIES:
        errs.append(f"category must be one of {sorted(CATEGORIES)}")
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
    weights = [d.get("weight") for d in cert.get("domains", [])]
    if any(w is not None for w in weights):
        if any(w is None for w in weights):
            errs.append("either every domain has a weight or none do")
        # Issuers sometimes publish rounded weights (ISC2 CC sums to 99.9), so allow a small tolerance.
        elif abs(sum(weights) - 100) > 0.2:
            total = round(sum(weights), 1)
            errs.append(f"domain weights add to {total}, not 100")
    return errs


def write_review_form(certs):
    """Regenerate the peer-review issue form so its tracker list always matches data/."""
    options = [f'{c["code"]}: {c["name"]}' for c in sorted(certs, key=lambda c: c["code"])]
    form = {
        "name": "Peer review a tracker",
        "description": "Hold one of these certifications? Check its tracker against your experience.",
        "title": "[CODE] Peer review",
        "labels": ["peer-review"],
        "body": [
            {"type": "markdown", "attributes": {"value": (
                "Thanks for reviewing! Trackers are built from each certifying body's official sources. "
                "Your review helps confirm they match what the exam actually tests.\n\n"
                "**Please don't share actual exam questions or answers.** Certification exams are under NDA; "
                "describe topics and patterns instead. Reviews that include exam content will be deleted.")}},
            {"type": "dropdown", "id": "tracker", "attributes": {"label": "Which tracker are you reviewing?", "options": options},
             "validations": {"required": True}},
            {"type": "dropdown", "id": "holds", "attributes": {"label": "Do you hold this certification?",
             "options": ["Yes, it's current", "Yes, but it has lapsed", "No, but I've taken the exam", "No"]},
             "validations": {"required": True}},
            {"type": "input", "id": "passed", "attributes": {"label": "When did you pass it?",
             "description": "Month and year is enough. It tells us which exam version you're comparing against.",
             "placeholder": "e.g. March 2026"}},
            {"type": "dropdown", "id": "accuracy", "attributes": {"label": "Overall, how well does the tracker match the exam?",
             "options": ["Matches well", "Mostly matches, with a few gaps", "Significant gaps or errors"]},
             "validations": {"required": True}},
            {"type": "textarea", "id": "issues", "attributes": {"label": "What's wrong, outdated or missing?",
             "description": "Point to the section or item where you can. Link an official source if something changed."},
             "validations": {"required": True}},
            {"type": "textarea", "id": "insights", "attributes": {"label": "What did the exam emphasize? (optional)",
             "description": "Patterns and topics only, e.g. which areas felt heavier than the guide suggests. These can go in the tracker's lens box."}},
            {"type": "dropdown", "id": "credit", "attributes": {"label": "May we credit you on the tracker?",
             "options": ["Yes, by name", "Yes, by name with my LinkedIn", "No, keep me anonymous"]},
             "validations": {"required": True}},
            {"type": "input", "id": "name", "attributes": {"label": "Name and LinkedIn (if you'd like credit)"}},
            {"type": "checkboxes", "id": "terms", "attributes": {"label": "Confirm", "options": [
                {"label": "My review contains no actual exam questions or answers.", "required": True},
                {"label": "My suggestions may be published in the trackers under CC BY 4.0.", "required": True}]}},
        ],
    }
    dest = ROOT / ".github" / "ISSUE_TEMPLATE" / "peer-review.yml"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("# Generated by scripts/build.py from data/. Edit the build script, not this file.\n"
                    + yaml.safe_dump(form, sort_keys=False, allow_unicode=True, width=1000), encoding="utf-8")


def share_data(certs):
    """Compact per-tracker id lists for the share image: required items, grouped by section."""
    out = []
    for c in certs:
        secs = [{"title": s.get("short") or s["title"],
                 "ids": [i["id"] for g in s["groups"] for i in g["items"] if i.get("tag") != "optional"]} for s in c["sections"]]
        obj = c.get("objectives") or {}
        if obj.get("items"):
            secs.append({"title": obj.get("title", "Coverage"), "ids": ["ts-" + str(o["id"]) for o in obj["items"]]})
        out.append({"slug": c["slug"], "code": c["code"], "name": c["name"], "category": c["category"],
                    "ids": [i for s in secs for i in s["ids"]], "sections": secs})
    return json.dumps(out, ensure_ascii=False).replace("</", "<\\/")


def fmt_date(ymd):
    d = dt.date.fromisoformat(ymd)
    return f"{d:%b} {d.day}, {d.year}"


def count(cert):
    n = sum(1 for s in cert["sections"] for g in s["groups"] for i in g["items"] if i.get("tag") != "optional")
    return n + len((cert.get("objectives") or {}).get("items", []))


def main():
    css = (TEMPLATE / "tracker.css").read_text(encoding="utf-8")
    icon = "data:image/svg+xml," + urllib.parse.quote((TEMPLATE / "icon.svg").read_text(encoding="utf-8").strip(), safe=" /:=',")
    head = (TEMPLATE / "head.html").read_text(encoding="utf-8").replace("{{ICON}}", icon)
    share = (TEMPLATE / "share.html").read_text(encoding="utf-8")
    toggle = (TEMPLATE / "toggle.html").read_text(encoding="utf-8")
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
        out = (page.replace("{{HEAD}}", head).replace("{{TOGGLE}}", toggle).replace("{{CSS}}", css)
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
        f'<a class="card" data-cat="{c["category"]}" data-slug="{html.escape(c["slug"])}" href="{html.escape(c["slug"])}/">'
        f'<span class="issuer">{html.escape(c["issuer"])}</span>'
        f'<h2><span class="ccode">{html.escape(c["code"])}</span><span class="cname">{html.escape(c["name"])}</span></h2>'
        f'<p class="sum">{html.escape(c["summary"])}</p>'
        f'<span class="prog"><span class="pbar" role="progressbar" aria-label="Your progress in {html.escape(c["code"])}" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><i></i></span>'
        f'<span class="ptxt none">Not started</span></span>'
        f'<span class="meta-row"><span class="tier {c["confidence"]}">{TIERS[c["confidence"]]}</span>'
        f'<span>{count(c)} items</span><span>Checked {fmt_date(c["last_checked"])}</span></span></a>'
        for c in sorted(certs, key=lambda c: (c["issuer"], c["code"]))
    )
    review_opts = "".join(f'<option value="{html.escape(c["code"])}">{html.escape(c["code"])}: {html.escape(c["name"])}</option>'
                          for c in sorted(certs, key=lambda c: c["code"]))
    tabs = f'<button type="button" class="tab" data-cat="all">All<span class="k">{len(certs)}</span></button>' + "".join(
        f'<button type="button" class="tab" data-cat="{k}">{v}<span class="k">{sum(c["category"] == k for c in certs)}</span></button>'
        for k, v in CATEGORIES.items())
    (DOCS / "index.html").write_text(index_tpl.replace("{{HEAD}}", head).replace("{{TOGGLE}}", toggle).replace("{{CSS}}", css)
                                     .replace("{{SHARE}}", share.replace("{{SHARE_DATA}}", share_data(certs)).replace("{{SITE}}", SITE))
                                     .replace("{{ICON}}", icon).replace("{{SHARE_DATA}}", share_data(certs)).replace("{{TABS}}", tabs).replace("{{CARDS}}", cards).replace("{{REVIEW_OPTIONS}}", review_opts)
                                     .replace("{{REPO}}", REPO), encoding="utf-8")
    write_review_form(certs)
    print("OK .github/ISSUE_TEMPLATE/peer-review.yml")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print(f"OK docs/index.html ({len(certs)} trackers)")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
