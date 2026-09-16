---
title: Inter-Annotator Agreement for LLM Evaluation Guide
id: inter-annotator-agreement-for-llm-evaluation-guide
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:28:17.599292Z'
source: https://datavlab.ai/post/inter-annotator-agreement-llm-evaluation-guide
source_domain: datavlab.ai
fetched_at: '2026-09-15T02:28:17.596294Z'
fetch_provider: builtin
status: draft
type: note
tier: unknown
content_type: unknown
deprecated: false
---

Inter-Annotator Agreement for LLM Evaluation Guide
Let's discuss your project
Get a Quote
Home
/
Blog
/
LLM Evaluation
/
Inter-Annotator Agreement for LLM Evaluation: A Practitioner's Guide
Inter-Annotator Agreement for LLM Evaluation: A Practitioner's Guide
Last updated:
03.08.2026
Read time:
X
min
Author:
Roy Andraos
Inter-annotator agreement is the quantitative foundation of every credible LLM evaluation pipeline. Most teams treat IAA as a one-time pilot check rather than the continuous quality signal it actually is, then wonder why their benchmark numbers contradict each other and their reward models fail to converge. This article gives AI leads, ML engineers, and operations managers a strategic framework for IAA: why disagreement is information rather than noise, the four metrics that actually matter (Cohen's kappa, Fleiss kappa, Krippendorff's alpha, correlation metrics), the right targets calibrated to task subjectivity (0.90+ for objective tasks, 0.70-0.85 for moderately subjective, 0.60-0.75 for inherently subjective like RLHF preference data), how to operate IAA as a continuous signal with overlap strategy and intervention protocols, and the four conditions where IAA itself can be misleading. Special focus on what European teams need for EU AI Act compliance documentation.
Topics
Text Link
Keypoints
Inter-annotator agreement is the quantitative foundation of every credible LLM evaluation pipeline.
Most teams treat IAA as a one-time pilot check rather than the continuous quality signal it actually is, then wonder why their benchmark numbers contradict each other and their reward models fail to converge.
Special focus on what European teams need for EU AI Act compliance documentation.
For RLHF preference data, ranking agreement metrics like Kendall's tau or the Bradley-Terry model framework (used in reward model training) capture the relative nature of preferences better than categorical agreement.
When two domain experts disagree about whether an LLM response is "helpful" or "harmful," who is right? When three annotators rate the same model output 4, 5, and 2 on a quality scale, what do you actually know about that output? When fifty annotators label preference data for RLHF and produce 60% consensus, is that good, bad, or expected?
These questions sit at the foundation of every LLM evaluation pipeline that uses human judgment. The answers determine whether your benchmark numbers mean anything, whether your reward model is learning something coherent, and whether your compliance documentation will hold up to regulatory scrutiny. Yet most teams treat inter-annotator agreement as a one-time pilot check rather than the continuous quality signal it actually is.
Inter-annotator agreement (IAA) is not just a methodology checkbox borrowed from academic NLP. It is the only quantitative way to know whether your annotation guidelines are clear enough, your annotators are calibrated enough, and your evaluation results are reliable enough to drive decisions. Without it, two teams running the "same" evaluation on the same model can produce contradictory conclusions and never know why.
This article is for AI leads, ML engineers, and operations managers running human evaluation pipelines for LLM products. We focus less on the statistical mathematics (which other resources cover well) and more on the strategic question:
which agreement metrics actually matter for which evaluation tasks, what targets should you set, and how do you operate IAA as a continuous quality signal rather than a one-time gate?
Why Disagreement Is Information, Not Noise
The first conceptual shift required to use IAA well is recognizing that annotator disagreement is not a failure to be eliminated. It is informative signal that, when measured correctly, tells you something important about your task, your guidelines, or your annotators.
For objective tasks (does this response contain the year 2024? is this code syntactically valid?), disagreement indicates either guideline ambiguity or annotator error. The fix is straightforward: tighten guidelines, retrain annotators, or both. Target agreement is high (0.90+) because the task allows it.
For moderately subjective tasks (does this response sound professional? is this summary complete?), disagreement reflects genuine interpretive variance even among careful annotators. Target agreement is moderate (0.70-0.85). Forcing higher agreement through over-constrained guidelines tends to reduce evaluation quality, not improve it: it pushes annotators to apply rules mechanically rather than exercise the judgment the task requires.
For inherently subjective tasks (which of these two responses do you prefer? how appropriate is this tone?), disagreement is the signal.
For tasks with genuine ambiguity, perfect agreement is neither achievable nor desirable. The signal is in the statistical distribution of preferences across annotators, not in unanimous votes
. This is especially true for RLHF preference data, where the variance across annotators captures real human disagreement that the model needs to learn from.
The mistake teams make is applying objective-task standards to subjective tasks, then concluding their annotation pipeline is broken when agreement comes in at 0.65. The pipeline is not broken; the target was wrong. The mistake teams also make is applying subjective-task tolerance to objective tasks, then accepting noisy data when calibration would have produced reliable signal.
The Metrics That Actually Matter
Three IAA metrics cover most production annotation needs. Each has specific use cases, specific assumptions, and specific failure modes when applied incorrectly.
Cohen's kappa (two annotators, categorical)
Cohen's kappa addresses chance-level agreement by computing the ratio of observed agreement above chance to maximum possible agreement above chance, yielding a value from -1 (perfect disagreement) to 1 (perfect agreement)
. The 1960 statistic was originally developed for psychiatric diagnosis reliability and remains the standard for two-annotator categorical tasks.
When to use: pairwise comparison of two annotators on binary or multi-class categorical labels (sentiment categories, content moderation categories, intent classification). Simple to compute. Well-understood interpretation.
When not to use: more than two annotators, ordinal or continuous labels, or when annotators do not all see the same items. Cohen's kappa can also produce misleading scores when class distribution is highly imbalanced; a 90/10 split can yield high kappa even from near-random labeling.
Fleiss kappa (multiple annotators, categorical)
Fleiss kappa extends Cohen's kappa to handle more than two annotators. It assumes annotators are interchangeable and that all items receive the same number of ratings, which is restrictive but common in pilot studies and calibration runs.
When to use: pilot studies where 3-10 annotators all rate the same items on categorical labels. Useful for guideline calibration before scaling to production volume.
When not to use: production pipelines where different items receive different annotator coverage, or when you have ordinal/continuous data. The interchangeability assumption rarely holds in practice when annotators have different expertise levels.
Krippendorff's alpha (production pipelines)
For production annotation pipelines, Krippendorff's alpha is the metric that actually scales.
It generalizes across any number of annotators, handles missing data, and supports nominal, ordinal, interval, and ratio measurement scales
. The flexibility comes at the cost of more complex computation, but tooling (Label Studio, Datasaur, Appen, custom Python implementations) makes this manageable.
When to use: production annotation at scale, especially when not every annotator sees every item, when annotation tasks include ordinal scales (1-5 quality ratings), or when you need to compare across annotation modalities.
Critical implementation detail: alpha depends on correctly specifying both your data type (nominal, ordinal, interval) and the distance metric. Treating ordinal data as nominal underestimates agreement; treating nominal data as ordinal overstates it. The choice matters substantially for the resulting score.
Correlation metrics (continuous ratings)
For tasks where annotators provide continuous ratings (1-10 quality scores, 0-1 confidence values), Pearson and Spearman correlations between annotator pairs measure rank-order consistency without requiring exact agreement. For preference ranking specifically, Kendall's tau captures whether annotators consistently order pairs the same way, even when their absolute scores differ.
For RLHF preference data, ranking agreement metrics like Kendall's tau or the Bradley-Terry model framework (used in reward model training) capture the relative nature of preferences better than categorical agreement.
Setting the Right Targets
The most consequential IAA decision is what target to set. Wrong targets either accept noisy data that compromises model training, or reject useful data that captures genuine subjectivity.
Objective tasks: 0.90+ kappa or alpha
Object detection, named entity recognition, syntactic correctness, factual accuracy verification, presence/absence labels. These tasks have clear right answers; sustained agreement below 0.90 indicates either unclear guidelines or annotator quality issues that need addressing.
For medical AI annotation, the bar is even higher.
In clinical settings, alpha greater than 0.90 is often required before releasing datasets, because clinical reliability standards demand near-perfect agreement before AI systems can be trusted
.
Moderately subjective tasks: 0.70-0.85 kappa or alpha
Content categorization, topic classification, summary completeness, response quality scoring on coarse scales. These tasks have substantial right-answer convergence but allow for legitimate interpretive differences. Below 0.70 indicates either guideline gaps or task definition that requires more refinement.
Subjective tasks: 0.60-0.75 alpha
Preference annotation for RLHF, tone evaluation, helpfulness rating on fine-grained scales, harm assessment on nuanced cases. These tasks have inherent subjective variance that no amount of guideline tightening can eliminate without distorting the task. The annotator disagreement distributions become training signal for the model.
For sarcasm detection, social media tone analysis, and similar deeply subjective tasks, alpha can legitimately come in below 0.35.
A sarcasm detection experiment using Twitter data found Krippendorff's alpha scores often below 0.35, and in some cases even negative, indicating less than chance agreement among certain annotator pairs
. The conclusion was not that the annotators were bad; it was that sarcasm identification is fundamentally subjective and benchmarks should be designed accordingly.
Avoid the false-precision trap
The temptation when reading IAA literature is to report alpha to four decimal places and treat tiny differences as meaningful. They are not. The 95% confidence interval on alpha typically spans 0.05-0.10 even with hundreds of annotated items. An alpha of 0.78 versus 0.81 tells you almost nothing useful about which annotation pipeline is better. Treat IAA scores as bands (low, moderate, good, excellent) rather than precise measurements.
Operating IAA as a Continuous Signal
The most common IAA mistake is treating it as a one-time pilot phase activity.
IAA must be monitored continuously throughout the annotation campaign, not just measured during pilot
. The reason is simple: annotator drift is real. Quality degrades over weeks of repetitive annotation. Guidelines that were clear in the pilot become ambiguous when novel edge cases arise. Annotators who were calibrated together drift apart as their individual interpretations diverge.
Overlap strategy
Production annotation rarely has every annotator rate every item; the cost would be prohibitive. The standard pattern is structured overlap: 5-15% of items receive 2-3 annotations specifically for IAA monitoring, while the remaining items receive single annotation for cost efficiency.
The overlap items should be sampled to represent the full distribution of annotation work, not concentrated in easy or hard cases. Random sampling within strata (by domain, query type, expected difficulty) typically produces the most useful overlap.
Continuous monitoring
Compute IAA on rolling windows (last 1000 annotations, last week of work, last batch). Track alpha or kappa over time. Set alerts for drops below threshold. When agreement drops, investigate before the issue propagates through subsequent annotation work.
The patterns to watch for: gradual decline (annotator fatigue, guideline drift), sudden drop (new annotator joined without proper calibration, new edge case category arrived), sustained low agreement on specific subcategories (guideline gap for that specific case).
Intervention protocols
When IAA drops, the response should be calibrated to the cause. For annotator-specific issues (one annotator producing outlier patterns), individual feedback and re-training. For category-specific issues (sudden drop on one type of input), guideline clarification and worked examples. For general decline, group calibration sessions where annotators discuss disagreements on specific items and reach explicit consensus on how to handle them.
The intervention should not be "force higher agreement at all costs." For subjective tasks, that path destroys the natural variance that captures real human judgment. The intervention should be "ensure disagreement is informed disagreement (annotators understand the choices and have considered alternatives) rather than uninformed disagreement (annotators are inconsistent within their own work)."
IAA for RLHF: Why Preference Data Is Different
Reinforcement learning from human feedback uses preference annotations to train reward models. The IAA conversation here differs meaningfully from classification or quality scoring tasks.
For preference annotation, the goal is not consensus. The goal is capturing the distribution of human preferences across the relevant population. If 70% of annotators prefer response A over response B, that 70/30 distribution is the training signal. Forcing 95% consensus through tight guidelines would actually reduce the quality of the resulting reward model by removing the natural variance.
The right IAA target for RLHF preference data is around 0.60-0.75 alpha. Below that, annotators are not understanding the task or guidelines need refinement. Above 0.85, annotators are likely applying mechanical rules rather than exercising the judgment the model needs to learn.
For high-stakes preference annotation (safety-critical applications, alignment-relevant judgments), the additional layer of probabilistic label models (Dawid-Skene and similar approaches) handles annotator reliability variance better than simple aggregation. These models estimate per-annotator quality from the data itself and weight contributions accordingly, producing more reliable consensus signals than majority voting.
For European teams building reward models under EU AI Act compliance, the documentation burden is substantial.
Preference dataset construction with EU-based annotators
generates the IAA documentation that high-risk AI systems require, with annotator demographics and methodology decisions captured for regulatory review.
When IAA Itself Is Misleading
Several conditions can produce IAA scores that look fine but mask serious annotation quality problems.
Class imbalance distortion
When one label dominates (90% positive examples), high observed agreement can coexist with random labeling on the minority class. The chance correction in kappa and alpha helps but does not fully eliminate this. For imbalanced datasets, report IAA per class in addition to overall, and pay particular attention to the minority class where the actionable signal usually lives.
Surface agreement, deep disagreement
Annotators can agree on labels while disagreeing fundamentally on why. Two annotators might both rate a response as "helpful" for entirely different reasons, one focused on completeness and the other on tone. The label-level IAA is high; the underlying judgment quality is poor. Periodic critique reviews (where annotators explain their reasoning on a sample of items) catch this pattern that pure label IAA misses.
Annotator collusion or shared bias
When annotators come from the same training, share the same demographic background, or work in close communication, their agreement can reflect shared assumptions rather than genuine inter-annotator reliability. The IAA score is high because the annotators are essentially one perspective with multiple voices. Diversity in annotator pools (background, geography, expertise) often produces lower IAA but more representative judgments.
Pilot-only measurement
Pilot phase IAA almost always exceeds production IAA because pilot conditions (smaller scale, focused attention, recent training) do not replicate. Teams that report only pilot IAA in their compliance documentation are reporting a number that does not reflect the production reality. Continuous IAA reporting is the only honest approach for production annotation.
Building IAA Infrastructure for Production
For teams operating annotation at scale, here is the practical infrastructure pattern that works.
Tooling layer
Label Studio, Datasaur, or comparable annotation platforms provide built-in IAA computation. For custom workflows, Python implementations (using packages like krippendorff or simpledorff) integrate cleanly into evaluation pipelines. The choice between hosted platforms and custom infrastructure depends on volume, customization needs, and compliance requirements.
Dashboards and alerts
IAA scores need visibility. Operations dashboards should display rolling IAA per project, per task type, per annotator cohort. Alerts should fire when scores drop below configured thresholds. Without these, IAA degradation goes unnoticed until it has already corrupted substantial annotation work.
Documentation for compliance
For EU AI Act high-risk applications, IAA evidence is part of the required compliance documentation. Capture and retain: annotator demographics (without compromising privacy), guideline versions, IAA scores per annotation batch, calibration session records, and intervention actions taken in response to IAA drops. This documentation will be required during regulatory review.
Continuous calibration
Quarterly group calibration sessions where annotators discuss specific challenging items and reach explicit consensus on how to handle them. These sessions are expensive in annotator time but pay back through sustained IAA and reduced individual drift. Skip them at the cost of slowly degrading annotation quality.
What This Means for European Annotation Operations
For European teams operating annotation pipelines under EU AI Act compliance, IAA is not optional infrastructure. The Act's high-risk category requires demonstrated annotation methodology, documented quality processes, and traceable decisions. IAA reporting is the quantitative backbone of this documentation.
EU-based annotator pools provide additional advantages beyond compliance. Cultural and linguistic familiarity with European context produces more representative judgments for European AI products. Native-speaker annotation of French, German, Italian, and Spanish content avoids the systematic errors that English-trained annotators or LLM judges introduce on multilingual content.
For teams deploying AI systems serving European users, the combination of EU sovereignty, native-language expertise, and rigorous IAA documentation increasingly differentiates evaluation pipelines that hold up to regulatory scrutiny from those that do not.
DataVLab operates LLM evaluation services
with EU-based domain experts specifically designed to produce the IAA documentation that high-stakes AI applications require.
The Honest Bottom Line
Inter-annotator agreement is the quantitative foundation of every credible LLM evaluation pipeline. Without it, your benchmark numbers, your reward model training data, and your compliance documentation rest on assumptions you have not actually verified. With it, you have a continuous quality signal that catches degradation before it propagates and demonstrates evaluation reliability to anyone who asks.
The right metric depends on your task. Cohen's kappa for two-annotator categorical work. Fleiss kappa for multi-annotator pilot studies. Krippendorff's alpha for production scale. Correlation metrics for continuous ratings. Bradley-Terry frameworks for preference data. Match the metric to the task; do not pick one and force everything through it.
The right target depends on task subjectivity. 0.90+ for objective tasks. 0.70-0.85 for moderately subjective. 0.60-0.75 for inherently subjective. Forcing higher targets on subjective tasks destroys the signal you need; accepting lower targets on objective tasks accepts noisy data that compromises everything downstream.
The right operating model is continuous, not pilot-only. Structured overlap of 5-15% of production work. Rolling IAA computation. Alerts on drops. Quarterly calibration sessions. Documented intervention protocols. This infrastructure is the difference between annotation pipelines that produce reliable evaluation data and those that produce numbers nobody should trust.
For teams just starting, the priority order is: pick the right metric for your task type, set targets calibrated to task subjectivity, build continuous monitoring before scaling, document everything. The compliance and quality benefits compound. The cost of skipping this is invisible until your first regulatory audit or your first reward model that fails to converge for reasons you cannot explain.
If You Are Building Annotation Quality Infrastructure
DataVLab provides annotation and evaluation services for European AI teams operating under EU AI Act compliance constraints. Our EU-based domain experts work within structured IAA monitoring frameworks designed to produce the documentation that high-risk AI applications require. We work with European AI labs, defense programs, and enterprise teams whose annotation pipelines need rigorous quality evidence rather than pilot-only IAA reporting. If you are designing annotation quality infrastructure and want to discuss IAA targets, monitoring patterns, or compliance documentation,
get in touch
.
What is Inter-Annotator agreement for LLM evaluation?
Inter-annotator agreement is the quantitative foundation of every credible LLM evaluation pipeline. Most teams treat IAA as a one-time pilot check rather than the continuous quality signal it actually is, then wonder why their benchmark numbers contradict each other and their reward models fail to converge.
Why is Disagreement Information, not noise?
The first conceptual shift required to use IAA well is recognizing that annotator disagreement is not a failure to be eliminated. For objective tasks (does this response contain the year 2024? is this code syntactically valid?), disagreement indicates either guideline ambiguity or annotator error.
What does the section on “Setting the right targets” explain?
The most consequential IAA decision is what target to set. Wrong targets either accept noisy data that compromises model training, or reject useful data that captures genuine subjectivity. Object detection, named entity recognition, syntactic correctness, factual accuracy verification, presence/absence labels.
What does the article explain about when IAA itself is misleading?
Several conditions can produce IAA scores that look fine but mask serious annotation quality problems. When one label dominates (90% positive examples), high observed agreement can coexist with random labeling on the minority class. The chance correction in kappa and alpha helps but does not fully eliminate this.
What does this mean for European annotation operations?
For European teams operating annotation pipelines under EU AI Act compliance, IAA is not optional infrastructure. The Act's high-risk category requires demonstrated annotation methodology, documented quality processes, and traceable decisions. IAA reporting is the quantitative backbone of this documentation.
How can teams ensure quality in Inter-Annotator agreement for LLM evaluation?
Our EU-based domain experts work within structured IAA monitoring frameworks designed to produce the documentation that high-risk AI applications require. We work with European AI labs, defense programs, and enterprise teams whose annotation pipelines need rigorous quality evidence rather than pilot-only IAA reporting.
Roy Andraos
CEO DataVlab
Founder of DataVLab, a data annotation company supporting AI teams across healthcare, agriculture, retail, satellite imagery and other vision-intensive industries. Since 2019, we have helped organizations turn complex image, video and text data into reliable training datasets, combining operational expertise with a strong focus on annotation quality and scalability.
Get  Started Now
Let's discuss your project
We can provide realible and specialised annotation services and improve your AI's performances
Get a Quote
Insights
Blog & Resources
Explore our latest articles and insights on Data Annotation
View all
View all
August 3, 2026
LLM Evaluation
Red-Teaming LLMs: A Practitioner's Guide for 2026
Read more
August 3, 2026
LLM Evaluation
Human Evaluation of LLMs in 2026: A Practical Guide for Teams That Need Real Reliability
Read more
August 3, 2026
LLM Evaluation
RAG Evaluation: Methods and Metrics That Predict Production Quality
Read more
Industries
Explore Our Different
Industry Applications
Get a Quote
Sovereign Data Annotation for European Defense and Aerospace AI
Defense
LLM Evaluation and Annotation for European Legal AI
Legal & LegalTech
Our data labeling services cater to various industries, ensuring high-quality annotations tailored to your specific needs.
Our Solutions
Data Annotation Services
Unlock the full potential of your AI applications with our expert data labeling tech. We ensure high-quality annotations that accelerate your project timelines.
Get a Quote
LLM Evaluation Services
LLM Evaluation Services by Multilingual Expert Reviewers
Human evaluation of large language models with expert reviewers, calibrated rubrics, and reliable inter-annotator agreement. EU-based teams for projects that require quality and sovereignty.
Show more
Model Benchmarking Services
Custom LLM Benchmarking for Decisions That Matter
Independent benchmarking of LLMs across domains, languages, and use cases to support vendor selection, procurement, and strategic AI decisions. Custom evaluation frameworks built around your actual requirements.
Show more
RAG Evaluation Services
RAG System Evaluation: Measure What Matters Before Production
End-to-end evaluation of retrieval-augmented generation systems across retrieval quality, context relevance, groundedness, faithfulness, and answer utility. For teams shipping RAG to production.
Show more
LLM Red Teaming Services
LLM Red Teaming: Find Failure Modes Before Your Users Do
Adversarial evaluation of large language models by safety and domain experts. Jailbreaks, prompt injection, harmful outputs, hallucinations, and bias discovery for AI teams shipping production systems.
Show more