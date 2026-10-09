# Cert Study Trackers

Free, interactive study trackers for professional certifications. Each tracker is a checklist you can tick off in the browser, built from the certifying body's own exam guide or requirements page, and labeled by how well it has been validated.

**Open the trackers:** https://william-herman.github.io/cert-study-trackers/

**Project Management**

| Certification | Issuer | Confidence |
|---|---|---|
| [PMP: Project Management Professional](https://william-herman.github.io/cert-study-trackers/pmp/) | PMI | Source-traced |
| [PAL-I: Professional Agile Leadership I](https://william-herman.github.io/cert-study-trackers/pal-i/) | Scrum.org | Field-validated |
| [CSM: Certified ScrumMaster](https://william-herman.github.io/cert-study-trackers/csm/) | Scrum Alliance | Field-validated |
| [RS@SP: Registered Scrum@Scale Practitioner](https://william-herman.github.io/cert-study-trackers/scrum-at-scale/) | Scrum Inc. | Source-traced |

**AI**

| Certification | Issuer | Confidence |
|---|---|---|
| [CCAO-F: Claude Certified Associate – Foundations](https://william-herman.github.io/cert-study-trackers/ccao-f/) | Anthropic | Source-traced |
| [CCAR-F: Claude Certified Architect – Foundations](https://william-herman.github.io/cert-study-trackers/ccar-f/) | Anthropic | Source-traced |
| [CCAR-P: Claude Certified Architect – Professional](https://william-herman.github.io/cert-study-trackers/ccar-p/) | Anthropic | Source-traced |
| [CCDV-F: Claude Certified Developer – Foundations](https://william-herman.github.io/cert-study-trackers/ccdv-f/) | Anthropic | Source-traced |
| [AIF-C01: AWS Certified AI Practitioner](https://william-herman.github.io/cert-study-trackers/aif-c01/) | AWS | Source-traced |
| [GAIL: Google Cloud Certified Generative AI Leader](https://william-herman.github.io/cert-study-trackers/gail/) | Google Cloud | Source-traced |

**Cybersecurity & Networking**

| Certification | Issuer | Confidence |
|---|---|---|
| [N10-009: CompTIA Network+](https://william-herman.github.io/cert-study-trackers/n10-009/) | CompTIA | Source-traced |
| [SY0-801: CompTIA Security+ (V8)](https://william-herman.github.io/cert-study-trackers/sy0-801/) | CompTIA | Source-traced |
| [CC: ISC2 Certified in Cybersecurity](https://william-herman.github.io/cert-study-trackers/isc2-cc/) | ISC2 | Source-traced |
| [CCNA: Cisco Certified Network Associate (v2.0)](https://william-herman.github.io/cert-study-trackers/ccna/) | Cisco | Source-traced |

More are on the way, including CSP-PO.

## How much to trust each tracker

- **Field-validated:** the author passed the certification and checked the list against that experience.
- **Source-traced:** built from the official sources and not yet tested by an exam attempt. Read it as a structured version of the blueprint.
- **Peer-reviewed:** built from official sources and reviewed by someone who holds the certification.

Every tracker shows which version of the official guide it traces to and the date it was last checked. If a tracker and the official guide disagree, the guide wins.

## What's not here

No exam questions, brain dumps or recalled exam content. Certification exams are under NDA, and these trackers only restructure what the certifying bodies publish openly.

## Hold one of these certifications?

[Peer-review a tracker](https://github.com/william-herman/cert-study-trackers/issues/new?template=peer-review.yml): tell us what matches the exam, what's missing, and whether you'd like credit. Trackers move to **peer-reviewed** once a certification holder has checked them.

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

Not affiliated with or endorsed by Anthropic, AWS, Google, CompTIA, ISC2, Cisco, PMI, Scrum.org, Scrum Alliance, Scrum Inc. or any other certification body. Certification names are trademarks of their owners.
