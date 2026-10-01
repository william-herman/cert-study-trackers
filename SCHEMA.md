# Cert data format

Each certification is one YAML file in `data/`. `python3 scripts/build.py` turns every file into an interactive tracker at `docs/<slug>/index.html` and refreshes the index page at `docs/index.html`.

Text fields accept light Markdown: `**bold**`, `*italic*`, `` `code` ``, `[link](https://…)`.

## Top-level fields

| Field | Required | Notes |
|---|---|---|
| `slug` | yes | URL folder name, lowercase with hyphens (`ccar-f`). Must match the file name. |
| `code` | yes | Short code shown in the header (`CCAR-F`). |
| `name` | yes | Full certification name. |
| `issuer` | yes | Certifying body (`Anthropic`, `AWS`, `Scrum.org`, `Scrum Alliance`). |
| `kind` | yes | `exam` (blueprint with weighted domains) or `path` (earned through courses, experience and prerequisites). |
| `confidence` | yes | `field-validated` (author passed it), `source-traced` (built from official sources, not yet tested), or `peer-reviewed` (checked by a holder). |
| `blueprint` | yes | `title`, `version`, `published` of the official document the checklist traces to. For `path` certs, the requirements page. |
| `last_checked` | yes | `YYYY-MM-DD` date the official sources were last compared against this file. |
| `summary` | yes | One or two sentences for the index page. |
| `snapshot` | no | `title` plus `items`: key facts (format, length, passing score, cost, validity). |
| `lens` | no | `title`, optional `intro` (one line above the bullets), `body` (a list of bullets, or one paragraph), `prompts`: the mindset that helps across questions. |
| `domains` | no | Exam domains: `id`, `name`, `short` (meter label), optional `weight` (percent), optional `label` (overrides the "Domain N" text, e.g. `Foundations`). Give every domain a weight (summing to 100) or none, e.g. when the issuer doesn't publish weights. Omit entirely for `path` certs; the progress meters are hidden. |
| `domain_label` | no | What the issuer calls a domain (default `Domain`; e.g. `Focus area`). |
| `tag_legend` | no | `tag`, `style` (`ex`, `added`, `optional`), `meaning`. Shown in the footer. |
| `sections` | yes | See below. |
| `objectives` | no | Coverage grid: `title`, `note`, `items` of `id` (e.g. `1.1`), `name`, `where`. Each objective counts toward the domain matching its leading number, or the one named by its optional `domain` field. |
| `sources` | yes | Official links: `title`, `url`, optional `note`. At least one. |

## Sections

```yaml
sections:
- id: s2            # unique, used for anchors
  no: '2'           # shown as §2
  title: Agentic Architecture & Orchestration
  short: Agentic    # optional shorter nav label
  domain: 1         # optional; links the section to a domain meter
  note: The highest-weighted domain.     # optional
  callout: Highlighted warning text      # optional
  groups:
  - title: Concepts to own               # optional group heading
    items:
    - id: d1-1                           # unique across the file; keeps saved progress stable
      text: Agentic loop
      ts: '1.1'                          # optional objective/task-statement badge
      tag: Ex1                           # optional; `optional` items don't count toward progress
      sub:                               # optional bullet details
      - Continue on `stop_reason`…
  skip: [ … ]                            # optional "skip or skim" list
  out_of_scope: [ … ]                    # optional "don't study these" list
```

## Rules the build checks

- All required fields are present, and `kind` and `confidence` use allowed values.
- Item and objective ids are unique within a file.
- `last_checked` is a valid date. The page shows a warning when it is more than 180 days old.
- No item text may come from real exam questions. That one can't be checked by the build; it's on the author.

Changing an item's `id` resets anyone's saved tick for that item, so reword the text instead.
