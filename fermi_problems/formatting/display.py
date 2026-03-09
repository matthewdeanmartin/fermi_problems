"""Result display formatting for ChainResult and Estimate."""

from fermi_problems.core.chain import ChainResult
from fermi_problems.core.estimate import Estimate
from fermi_problems.formatting.notation import to_human, to_scientific, to_engineering


def format_estimate(estimate: Estimate, style: str = "human") -> str:
    """Format a single estimate.

    style: 'human', 'scientific', 'engineering'
    """
    display_value = estimate.value / estimate._display_scale if estimate._display_scale != 0 else estimate.value
    unit_str = estimate._display_unit_str

    if style == "scientific":
        val_str = to_scientific(display_value, estimate.sig_figs)
    elif style == "engineering":
        val_str = to_engineering(display_value, estimate.sig_figs)
    else:
        val_str = to_human(display_value, estimate.sig_figs)

    low_si, high_si = estimate.confidence_interval()
    low_disp = low_si / estimate._display_scale if estimate._display_scale != 0 else low_si
    high_disp = high_si / estimate._display_scale if estimate._display_scale != 0 else high_si

    low_str = to_scientific(low_disp, estimate.sig_figs)
    high_str = to_scientific(high_disp, estimate.sig_figs)

    return f"~{val_str} {unit_str} [{low_str}, {high_str}]"


def format_chain_result(result: ChainResult, show_factors: bool = True) -> str:
    """Format a ChainResult as a multi-line string.

    Example output:
        Estimate: ~108 tuners
        90% CI: [25, 460] tuners (best case, lognormal)
        Worst case: [11, 1080] tuners (interval arithmetic)
        Significant figures: 1
        Unit check: PASS
    """
    est = result.estimate
    unit_str = est._display_unit_str

    display_value = est.value / est._display_scale if est._display_scale != 0 else est.value
    val_str = to_human(display_value, result.sig_figs)

    best_low = result.best_case[0] / est._display_scale if est._display_scale != 0 else result.best_case[0]
    best_high = result.best_case[1] / est._display_scale if est._display_scale != 0 else result.best_case[1]
    worst_low = result.worst_case[0] / est._display_scale if est._display_scale != 0 else result.worst_case[0]
    worst_high = result.worst_case[1] / est._display_scale if est._display_scale != 0 else result.worst_case[1]

    lines = [
        f"Estimate: ~{val_str} {unit_str}",
        f"90% CI: [{to_human(best_low)}, {to_human(best_high)}] {unit_str} (best case, lognormal)",
        f"Worst case: [{to_human(worst_low)}, {to_human(worst_high)}] {unit_str} (interval arithmetic)",
        f"Significant figures: {result.sig_figs}",
        f"Unit check: {'PASS' if result.unit_check else 'FAIL'}",
    ]

    if not result.unit_check and result.unit_mismatch_detail:
        lines.append(f"  {result.unit_mismatch_detail}")

    if show_factors and hasattr(est, "_chain_factors"):
        lines.append("Factors:")
        for name, factor_est, is_divisor in est._chain_factors:
            sign = "/" if is_divisor else "="
            factor_display = (
                factor_est.value / factor_est._display_scale if factor_est._display_scale != 0 else factor_est.value
            )
            low_si, high_si = factor_est.confidence_interval()
            low_disp = low_si / factor_est._display_scale if factor_est._display_scale != 0 else low_si
            high_disp = high_si / factor_est._display_scale if factor_est._display_scale != 0 else high_si
            factor_str = f"{to_scientific(factor_display)} [{to_scientific(low_disp)}, {to_scientific(high_disp)}]"
            lines.append(f"  {name:<20} {sign} {factor_str} {factor_est._display_unit_str}")

    return "\n".join(lines)
