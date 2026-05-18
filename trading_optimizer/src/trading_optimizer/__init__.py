"""LLM-as-Optimizer portfolio return/risk optimization."""

from .portfolio_return_optimizer import (
    PortfolioCandidate,
    PortfolioCandidateBatch,
    WeightedPortfolioEvaluation,
    latest_asset_prices,
    optimize_random_return_under_risk,
    optimize_return_under_risk,
    portfolio_metrics_rolling,
    plot_walk_forward_comparison,
    run_multi_model_walk_forward_llm,
    run_walk_forward_baseline,
    run_walk_forward_llm_optimizer,
    safe_model_dir_name,
    share_allocation,
)

__all__ = [
    "PortfolioCandidate",
    "PortfolioCandidateBatch",
    "WeightedPortfolioEvaluation",
    "latest_asset_prices",
    "optimize_random_return_under_risk",
    "optimize_return_under_risk",
    "portfolio_metrics_rolling",
    "plot_walk_forward_comparison",
    "run_multi_model_walk_forward_llm",
    "run_walk_forward_baseline",
    "run_walk_forward_llm_optimizer",
    "safe_model_dir_name",
    "share_allocation",
]

__version__ = "0.1.0"
