# AI Prompt Studio for Teachers — interactive prototype

A self-contained, offline **prompt builder** that turns a curated library of
advanced teacher prompts into fill-in-the-blank tools. The buyer opens the
`.html` file in any browser (no install, no internet), picks a prompt, fills
the fields, and clicks **Copy prompt** — ready to paste into ChatGPT, Claude
or Gemini.

## Why this format
A PDF's built-in JavaScript only runs in Adobe Acrobat, so an "assemble the
prompt" dialog inside a PDF fails for most buyers. A single self-contained
HTML file runs in every browser, on every device, offline — the robust way to
deliver the "fill fields → copy" experience.

## File
| File | What it is |
|---|---|
| `prompt_studio.html` | The whole tool — inline CSS/JS, no external assets. Double-click to run. |

## Prompt design (why results are precise)
Every template: assigns an **expert role**, supplies **context** via fields,
demands a **structured output**, and invokes a pedagogical framework (Bloom's,
UDL/WIDA, DOK, backward design, success criteria, misconception-targeted
distractors). Tokens are `{{key}}`; blanks left unfilled stay visible as
`[Label]` in the output so nothing is forgotten.

15 prompts across: Planning, Differentiation, Assessment, Feedback,
Communication, Engagement, Reteaching, Adaptation.

## Status
Prototype for the planned **"AI Prompts for Teachers"** Etsy listing. Intended
packaging: this HTML tool + a printable PDF prompt catalog (the visual the
listing photos show) + optional Google Sheet version. Not yet published.

Content is original, curated teaching prompts (not bulk AI-generated media).
Personal / single-classroom use.
