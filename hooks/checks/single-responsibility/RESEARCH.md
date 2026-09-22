# Research behind the entity rule

This check asks one question: how many external entities does a unit reach? Two
or more are two reasons to change, and the unit is split. This report records
why that rule replaced the previous cohesion coefficient, what the literature
supports, and what it does not.

## Summary

The previous implementation scored a weighted blend of implementation burden,
disconnected member components, external client populations, effect-slice
workflows and a PMD-inspired God Class conjunction. Measured against this
repository it did not work:

- 1200 of 1283 units scored exactly `0.0`; the maximum was `0.4025` against a
  gate of `0.5`. Nothing could ever block.
- The dominant term was disconnectedness, which had no support requirement.
  `shared/file_storage.py` — 17 lines, two functions — scored `0.4000` purely
  because its two functions share no state, while `json.ts` with eleven
  unconnected members scored `0.0000` because none of them touched an import.
- The God Class route was unreachable: `tight_cohesion` was `null` for every
  unit in the repository, because this codebase is function-oriented and the
  metric only measures `self.<field>` sharing.
- 0 of 969 callables reached the two strong effect domains the formula needed,
  and 0 had observable effect flow, so 65% of the callable score and the entire
  workflow subsystem were inert.

The entity rule keeps the one evidence family that was doing real work — resolved
library operations, including those reached through helpers — and discards the
rest.

## What the literature supports

**Responsibility is about actors, not structure.** Martin ties SRP to reasons for
change associated with different stakeholders.[^1] An external entity is a
direct, if blunt, reading of that: each outside world a unit talks to is owned
elsewhere and changes on its own schedule.

**Responsibility is observable through impact on the outer scope.** Ardalani and
colleagues define a method's responsibility as its effect on the outer scope, and
slice on output instructions — returns, and writes to a console, file, database
table, I/O port or global.[^6] The entity rule takes the same object of study,
counted per external medium instead of sliced per output variable.

**Structural cohesion is a weak proxy for the SRP smell.** Palomba and colleagues
built DCCA, a static detector for Divergent Change — the smell that literally is
"a class changed in different ways for different reasons" — using the Connectivity
metric, the fraction of method pairs sharing a field or calling each other, with
a calibrated threshold of 0.3. Over eight Java systems it achieved **F-measure
10% (7% recall, 20% precision)**, against **76% (79% recall, 73% precision)** for
the same smell detected from change history.[^9] This is the strongest available
evidence that the removed disconnected-component term could not carry a commit
gate, and it matches what this repository showed.

**Metric-based responsibility detectors produce mostly false positives.**
SmellBench took PyExamine's hard-severity architectural smells on scikit-learn
and had three annotators classify them (κ=0.67): **41 of 65 (63.1%) were false
positives**, 13 partially valid, 11 true positives.[^12][^13] Developers also
disagree with each other: a family of controlled experiments on God Class
detection found low inter-rater agreement even when subjects found the task easy,
and visualization did not improve it.[^14]

**Developers act on what they can see.** Palomba's perception study found the
smells developers reliably identify and rate severe are Complex Class, God Class,
Long Method and Spaghetti Code — the ones visible by reading the code.[^15] The
large-scale diffuseness study found smelly classes have 3x the median change
proneness (32 vs 12) and 3x the faults (9 vs 3) of clean ones.[^16] None of this
validates a cohesion coefficient; it argues for findings a reader can verify at
a glance. "This function talks to the network and the filesystem, here are the
calls" is such a finding.

**LCOM variants are the wrong tool and know it.** Sharma and Spinellis catalogue
five defects in LCOM1–5, including that LCOM2 reports perfect cohesion both for a
fully cohesive class and for one where cohesion cannot be measured at all, and
propose returning an explicit unmeasurable value instead.[^3] The previous
implementation inherited exactly that ambiguity through `null` metrics.

## What the rule deliberately does not use

**Implementation burden.** Cognitive Complexity is the only code-only metric with
a validated relationship to understandability: a meta-analysis over ~24,000
evaluations of 427 snippets found a weighted mean correlation of **0.54** with
comprehension time, against a best of **0.11** among the 121 metrics Scalabrino
and colleagues tested.[^17] It is a good metric — for understandability, which is
the file-length check's concern, not this one. A 200-line function that talks to
one database has one reason to change.

**Benchmark-derived thresholds.** Alves, Ypma and Visser derive thresholds from
the LOC-weighted cumulative distribution over 100 systems, taking the 70th, 80th
and 90th percentiles; for McCabe that yields 6, 8 and 14.[^18] This is the right
method for a continuous metric. The entity count is not continuous: the threshold
is 2 because two is more than one, and no benchmark is required to say so.

**Client populations.** Alzahrani and Alqithami use clients external to a class
to support Extract Class.[^4] The previous implementation required two disjoint
client source files per group. It never fired here, it made results depend on
which files were in the scan, and a source file is only a proxy for an actor.

**Change history.** HIST detects Divergent Change from co-change with association
rules (support 0.008, confidence 0.70) and outperforms every static equivalent on
that smell.[^9] It remains out of scope: it would make a pre-commit verdict depend
on how much history the developer has fetched, mass formatting commits corrupt
the signal, and renames break callable identity.

**Semantics.** C3 measures conceptual cohesion with LSI over identifiers and
comments.[^8] ConcernBERT learns responsibilities from class membership over two
million Java files and reports strong results recovering merged class
memberships.[^19] Both are promising as review aids. Neither belongs in a hook
where renaming a variable must not change the verdict, and the regression suite
enforces that comments and renames do not.

**Language models.** GPT-4.0 reaches precision 0.79 and recall 0.41 (F1 0.54) on
an annotated multi-language smell dataset; DeepSeek-V3 reaches 0.42/0.31.[^20]
On architectural smell repair, the best agent resolved 31 of 65 findings while
introducing 140 new smells.[^12] Recall that low, cost, reproducibility and
source-code privacy all rule out inference in a commit gate.

## Known limits of the rule

The count is blunt by construction, and that is the trade.

- **Two policies over one entity are invisible.** Two unrelated tables behind the
  same ORM are one entity. Pure computational SRP violations have no entity at
  all.
- **Cohesive work can cross two media.** Writing a temporary file in order to run
  a converter is one job by any reasonable reading and two entities by this rule.
  `shared/pdf_conversion.py` is exactly that case. The whitelist exists for it,
  and a reviewed exception with a reason is the intended outcome, not a defect.
- **Coverage is the accuracy ceiling.** An entity exists only if its library is in
  the catalogue. Before the catalogue was extended, 731 of 969 callables here
  appeared to touch no outside world at all. Absence of a row is absence of
  evidence.
- **Aggregation punishes breadth.** A module unions its members' entities, so a
  well-factored module of single-entity functions still blocks. That is the rule
  working as specified — the module has two reasons to change — but it is the
  finding most likely to be argued with.
- **Nothing here is calibrated.** No precision or recall has been measured against
  a human-labelled SRP dataset for this repository, and the cited work does not
  validate this rule. Passing is one architecture check, not a certification.

## Sources

[^1]: Robert C. Martin. [The Single Responsibility Principle](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html). May 8, 2014.

[^3]: Tushar Sharma and Diomidis Spinellis. [Do We Need Improved Code Quality Metrics?](https://arxiv.org/html/2012.12324) arXiv:2012.12324. LCOM defects and YALCOM; explicit unmeasurable values.

[^4]: Musaad Alzahrani and Saad Alqithami. [An External Client-Based Approach for the Extract Class Refactoring](https://doi.org/10.3390/app10176038). Applied Sciences 10(17), 6038, 2020.

[^6]: Alireza Ardalani, Saeed Parsa, Morteza Zakeri-Nasrabadi and Alexander Chatzigeorgiou. [Supporting single responsibility through automated extract method refactoring](https://arxiv.org/pdf/2305.03428). Empirical Software Engineering, 2023. Responsibility as impact on the outer scope; output-instruction slicing.

[^8]: Andrian Marcus and Denys Poshyvanyk. [The Conceptual Cohesion of Classes](https://www.cs.wm.edu/~denys/pubs/marcusa-Cohesion.pdf). ICSM 2005. C3 and LCSM over identifiers and comments.

[^9]: Fabio Palomba et al. [Detecting Bad Smells in Source Code Using Change History Information](https://fpalomba.github.io/pdf/Conferencs/C2.pdf). ASE 2013. HIST; DCCA and the Connectivity metric; calibration table and per-smell results.

[^12]: [SmellBench: Evaluating LLM Agents on Architectural Code Smell Repair](https://arxiv.org/html/2605.07001). 65 hard-severity smells on scikit-learn, expert-classified at κ=0.67; 63.1% false positives; agent resolution and regression counts.

[^13]: [PyExamine: A Comprehensive, Un-Opinionated Smell Detection Tool for Python](https://arxiv.org/pdf/2501.18327). arXiv:2501.18327. The detector SmellBench sampled; reported 80.6% recall on architectural smells.

[^14]: [The problem of conceptualization in god class detection: agreement, strategies and decision drivers](https://link.springer.com/article/10.1186/s40411-014-0011-9). JSERD, 2014. Low inter-rater agreement; visualization does not fix it.

[^15]: Fabio Palomba et al. [Do they Really Smell Bad? A Study on Developers' Perception of Bad Code Smells](https://fpalomba.github.io/pdf/Conferencs/C3.pdf). ICSME 2014. Which smells developers actually perceive as problems.

[^16]: Fabio Palomba et al. [On the diffuseness and the impact on maintainability of code smells](https://link.springer.com/article/10.1007/s10664-017-9535-z). EMSE, 2018. 395 releases of 30 projects; change- and fault-proneness of smelly classes.

[^17]: Marvin Muñoz Barón, Marvin Wyrich and Stefan Wagner. [An Empirical Validation of Cognitive Complexity as a Measure of Source Code Understandability](https://arxiv.org/pdf/2007.12520). ESEM 2020. Also [the SonarSource specification](https://www.sonarsource.com/docs/CognitiveComplexity.pdf).

[^18]: Tiago L. Alves, Christiaan Ypma and Joost Visser. [Deriving Metric Thresholds from Benchmark Data](https://webarchive.di.uminho.pt/wiki.di.uminho.pt/twiki/pub/Personal/Joost/PublicationList/AlvesYpmaVisserICSM2010.pdf). ICSM 2010. LOC-weighted percentile thresholds.

[^19]: [ConcernBERT: Learning Responsibilities Using Class Membership](https://arxiv.org/abs/2606.21647). Entity-level embeddings trained with triplet loss on class membership.

[^20]: Ahmed Sadik and Siddhata Govind. [Benchmarking LLM for Code Smells Detection: OpenAI GPT-4.0 vs DeepSeek-V3](https://arxiv.org/abs/2504.16027). EASE 2025. Precision/recall/F1 across Java, Python, JavaScript and C++.

Also consulted: [PMD's design rules](https://docs.pmd-code.org/latest/pmd_rules_java_design.html) for the GodClass conjunction the previous implementation used (WMC/ATFD/TCC) and its other default thresholds; [Designite](https://www.designite-tools.com/docs/features_cs.html) and [Arcan](https://essere.disco.unimib.it/wiki/arcan/) for architectural smell definitions, including God Component and Feature Concentration; [Bieman and Kang's TCC/LCC](https://www.cs.colostate.edu/~bieman/Pubs/bieman-kang-ssr95.pdf) and [a reference implementation of the LCOM family](https://www.aivosto.com/project/help/pm-oo-cohesion.html); and the Yourdon and Constantine [cohesion taxonomy](https://en.wikipedia.org/wiki/Cohesion_(computer_science)), whose coincidental cohesion is what the removed disconnected-component term was reaching for.
