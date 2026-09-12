# Research-informed SRP detection

This report records the research and historical 0.8 blocking policy. The current
gate is 0.5; scoring still uses the original 0.8 high-confidence boundary.
Review of `link_extractor.py` identified separate YouTube-transcript and webpage
extraction responsibilities, which are now split into separate modules. The
check instructs agents to inspect findings, fix real violations, and document
exact false positives with reasons in `whitelist.txt`. See [the current
evaluation](EVALUATION.md) and [usage documentation](README.md) for current
results and policy; historical findings below describe their recorded revisions.

## Summary

The most useful improvement to this check is stronger corroboration, not more
size metrics. A class can contain disconnected methods without having separate
business responsibilities. A function can perform network and filesystem work
as steps of one cohesive operation. A blocking detector should recognize both
possibilities before treating either pattern as strong evidence.

The implementation now combines structural groups with observed client
populations, treats connected effect computations as counterevidence, and adds
a conjunctive God Class risk rule. Disconnected groups alone no longer reach
the 0.8 blocking threshold. The detector remains local, deterministic for a
given source snapshot and analysis scope, and explainable through JSON facts.
It does not require model downloads, external inference, or repository history.

The score is a normalized risk coefficient, not a calibrated probability.
Neither 0 nor 1 establishes the truth of a business-level SRP claim. The
literature supports several useful evidence families but does not validate the
weights or the 0.8 cutoff used here. The improvement demonstrated locally is
specific: a previously overconfident adapter finding is downgraded, while
representative independent-work fixtures still block.

## Responsibility and observable evidence

Robert C. Martin's explanation ties SRP to reasons for change associated with
different stakeholders or actors. It is not a rule that every class must contain
one method, or that a function must call only one kind of library.[^1]

That distinction changes the interpretation of static measurements. Length,
branches, parameters and dependencies measure aspects of implementation burden.
They can identify difficult code without revealing whether accounting policy,
storage policy and presentation policy are being maintained together. Similarly,
two algorithms may implement alternatives within one feature rather than two
independently owned policies.

For this hook, the practical objective is to prioritize evidence sufficiently
strong to justify interrupting a commit. That is different from generating
every plausible Extract Class or Extract Method suggestion. Review candidates
can remain below the threshold without being declared clean. Analysis errors
are separate again: unreadable or invalid source must fail the analysis instead
of becoming a low coefficient.

The evidence reviewed includes foundational cohesion work and research
available through September 11, 2026. Most applicable studies concern Java
refactoring or code smells. Their applicability to Python modules, TypeScript
components and this repository's business responsibilities is therefore limited.
The accepted ideas below are adaptations, not reproductions of published tools.

## Evidence families and decisions

| Evidence family | Useful observation | Implementation decision |
|---|---|---|
| Runtime size and complexity | Substantial work makes a partition more consequential | Supporting burden only; never sufficient by itself |
| Field and call-graph cohesion | Methods may share state directly or through helpers | Retained with transitive relationships and explicit missing values |
| External client usage | Different consumers can corroborate a method partition | Added, requiring multiple disjoint observed source-file clients |
| Effect-slice relationships | Different outputs may share one computation | Added as a conservative independence guard and counterevidence |
| Conjunctive God Class metrics | Complexity, foreign data and poor cohesion together are stronger than one metric | Added as a distinct class-only risk route |
| Semantic similarity | Related vocabulary can inform candidate decompositions | Deferred from the blocking score |
| Change-history patterns | Different member groups may evolve separately | Deferred pending history-quality and identity handling |
| Learned classifiers | Semantic representations may detect patterns absent from explicit rules | Deferred pending representative labels and independent validation |

### Structural cohesion

Bieman and Kang's TCC/LCC work distinguishes direct and indirect relationships
among methods based on instance-variable usage. Sharma and Spinellis discuss
limitations of established cohesion metrics and propose YALCOM, including
method interactions and clearer treatment of cases that cannot be measured.
These sources support looking beyond literal field-name intersections and
distinguishing unavailable evidence from measured cohesion.[^2][^3]

The implementation's graph includes fields, imported dependencies, globals and
internal calls. Short forwarding helpers remain visible. Constructors are
excluded from behavioral cohesion because initializing every field should not
automatically join otherwise separate method groups. Field usage is propagated
through internal call links before the pairwise diagnostics are calculated.

These metrics remain deliberately labelled as variants. Private helpers are
included, inherited method bodies are not resolved across files, and imports
are resource proxies rather than field accesses. TCC-like cohesion, LCC-like
cohesion and disconnected-component count are not counted as three independent
votes: they largely describe the same structural evidence.

### External clients

Alzahrani and Alqithami propose using clients external to a class to support
Extract Class refactoring. Their model compares clients of method pairs,
including a Jaccard-style similarity, and their empirical evaluation covers two
systems. Lee and colleagues likewise investigate responsibility decomposition
using internal and external method relationships.[^4][^5]

The local adaptation asks a narrower question: do the supported groups have
different observed consumers in the current source tree? A client is a source
file, not each calling method. Two methods in one controller therefore do not
become two presumed actors. To corroborate a partition for blocking, every group
must have at least two observed client files and no client may be shared between
groups. The two-client minimum is a conservative local choice, not a published
statistical confidence threshold.

Explicit imports and simple aliases identify targets. External client sets
propagate through internal helpers and resolvable cross-file wrappers. Top-level
calls and callable references also contribute. Resolution is constrained to the
same source tree so similarly named modules in different services do not merge.
Ambiguous resolution is declined rather than arbitrarily choosing a target.

Shared clients are counterevidence, not proof of good design. A giant controller
may legitimately consume two poorly combined responsibilities. Conversely,
separate clients may consume different alternatives of one coherent service.
Client segregation is therefore a corroborating proxy for change ownership, not
an observation of the actual business actors. Missing clients remain unknown;
scanning only one file generally removes this evidence.

### Effect slices and cohesive workflows

Ardalani and colleagues' SBSRE work proposes output-based slicing for Extract
Method refactoring in support of single responsibility. It considers more than
return statements and uses control/program-dependence analysis. Importantly,
multiple outputs with heavily overlapping computation can be cohesive; counting
outputs alone is insufficient.[^6]

The new hook uses a much smaller approximation. Each top-level runtime statement
records reads, writes and recognized effect calls. Definitions carry the earlier
statements on which their values depend. For each effect domain, the checker
collects these contributing statement indices. A domain needs at least two
distinct operations and four contributing statements before participating in
the independence decision.

Two domains join one workflow group if one domain's effect feeds the other's
computation, or their slices overlap by at least half the smaller slice. Thus
fetching a response and writing its contents to disk supplies evidence of one
pipeline, even when the function is long. Substantial, separate computations
feeding different effect domains can still supply independent groups. Adding
unused assignments does not by itself make trivial effects substantial.

This is not a full backward slicer, alias analysis, control-flow graph, or SBSRE
implementation. Compound statements are summarized as blocks; a receiver call
is conservatively allowed to mutate that receiver. Those choices can connect
work that is actually independent, lowering recall. They also make it less
likely that a connected workflow is penalized merely because it crosses I/O
boundaries. The overlap threshold and support minimum are local policy choices.

### God Class conjunction

PMD's official GodClass rule combines three conditions: weighted method count
at least 47, access to foreign data greater than 5, and tight class cohesion
below one third. Its implementation requires all three measurements, rather
than treating any single condition as sufficient.[^7]

The hook adds an analogous class-only conjunction. Weighted methods are the sum
of the existing runtime complexity approximations. Foreign data is the number
of distinct observed non-method attribute references outside the class's own
direct state, including references through typed parameters. Tight cohesion is
the existing runtime-member field-cohesion variant.

These are proxies and can disagree with Java type-resolved metrics. Dynamic
objects, aliases and ownership of nested objects are not fully known. The rule
is useful as a separate high-risk route because a large policy-heavy class can
have few clients or no recognized direct I/O. It does not turn a God Class
finding into a proven SRP violation. Removing any one of the three conditions
must remove this route to blocking; regression tests enforce that behavior.

## Approaches excluded from the blocking coefficient

### Vocabulary and semantic clustering

Bavota and colleagues investigate Extract Class opportunities using structural
and semantic cohesion. Their approach demonstrates the relevance of combining
relationships beyond simple shared fields, in the context of suggesting and
evaluating class decompositions.[^8]

An identifier/topic heuristic would be cheap to add, but its meaning would be
weak here. Consistent vocabulary can describe several policies over the same
entity; different vocabulary can describe two formats in one conversion
feature. Comments and renaming would also become ways to change the coefficient
without changing behavior. The current regression suite instead requires
comment padding and relevant variable renaming to preserve the result.

A future semantic signal should be evaluated as a separate review aid first.
Its justification should identify independently changeable policies rather
than merely presenting a low text-similarity value. Any improvement must survive
renamed versions of the examples and project-separated evaluation. No name list,
topic model or language-model verdict currently affects the hook.

### Git history and divergent change

Palomba and colleagues' HIST work uses version history to detect code smells,
including divergent-change patterns. Its method-level co-change reasoning is
more relevant to independent reasons for change than raw file length or a
single file's total edit count.[^9]

That makes history promising but not ready to add as a simple numerical bonus.
A file edited often may contain one frequently changing policy. A mass formatting
commit can make unrelated methods appear to evolve together. Renames and moved
methods complicate identity; a shallow clone may not contain enough evidence
for a meaningful comparison. A stable pre-commit result should not unexpectedly
depend on which developer has fetched more history.

A viable later design would keep history analysis optional and report evidence
coverage explicitly. It would track callable identity across revisions, exclude
mechanical edits, require sufficient meaningful changes, and distinguish
co-change inside candidate groups from co-change across groups. Until those
conditions and validation are in place, no Git churn metric contributes to the
blocking score. No history mining or history-dependent cache was added.

### Machine learning and recent SRP-specific evidence

A 2026 Information and Software Technology study evaluates SOLID compliance on
1,103 Java/Python code units using transformer representations and classifiers.
Its reported SRP/LSP F1 scores are approximately 70–75%, lower than the results
for structurally explicit ISP/DIP. Its evaluation uses stratified five-fold
cross-validation; it is not a validation on this repository or TypeScript.[^10]

That result argues against presenting a model's output as certainty. It also
does not establish that the present heuristic is better: the approaches have
not been compared on the same labelled data. Model selection, runtime cost,
source-code privacy, reproducibility and probability calibration would all need
separate treatment before introducing inference into a Git hook.

The immediate priority is an independently labelled local evaluation set. A
model could later help reviewers identify candidate policies or supply a
non-blocking semantic opinion. Any claimed benefit should be measured against
the transparent baseline, including false-positive rates on cohesive adapters
and orchestration. No external dataset benchmark or learned calibration was
performed for this implementation.

## Coefficient policy and interpretation

The exact formula and metric ramps are documented in [README.md](README.md).
The implementation retains the requested inclusive threshold: a normalized
coefficient of 0.8 blocks. Coefficients are rounded to twelve decimal places
before comparison, and the reported file/repository value is the maximum unit
value. Additional unrelated clean files cannot dilute a high-risk unit through
averaging.

For callables, implementation burden contributes 35% and strong known-effect
evidence contributes up to 65%. Reaching the blocking range additionally
requires two substantial structural signals and multiple independent effect
groups. When that evidence is unavailable, or all substantial effects form one
workflow, the callable is capped below the threshold.

The follow-up implementation also summarizes I/O through uniquely resolved
actual helper calls in the analyzed source. Summaries converge with a worklist,
including recursive call graphs, and retain original library operation identity.
They enter the caller's statement slices at the call site without importing the
callee's structural burden. Reports distinguish direct and delegated evidence.
This extension is a local engineering rule tested with positive and negative
regressions; the cited research does not validate its accuracy.

For owners, structural separation and supported effect profiles generate review
scores. Neither alone reaches 0.8. Segregated clients can corroborate a supported
partition; alternatively, the three-condition God Class route can identify a
high-risk class. Related measurements use maximum-based alternatives rather
than indiscriminate addition. Shared callers lower the review score and prevent
the corresponding partition from qualifying through the client route.

The formula is a policy encoding, not a measured mapping from code to the
probability of a violation. A score near 0.8 does not mean an 80% chance that
reviewers will agree. A score of zero means that the modeled evidence is absent,
not that responsibilities were verified with domain owners. Renaming a function
or moving it to another file is not intrinsically a design improvement, even if
some structural quantities change.

## Repository finding and validation

The earlier implementation assigned approximately 0.9093 to
`content-management-service/src/features/study_units_generation/link_extractor.py`.
The principal evidence was two substantial dependency-connected groups inside
one module: transcript extraction and HTML content extraction. Those algorithms
are already separated into functions.

The relevant caller, `text_sources.py`, uses both groups as alternatives within
link-to-text extraction. `extraction_router.py` also appears as a shared client
through propagated usage. That is concrete contextual counterevidence to the
claim that the partition should automatically block a commit. It does not settle
whether separate adapter modules would be a worthwhile organizational choice.

Under the revised generic rules, the module scores `0.509261363636`. It remains
the highest-scoring current unit but does not block. There is no filename
allowlist or special-case coefficient. A regression test copies the module and
its direct caller into a temporary source tree; it repeats the assessment under
a different module filename to verify that the behavior is general.

The current working-tree scan covers 200 files and 1,283 scored callable,
class and module units:

| Source tree | Files analyzed |
|---|---:|
| `user-service/src` | 18 |
| `content-management-service/src` | 62 |
| `ui-service/src` | 119 |
| `api-gateway/src` | 1 |

No current unit reaches 0.8. This is a count of blocking findings under the
implemented policy, not a count of all actual SRP violations. The hook analyzes
working-tree sources, including untracked and unstaged files, rather than only
the Git index. Tests and dependency/build/cache directories are outside the
declared source scan.

The focused suite contains 100 passing tests at this revision. It checks both
language adapters, source discovery and reporting, and the risk rules:

| Scenario | Required behavior |
|---|---|
| Disconnected state groups without client evidence | Remain below 0.8; report missing context |
| Supported groups with two disjoint clients each | Reach the inclusive 0.8 boundary |
| Shared client, including top-level calls or wrappers | Refute segregation for that partition |
| Large, independent network/filesystem computations | Block |
| Network result written to disk | Recognize workflow counterevidence; do not block the callable |
| Shared computation or unrelated padding | Do not invent independent substantial jobs |
| Complexity, foreign-data access and low cohesion together | Trigger the class-only risk route |
| Any one God Class condition removed | Remove that blocking route |
| Invalid syntax or missing tools | Fail visibly; never report a successful partial scan |

Other tests check bounds, deterministic maximum aggregation, aliases and
shadowing, comments, nested scopes, constructors, static fields, relative
imports, ambiguous resolution, service isolation and paths containing spaces.
These fixtures test intended behavior and regressions. They do not provide a
statistical precision, recall, F1 score or calibrated reliability estimate.

The broader hook regression run passed 317 tests using
`.venv/bin/pytest -q hooks/tests`.
That excludes the unrelated lockfile module, which also tests Docker builds and
Git branch/task state; it is not a claim that every repository test or every
pre-commit check was executed. The file-length check,
SRP hook, Python lint/format checks, JavaScript syntax checks and shell syntax
checks also passed.

## Remaining blind spots

Responsibility is not always observable through I/O, fields or consumers. Two
unrelated pure algorithms in one long function may evade the blocking rules.
A polymorphic dispatcher may hide effects behind custom interfaces. Business
actors may cut across files, and a single source file may serve several actors.
No static proxy completely resolves those situations.

Import and alias resolution is intentionally bounded. The current implementation
now resolves explicit Python re-exports, TypeScript compiler path aliases,
named/default/star re-exports and static CommonJS import forms. Dynamic imports,
reflection, computed `require`, dynamic `module.exports`, Python wildcard exports
and complex aliases may still be missed. An unresolved common caller
can make observed client sets appear more separate than the real sets. Requiring
multiple clients reduces weak evidence but cannot remove that coverage risk.

The effect library catalogue is explicit. Unknown packages are not guessed from
method names. Top-level statements supply caller evidence but are not scored as
standalone callables. Module scores aggregate member relationships, not every
possible responsibility at package or service scope. Inherited methods and
cross-function data flow are not fully analyzed. Resolved helper bodies now
contribute effect summaries, but opaque callbacks, polymorphic calls, hidden
global state and mutations across function boundaries remain limitations.

These omissions are reasons to retain human review, not to silently increase
scores. A suitable explanation of a high finding should identify the implicated
methods, their separate work, and the supporting evidence. A low finding should
still be investigated when domain knowledge establishes distinct change owners.
Passing this hook is one architecture check, not a certification.

## Evaluation and calibration plan

The survey by Zakeri-Nasrabadi and colleagues reviews 45 code-smell datasets and
highlights problems including imbalance, limited severity labels and Java-heavy
coverage. Many datasets target God Class, Long Method or Feature Envy rather
than SRP itself.[^11] A smell label must therefore not be silently relabelled as
a definite SRP verdict.

The next meaningful evaluation should use repository-relevant cases labelled
without consulting this coefficient. Reviewers should identify the unit, the
responsibilities, the actors or policies that could change independently, and
the supporting callers or change examples. Include an explicit uncertain label
for cases like alternative adapters whose preferred packaging is debatable.
Keep uncertainty rather than forcing every example into a clean/violation pair.

Sampling should include cohesive controllers, converters, parsers, repositories,
React components, pure calculations and genuinely mixed-policy implementations.
Include unflagged units and difficult negatives, not only existing warnings.
Preserve realistic source context so client-based evidence can be assessed;
isolated snippets are insufficient to evaluate that route. Python and
TypeScript results should be reported separately as well as together.

Hold out whole projects or feature families and keep related revisions and
renamed copies in the same split. Tune weights only on the development split.
Measure precision among blocking findings, recall over agreed violations,
false-positive rate over agreed cohesive units, and the proportion of examples
with insufficient or disputed evidence. For a commit gate, the cost of a false
block deserves explicit attention, but conservative abstention also has a cost
in missed violations.

Use an ablation comparison: size/cohesion baseline, baseline plus clients,
baseline plus flow, and the combined policy. That reveals whether a signal
improves independently labelled outcomes instead of merely reproducing the
fixtures written for it. Review disagreements before adjusting thresholds.
Repeatedly tuning to one disputed module would overfit the repository finding.

Only after independent evaluation should the coefficient be considered for
probability calibration. Even then, the reported meaning must be tied to the
population and labels used for calibration. A practical intermediate step is
to preserve the current explainable risk score and collect reviewed outcomes,
without claiming its decimal precision reflects statistical certainty.

## Sources

[^1]: Robert C. Martin. [The Single Responsibility Principle](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html). May 8, 2014. Primary explanation of responsibility in terms of reasons for change and actors.

[^2]: James M. Bieman and Byung-Kyoo Kang. [Cohesion and Reuse in an Object-Oriented System](https://www.cs.colostate.edu/~bieman/Pubs/bieman-kang-ssr95.pdf). ACM Symposium on Software Reusability, 1995. Author-hosted paper; TCC/LCC and direct/indirect cohesion.

[^3]: Tushar Sharma and Diomidis Spinellis. [Do We Need Improved Code Quality Metrics?](https://arxiv.org/html/2012.12324). arXiv:2012.12324, first submitted 2020. Metric limitations, method relationships and YALCOM. The hook is not a complete implementation of the paper's metric.

[^4]: Musaad Alzahrani and Saad Alqithami. [An External Client-Based Approach for the Extract Class Refactoring: A Theoretical Model and an Empirical Approach](https://doi.org/10.3390/app10176038). Applied Sciences 10(17), 6038, August 31, 2020. [Accessible article PDF](https://pdfs.semanticscholar.org/41c8/21d50e233e983664f94a0fe9117fc02e1a89.pdf). External-client similarity and its evaluation; publisher access was rate-limited.

[^5]: Lee et al. [Decomposing class responsibilities using distance-based method similarity](https://journal.hep.com.cn/fcs/EN/10.1007/s11704-015-5001-5). Frontiers of Computer Science, 2016. Structural and external relationships for decomposition.

[^6]: Alireza Ardalani, Saeed Parsa, Morteza Zakeri-Nasrabadi and Alexander Chatzigeorgiou. [Supporting single responsibility through automated extract method refactoring](https://arxiv.org/abs/2305.03428). 2023. [Full paper, revised November 26, 2023](https://arxiv.org/pdf/2305.03428v2). Output-oriented slicing, program dependence and overlapping computations; the local flow guard is a limited adaptation.

[^7]: PMD project. [GodClass rule documentation](https://docs.pmd-code.org/latest/pmd_rules_java_design.html#godclass) and [official GodClassRule implementation](https://raw.githubusercontent.com/pmd/pmd/main/pmd-java/src/main/java/net/sourceforge/pmd/lang/java/rule/design/GodClassRule.java). Inspected September 11, 2026. Exact conjunction: WMC >= 47, ATFD > 5, TCC < 1/3; thresholds attributed in source to Lanza/Marinescu's metrics work.

[^8]: Gabriele Bavota et al. [Identifying Extract Class refactoring opportunities using structural and semantic cohesion measures](https://www.sciencedirect.com/science/article/pii/S0164121210003195). Journal of Systems and Software, 2011. Structural/semantic decomposition; publisher-indexed text available, direct page access restricted.

[^9]: Fabio Palomba et al. [Mining Version Histories for Detecting Code Smells](https://mdipenta.github.io/files/TSE2372760.pdf). IEEE Transactions on Software Engineering, 2015. Author-hosted paper; HIST and change-history evidence.

[^10]: Balim et al. [Automatic multi-language analysis of SOLID compliance via machine learning algorithms](https://www.sciencedirect.com/science/article/pii/S0950584926000029). Information and Software Technology 192, 108013, April 2026. DOI: 10.1016/j.infsof.2026.108013. Publisher-indexed abstract and method/result summaries; no independent reproduction or repository-specific validation.

[^11]: Morteza Zakeri-Nasrabadi, Saeed Parsa, Ehsan Esmaili and Fabio Palomba. [A systematic literature review on the code smells datasets and validation mechanisms](https://arxiv.org/abs/2306.01377). ACM Computing Surveys, 2023; DOI: 10.1145/3596908. Dataset coverage, imbalance, severity and language limitations.
