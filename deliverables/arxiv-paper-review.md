# ArXiv paper review

Paper: **Mechanism-Diverse Tail Robustness for Multi-Agent LLM Systems: A Falsifiable Evaluation Harness**

Author: **Yashila Bordag**

## Overall assessment

The paper has a credible research shape: it states a narrow conjecture, defines falsifiers, separates controlled from model-backed evidence, reports negative results, and turns open gaps into confirmatory experiments. Its strongest contribution is not the CVaR objective by itself. It is the conjunction of conditional-tail selection, matched failure-set geometry, deployment interaction, stack-specific adaptation, and immutable held-out transfer.

The paper is strongest when it is conservative. The sentence “These findings support mechanism-backed feasibility, not a general robustness claim” should remain central to the abstract, presentation, and interview discussion.

## Changes made in this review

- Replaced the anonymous author line with **Yashila Bordag**.
- Added Yashila Bordag to the PDF metadata.
- Corrected the attack-cell tuple from seven to eight dimensions by separating directness and reversibility.
- Defined the CVaR convention explicitly as mean loss in the worst q fraction, with q = 0.10 in the registered experiments.

## Major strengths

1. **Claim discipline.** The paper labels controlled fixtures, small online canaries, and offline monitoring as different evidence tiers.
2. **Falsifiability.** Selector contrast, adaptive persistence, deployment interaction, and transfer each have failure conditions.
3. **Operational detail.** The paper states model revision, agent counts, execution location, defense placement, sample sizes, and artifact paths.
4. **Negative results.** E01 and E04 remain false despite favorable secondary diagnostics.
5. **Reproducible design.** Immutable manifests, paired seeds, trace hashing, frozen gates, and split discipline are part of the research object rather than afterthoughts.

## Main limitations before a strong research claim

1. **No model-backed complementarity estimate yet.** Gamma is currently supported by controlled fixtures, not matched LLM-generated shadow forks.
2. **No autonomous equal-budget best response.** Registered adaptations and goal pressure are not equivalent to optimizing an attacker independently against each deployed stack.
3. **No genuinely held-out model family.** Current E04 model-family labels are synthetic; the strong transfer claim needs a distinct 7-9B instruction model.
4. **Small online canaries.** The 64-episode channel study and 24-episode workflow study demonstrate mechanisms but provide wide rate uncertainty.
5. **Offline sequential defenses.** Phase 5 measures monitoring performance after generation and therefore does not establish online prevention or utility effects.
6. **Incomplete forensic replay for Phase 5.** Per-episode scores and hashes are retained, but full generated text is not.

## Recommended next paper revision after new experiments

- Add a model-backed shadow-fork table with singleton bypass, joint bypass, enforced-stack bypass, Gamma, realized gain, and interaction gap.
- Add a budget-accounting table for each stack-specific attacker: queries, tokens, tools, rollouts, wall time, and search seeds.
- Add a held-out-transfer regression with enough candidate stacks to estimate the incremental value of Gamma beyond singleton quality, utility, and latency.
- Include a compact threat-to-observation matrix showing which carriers are visible to each defense and which remain out of scope.
- Add an ethics/responsible-release paragraph explaining that attack policies are evaluated in a controlled, permissioned environment and that artifacts omit operational exploitation targets.
- Add an appendix with exact manifest hashes and commands for every headline table.

## Recommended submission positioning

In its current form, the paper should be positioned as an evaluation-harness and mechanism-evidence paper with a registered confirmatory program. It should not be positioned as proof that the proposed selector is state of the art. After the three decisive experiments pass, the paper can make the stronger claim that validation-time failure geometry is a useful predictor for robust multi-agent defense composition.

