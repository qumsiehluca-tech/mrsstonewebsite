# Stone Cold Loans — Website (3 Themes)

A one-page marketing site for a Merchant Cash Advance company, delivered in three
distinct visual themes so you can compare directions before committing.

## Start here

Open **`index.html`** in the root folder. It's a comparison page with previews and
links to all three live themes. Everything works by double-clicking — no setup.

## What's inside

```
stone-cold-loans/
├── index.html              ← comparison / preview page (start here)
├── theme1-fintech/         ← Theme 1: Modern Fintech Authority
├── theme2-wallstreet/      ← Theme 2: Wall Street / Private Capital
├── theme3-industrial/      ← Theme 3: Industrial / Blue-Collar Capital
└── _preview/               ← thumbnail images used by the comparison page
```

Each theme folder is a complete, standalone site:
`index.html` + `styles.css` + `script.js` (Theme 3 also has an `assets/` folder).

## The three themes

1. **Modern Fintech Authority** — dark navy, white cards, emerald/gold accents,
   large serif headlines. Institutional and trustworthy.
2. **Wall Street / Private Capital** — black and gold, sharp angled edges, high
   contrast, fast animation, skyline visuals. Aggressive sales energy.
3. **Industrial / Blue-Collar Capital** — steel gray with deep green and amber,
   built around the industries that use MCAs (trucking, construction, auto repair,
   restaurants, logistics, trades).

All three share the same copy and the same 4-step funding application.

## Things to know before launch

- **Placeholder branding.** The name "Stone Cold Loans", the square logo, the phone
  number `(800) 555-0100`, and the email `hello@stonecoldloans.com` are placeholders.
  Search-and-replace them across the files when the real brand is set.
- **The application form is front-end only.** All four steps validate and a success
  message appears, but no data is sent anywhere yet. `script.js` has a marked spot to
  connect it to a real email handler, form service, or CRM.
- **Theme 3 imagery is stand-in art.** The files in `theme3-industrial/assets/` are
  self-contained SVG industrial graphics — no external dependencies. To use real
  photography, replace each `.svg` with a photo of the same name (e.g. `hero.svg`,
  `trucking.svg`). `gen_assets.py` is the script that produced them, kept for reference.
- **Compliance.** Each footer states that Stone Cold Loans provides merchant cash
  advances, not loans. Have a lawyer review all disclosure language before going live.

## Decisions made along the way

A few open questions were answered with sensible defaults — all easy to change:

- Delivered as **three fully separate sites** so they can be compared directly.
- The loan application is a **4-step form** (business info → revenue & amount →
  contact → review & consent).
- Theme 3 uses **generated industrial art** rather than stock photos, since real
  photography can be dropped in later without touching the code.

Tell me which theme to move forward with and I'll refine that one and wire up the form.
