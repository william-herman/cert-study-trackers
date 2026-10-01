# Cert Study Trackers

Free, interactive study trackers for professional certifications. Each tracker is a checklist you can tick off in the browser, built from the certifying body's own exam guide or requirements page, and labeled by how well it has been validated.

**Open the trackers:** https://william-herman.github.io/cert-study-trackers/

| Certification | Issuer | Confidence |
|---|---|---|
| [CCAR-F: Claude Certified Architect – Foundations](https://william-herman.github.io/cert-study-trackers/ccar-f/) | Anthropic | Source-traced |

More are on the way: PAL-I, CSM, CSP-PO and AWS Certified Cloud Practitioner.

## How much to trust each tracker

- **Field-validated:** the author passed the certification and checked the list against that experience.
- **Source-traced:** built from the official sources and not yet tested by an exam attempt. Read it as a structured version of the blueprint.
- **Peer-reviewed:** built from official sources and reviewed by someone who holds the certification.

Every tracker shows which version of the official guide it traces to and the date it was last checked. If a tracker and the official guide disagree, the guide wins.

## What's not here

No exam questions, brain dumps or recalled exam content. Certification exams are under NDA, and these trackers only restructure what the certifying bodies publish openly.

## Spotted something outdated?

[Open an issue](https://github.com/william-herman/cert-study-trackers/issues/new?template=outdated-content.md) with a link to the official source that changed.

## How it's built

```
data/<slug>.yaml        one file per certification (format: SCHEMA.md)
template/               shared page template and styles
scripts/build.py        renders data/ into docs/
docs/                   the published site (GitHub Pages serves this folder)
```

To rebuild after editing a data file:

```
pip install pyyaml
python3 scripts/build.py
```

The build checks each file for required fields, duplicate ids and domain weights before writing the pages. Progress ticks are stored in each visitor's browser (localStorage) and never leave their device.

## License

- Checklist content (`data/`, `docs/`): [CC BY 4.0](LICENSE-CONTENT.md). Reuse it freely with credit.
- Code (`scripts/`, `template/`): [MIT](LICENSE).

Not affiliated with or endorsed by Anthropic, AWS, Scrum.org, Scrum Alliance or any other certification body. Certification names are trademarks of their owners.
