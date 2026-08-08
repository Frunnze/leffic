---
name: lws
description: Light web search. Runs at least 5 web searches for the user's request, filters to valid/authoritative sources only, and returns a concise synthesis with citations.
---

# /lws — Light Web Search

Perform a focused web search for the user's request. Use this when the user wants quick, source-grounded information from the web rather than a deep investigation.

## Arguments

The user's query follows the command, e.g. `/lws best practices for Python logging`.

If no query is provided, ask the user what to search for before continuing.

## Procedure

1. **Plan queries.** Derive **at least 5 distinct search queries** from the user's request. Vary them by:
   - Rephrasing (different keywords for the same intent)
   - Narrowing (specific subtopics, versions, error messages)
   - Broadening (background/context queries)
   - Adding qualifiers (`site:docs.python.org`, `2025`, `official`, `RFC`, etc.)

2. **Run the searches.** Use the `WebSearch` tool for each query. Run independent searches in parallel within a single message when possible.

3. **Filter to valid sources only.** A valid source is one of:
   - Official project documentation (e.g. `docs.python.org`, `kubernetes.io`, MDN, RFC editor)
   - Reputable standards bodies (IETF, W3C, ISO, NIST)
   - Vendor docs from the maintainer of the technology in question
   - Well-known peer-reviewed or editorially-curated outlets (e.g. arXiv for papers, established engineering blogs from the maintainers themselves)
   - High-signal community sources where the answer is endorsed/accepted (e.g. accepted Stack Overflow answers with high votes), used as a secondary signal only

   Reject:
   - Content farms, SEO-spam aggregators, AI-generated rewrites
   - Unverified blog posts with no author or date
   - Forum posts without consensus or acceptance
   - Sources older than the technology's last major version when version-sensitive

4. **Read selectively.** If a search result snippet looks promising but the answer needs detail, use `WebFetch` to pull the page contents. Do not fetch every result — only the ones that materially add to the answer.

5. **Synthesize.** Write a concise answer that:
   - Directly addresses the user's request
   - Cites each claim with the source URL inline (e.g. `(docs.python.org)`)
   - Notes disagreement between sources if present
   - States explicitly if no valid source was found, rather than padding with weak material

## Output format

- Lead with the answer in 1–3 short paragraphs or a tight bulleted list.
- Follow with a **Sources** section: numbered list of the URLs you actually used, each with a one-line note on what it contributed.
- Do not list rejected or unused sources.

## Constraints

- Minimum 5 searches. Always.
- Never cite a source you did not actually open or whose snippet you did not actually read.
- Keep the final answer tight — this is *light* web search, not a research report.
