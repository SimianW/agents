---
name: second-opinion
description: "Second opinion on an engineering approach: XY check, real-world evidence, scored candidates, one recommendation."
disable-model-invocation: true
---

# Second opinion

Review an engineering approach the way a consulting physician gives a second opinion: question the diagnosis first, then evaluate the treatment. Hold the user's approach and your own to the same standard of evidence. Deliver an assessment: what the real problem is, under which conditions each candidate holds, how each scores, and which one you recommend.

## Confidence labels

Tag every claim with one label:

- **Verified**: directly shown by local code or by a source you read in full.
- **Conditional**: holds under a stated trigger or assumption.
- **Trade-off**: not a defect; a cost paid for some other benefit.
- **Unverified**: based on prior knowledge; no source found or readable.

A source proves only what it covers. Official docs prove public interfaces and guarantees; open-source code proves that version's implementation; production use needs matching public evidence; undisclosed internals stay unknown. Separate formal standards (cite the clause), official recommendations, common practice across independent implementations, and one team's choice. A handful of cases supports "these projects do this", never "the industry does this". A large company's scale and organisational constraints are applicability conditions, not proof of superiority.

## 1. Frame the problem

Reconstruct from the conversation the outcome the user wants (X) and the current approach (Y). When Y is a direct path to X, confirm and move on. When Y sidesteps the usual solutions to X, or patches a hole left by another problem, it is an XY problem: name the suspected X, switch to evaluating solutions to X, and keep Y as one candidate. When X is uncertain, ask one focused question and continue the research that does not depend on the answer.

For an existing project, read the relevant code, accepted design decisions, and requirements to confirm actual behaviour. Keep the product goals and technical constraints the user has already chosen. List only constraints that would change the verdict: scale, consistency requirements, deployment environment, team capacity, migration cost.

Done when you can state X, Y, and the verdict-changing constraints in one sentence.

## 2. List candidates

Candidates are the current approach Y, the minimal fix to Y, and competitive alternative solutions to X. With no approach formed yet, start from 2–3 candidates. Keep only candidates that could change the decision.

Done when the list is fixed and each candidate's mechanism fits in one sentence.

## 3. Check against reality

Search around X and each candidate's key risks; hunt for counterexamples, post-mortems, and failure reports. Read primary sources first: company engineering blogs, project source and tests, maintainer design docs and discussions, official protocols and docs, incident reviews. Tutorials, roundups, and search snippets only locate sources; read the original or the code before it backs a claim.

Find 2–4 cases from different teams or projects around the key trade-off. Reposts of one article count once; when material is scarce, report what you actually found.

Done when the key risks and main candidates rest on checkable evidence, or further searching can no longer close the gap. Report gaps as they are and label the affected claims **Unverified**.

## 4. Find the faults

Walk each candidate's decision points. Rank by consequence: correctness, reliability, access boundaries, and goal attainment first; then performance, maintenance, and cost at the current scale.

Write each issue as a causal chain the user can retell:

- **Where**: the specific decision or code location.
- **Trigger**: a concrete request sequence, failure process, or data example.
- **Consequence**: the effect on X.
- **Evidence**: local facts and external sources, labelled.
- **Fix**: the minimal workable change, its cost, and how to verify it.

For example: two requests both read a remaining quantity of 1 outside a transaction, each decrements, and the quantity goes negative; then say whether the applicable database mechanism eliminates that ordering.

Done when every relevant decision point is either listed as an issue or explicitly cleared. With no substantive fault, say so, and state the conditions under which the approach holds and what remains unverified.

## 5. Score and recommend

Compare all candidates under one set of constraints. Pick the dimensions that discriminate for this problem; score each candidate 1–10 on each, with evidence and label. Then give a 1–10 overall score and name the dimensions that drive it.

Give one recommendation: what to adopt now, which changes come first, and which changed conditions should trigger a re-evaluation. When uncertainty could flip the ranking, propose a small experiment, failure test, or measurement that separates the candidates.

Done when every candidate has scores with evidence, and there is one recommendation with its re-evaluation conditions.

## Output

Lead with the verdict (what X is, which candidate wins), then:

- XY finding: expand only when it is an XY problem.
- Case table with columns: project | problem solved | mechanism | constraints, benefits, published costs | source (date, version, or code location) | similarities, differences, and what to borrow.
- Issue list in the step-4 structure.
- Score table: candidates × dimensions, plus overall.
- Recommendation.

Keep evidence next to the claim it supports. Explain the technical mechanism behind the verdict so the user can retell why the recommendation holds.

Stop after delivering the assessment; the user decides whether to implement.
