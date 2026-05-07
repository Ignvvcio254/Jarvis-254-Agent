from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class ProviderStatus:
    name: str
    configured: bool
    env_var: str
    notes: str


@dataclass(frozen=True)
class ProviderPlan:
    selected: str | None
    fallbacks: list[str]
    unavailable: list[str]
    reason: str


PROVIDER_ENV_MAP = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
}


DEFAULT_PROVIDER_ORDER = ["anthropic", "openai", "gemini"]


def detect_providers() -> list[ProviderStatus]:
    statuses: list[ProviderStatus] = []
    for name, env_var in PROVIDER_ENV_MAP.items():
        configured = bool(os.getenv(env_var, "").strip())
        notes = "ready" if configured else "missing key"
        statuses.append(
            ProviderStatus(name=name, configured=configured, env_var=env_var, notes=notes)
        )
    return statuses


def _normalize_provider_order(order: list[str]) -> list[str]:
    normalized: list[str] = []
    for item in order:
        name = item.lower().strip()
        if not name:
            continue
        if name not in PROVIDER_ENV_MAP:
            continue
        if name in normalized:
            continue
        normalized.append(name)
    for default_name in DEFAULT_PROVIDER_ORDER:
        if default_name not in normalized:
            normalized.append(default_name)
    return normalized


def configured_provider_order() -> list[str]:
    raw = os.getenv("JARVIS_PROVIDER_ORDER", "")
    if not raw.strip():
        return list(DEFAULT_PROVIDER_ORDER)
    parts = [segment for segment in raw.split(",")]
    return _normalize_provider_order(parts)


def build_provider_plan(preferred: str | None = None) -> ProviderPlan:
    statuses = {item.name: item for item in detect_providers()}
    order = configured_provider_order()

    preferred_name = ""
    if preferred:
        preferred_name = preferred.lower().strip()

    preferred_ready = bool(
        preferred_name and preferred_name in statuses and statuses[preferred_name].configured
    )
    if preferred_ready:
        selected = preferred_name
        reason = "preferred provider is configured"
    else:
        selected = None
        reason = "no configured providers found"
        for name in order:
            status = statuses.get(name)
            if status and status.configured:
                selected = name
                reason = "selected first configured provider from priority order"
                break

    fallback_candidates = [name for name in order if name != selected]
    fallbacks = [name for name in fallback_candidates if statuses[name].configured]
    unavailable = [name for name in order if not statuses[name].configured]

    if preferred_name and not preferred_ready:
        if preferred_name in PROVIDER_ENV_MAP:
            reason = f"preferred provider '{preferred_name}' is not configured"
        else:
            reason = f"preferred provider '{preferred_name}' is unknown"

    return ProviderPlan(
        selected=selected,
        fallbacks=fallbacks,
        unavailable=unavailable,
        reason=reason,
    )


def select_best_provider(preferred: str | None = None) -> str | None:
    return build_provider_plan(preferred=preferred).selected
