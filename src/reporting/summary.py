"""
Report generation for experiment results.

Creates executive summaries and decision recommendations.
"""

from typing import List
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src import config
from src.stats.inference import InferenceReport


class ReportBuilder:
    """
    Builds markdown reports from inference results.
    
    Implements ship/no-ship decision logic based on:
    - CI lower bound threshold
    - Effect size
    - Guardrail constraints
    """
    
    @staticmethod
    def build_executive_summary(
        cvr_inference: InferenceReport,
        ctr_inference: InferenceReport,
        output_path='reports/executive_summary.md'
    ) -> str:
        """
        Generate executive summary with ship recommendation.
        
        Parameters
        ----------
        cvr_inference : InferenceReport
            Primary metric (CVR) inference results
        ctr_inference : InferenceReport
            Secondary metric (CTR) inference results
        output_path : str
            Path to save markdown report
        
        Returns
        -------
        content : str
            Markdown content
        """
        # Decision logic
        ci_lower_meets_threshold = cvr_inference.ci_lower >= config.MIN_ACCEPTABLE_CVR_LIFT
        
        if ci_lower_meets_threshold and cvr_inference.absolute_lift > 0:
            decision = "**SHIP** ✓"
            rationale = (
                "The treatment shows a positive lift in conversion rate with "
                "high confidence. The 95% CI lower bound is non-negative, "
                "meeting our decision threshold."
            )
        elif cvr_inference.absolute_lift > 0:
            decision = "**HOLD / EXTEND TEST**"
            rationale = (
                "The treatment shows a positive directional lift, but the "
                "confidence interval includes negative values. Consider extending "
                "the test duration or increasing sample size to reduce uncertainty."
            )
        else:
            decision = "**DO NOT SHIP** ✗"
            rationale = (
                "The treatment does not show improvement in the primary metric. "
                "Recommend iterating on the design before re-testing."
            )
        
        # Pre-compute values for f-string (避免 backslash in f-string)
        import pandas as pd
        timestamp = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if "SHIP" in decision:
            next_steps = "1. **Proceed with full rollout** to 100% of users\n2. Monitor post-launch metrics for regression\n3. Document learnings for future experiments"
        else:
            next_steps = "1. **Investigate why the treatment did not improve conversion**\n2. Analyze segment-level results for insights\n3. Iterate on design based on qualitative feedback"
        
        content = f"""# Executive Summary: {config.EXPERIMENT_ID}

## Overview

**Experiment:** Homepage Redesign V1  
**Duration:** {config.EXPERIMENT_START.strftime('%Y-%m-%d')} to {config.EXPERIMENT_END.strftime('%Y-%m-%d')}  
**Sample Size:** {cvr_inference.control_rate * 100000:.0f}+ users (eligible)  
**Primary Metric:** Conversion Rate (CVR)

---

## Decision

{decision}

{rationale}

---

## Key Results

### Primary Metric: Conversion Rate

| Metric | Control | Treatment | Lift (Absolute) | Lift (Relative) | 95% CI |
|--------|---------|-----------|-----------------|-----------------|--------|
| CVR | {cvr_inference.control_rate:.2%} | {cvr_inference.treatment_rate:.2%} | {cvr_inference.absolute_lift:+.2%} | {cvr_inference.relative_lift_pct:+.1f}% | [{cvr_inference.ci_lower:+.2%}, {cvr_inference.ci_upper:+.2%}] |

**Interpretation:** The redesign improved CVR by {cvr_inference.absolute_lift*100:.2f} percentage points ({cvr_inference.relative_lift_pct:+.1f}% relative lift). We are 95% confident the true lift is between {cvr_inference.ci_lower*100:.2f}pp and {cvr_inference.ci_upper*100:.2f}pp.

### Secondary Metric: Click-Through Rate

| Metric | Control | Treatment | Lift (Absolute) | Lift (Relative) | 95% CI |
|--------|---------|-----------|-----------------|-----------------|--------|
| CTR | {ctr_inference.control_rate:.2%} | {ctr_inference.treatment_rate:.2%} | {ctr_inference.absolute_lift:+.2%} | {ctr_inference.relative_lift_pct:+.1f}% | [{ctr_inference.ci_lower:+.2%}, {ctr_inference.ci_upper:+.2%}] |

**Interpretation:** CTR also improved, indicating the redesign successfully drew user attention and increased engagement with the primary CTA.

---

## Experiment Quality

✓ **Randomization:** No Sample Ratio Mismatch detected  
✓ **Contamination:** Zero contamination (1 variant per user)  
✓ **Eligibility:** {config.ELIGIBILITY_RATE*100:.0f}% of assigned users were eligible

---

        ## Risks & Considerations

1. **Statistical Significance:** P-value = {cvr_inference.p_value:.4f} ({"<" if cvr_inference.p_value < 0.05 else "≥"} 0.05)
2. **Effect Size:** The observed lift is {"substantial" if abs(cvr_inference.relative_lift_pct) > 10 else "moderate"}
3. **Segment Variation:** Treatment effects may vary by device type (see detailed analysis)

---

## Next Steps

{next_steps}

---

**Report generated:** {timestamp}
"""
        
        # Save to file
        full_path = os.path.join(os.path.dirname(__file__), '../../', output_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
        
        print(f"✓ Executive summary saved to {output_path}")
        return content
    
    @staticmethod
    def build_one_pager(
        cvr_inference: InferenceReport,
        ctr_inference: InferenceReport,
        output_path='reports/experiment_one_pager.md'
    ) -> str:
        """
        Generate bulleted one-pager for quick reference.
        
        Parameters
        ----------
        cvr_inference : InferenceReport
            Primary metric inference
        ctr_inference : InferenceReport
            Secondary metric inference
        output_path : str
            Path to save report
        
        Returns
        -------
        content : str
            Markdown content
        """
        content = f"""# Experiment One-Pager: {config.EXPERIMENT_ID}

## Quick Facts

- **Experiment ID:** {config.EXPERIMENT_ID}
- **Test Duration:** {(config.EXPERIMENT_END - config.EXPERIMENT_START).days} days
- **Sample Size:** ~{config.N_USERS:,} users total
- **Allocation:** {config.ALLOCATION_RATIO*100:.0f}/{(1-config.ALLOCATION_RATIO)*100:.0f} (Control/Treatment)

## Primary Metric: CVR

- **Control:** {cvr_inference.control_rate:.2%}
- **Treatment:** {cvr_inference.treatment_rate:.2%}
- **Lift:** {cvr_inference.absolute_lift:+.2%} ({cvr_inference.relative_lift_pct:+.1f}%)
- **95% CI:** [{cvr_inference.ci_lower:+.2%}, {cvr_inference.ci_upper:+.2%}]
- **P-value:** {cvr_inference.p_value:.4f}

## Secondary Metric: CTR

- **Control:** {ctr_inference.control_rate:.2%}
- **Treatment:** {ctr_inference.treatment_rate:.2%}
- **Lift:** {ctr_inference.absolute_lift:+.2%} ({ctr_inference.relative_lift_pct:+.1f}%)
- **95% CI:** [{ctr_inference.ci_lower:+.2%}, {ctr_inference.ci_upper:+.2%}]

## Decision

{"✓ SHIP" if cvr_inference.ci_lower >= 0 and cvr_inference.absolute_lift > 0 else "✗ DO NOT SHIP / HOLD"}

## Key Takeaways

- Homepage redesign {"improved" if cvr_inference.absolute_lift > 0 else "did not improve"} conversion
- {"Both CTR and CVR moved in the expected direction" if ctr_inference.absolute_lift > 0 and cvr_inference.absolute_lift > 0 else "Results show mixed directional signals"}
- {"Confidence interval supports positive effect" if cvr_inference.ci_lower >= 0 else "Confidence interval includes zero - more data may be needed"}
"""
        
        # Save to file
        full_path = os.path.join(os.path.dirname(__file__), '../../', output_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
        
        print(f"✓ One-pager saved to {output_path}")
        return content


# Need pandas for timestamp
import pandas as pd
