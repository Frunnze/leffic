---
name: dws
description: Deep web search. Runs at least 20 searches across diverse angles, filters to authoritative sources, cross-checks claims across independent sources, and returns a thorough, verified synthesis with citations.
---

# /dws — Deep Web Search

Perform a thorough, verification-oriented web investigation for the user's request. Use this when the user wants a deeply researched answer with cross-checked facts and broad coverage, not a quick lookup.

For quick lookups, use `/lws` instead.

## Arguments

The user's query follows the command, e.g. `/dws how does Raft consensus handle network partitions`.

If no query is provided, ask the user what to research before continuing.

## Procedure

### 1. Decompose the request

Break the user's request into sub-questions. A good deep search covers:
- **Core definition / mechanism** — what the thing is, how it works
- **Authoritative specification** — official docs, standards, papers
- **Variants and alternatives** — competing approaches, trade-offs
- **Real-world usage** — known implementations, case studies
- **Common failure modes / criticisms** — limitations, pitfalls
- **Recency** — current state vs. historical, latest version

### 2. Plan queries

Derive **at least 20 distinct search queries** spanning the sub-questions above. Vary by:
- Rephrasing (different terminology for the same concept)
- Narrowing (specific subtopics, versions, edge cases, error conditions)
- Broadening (background, history, motivation)
- Qualifiers (`site:` filters for official docs, `filetype:pdf` for papers, year filters, `RFC`, `spec`, `official`)
- Adversarial angles (`<topic> criticism`, `<topic> limitations`, `<topic> vs <alternative>`)

### 3. Run the searches

Use the `WebSearch` tool. Run independent searches in parallel within a single message when possible to save time. Track which queries you've run so you don't duplicate.

### 4. Filter to valid sources only

A **valid source** is one of:
- Official project / vendor documentation (the maintainer's own docs)
- Standards bodies (IETF/RFCs, W3C, ISO, NIST, IEEE)
- Peer-reviewed publications (journals, conference proceedings, arXiv when the paper is cited/established)
- Primary-source engineering writeups from the maintainers themselves
- Government / regulatory bodies for legal or compliance topics
- Reputable, editorially-curated outlets with named authors and dates
- High-signal community sources (accepted Stack Overflow answers with strong votes, GitHub issues with maintainer responses) — secondary signal only

**Reject:**
- SEO content farms and AI-generated rewrites
- Anonymous blog posts with no author or date
- Forum posts without consensus or maintainer involvement
- Tutorials that contradict official docs without explanation
- Sources older than the relevant version when version-sensitive

### 5. Fetch and read

For each candidate source that looks materially useful, use `WebFetch` to pull and read the page. Do not rely on search snippets alone for substantive claims — snippets are often misleading or out of context.

Aim for **at least 20 sources actually opened and read**, not just 20 search results returned.

### 6. Cross-check (proof-checking)

For every non-trivial claim in your final answer:
- **Require at least 2 independent valid sources to corroborate it.** Independent means not derivative of the same primary source.
- If only one source supports a claim, mark it as **single-source** in the answer.
- If sources **disagree**, present both positions, identify the more authoritative one, and explain the disagreement — do not silently pick a side.
- If a widely-repeated claim turns out to trace back to a single unreliable origin, flag it as **unverified** rather than asserting it.

### 7. Synthesize

Write a thorough but tight answer:
- Open with a **direct answer** to the user's request (no preamble).
- Follow with **sections** covering the sub-questions you decomposed.
- Cite every substantive claim inline with a short tag (e.g. `[1]`, `[7]`).
- Note disagreements, uncertainty, and recency explicitly.
- Distinguish **established fact** from **community consensus** from **single-source claim**.

## Output format

1. **Answer** — direct response to the user's request.
2. **Detail** — sections per sub-question with inline citations.
3. **Conflicts / caveats** — claims where sources disagree, are dated, or are single-source.
4. **Sources** — numbered list of every URL you actually opened, each with a one-line note on what it contributed and what type of source it is (official / standard / peer-reviewed / engineering blog / community).

## Constraints

- **Minimum 20 sources opened and read.** Always. If you cannot find 20 valid sources, say so explicitly and explain what you searched.
- Never cite a source you did not actually fetch and read.
- Cross-check every non-trivial claim against ≥2 independent valid sources. Flag single-source and unverified claims explicitly.
- Prefer primary sources over secondary; secondary over tertiary.
- This is **deep** search — thoroughness and verification matter more than brevity. Do not pad, but do not cut corners on coverage.
