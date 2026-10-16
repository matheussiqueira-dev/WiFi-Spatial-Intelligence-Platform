"""Composition boundary. The legacy laboratory is opt-in and lazily imported."""

from app.adapters.native import NativeProvider


def build_provider(source, config, settings):
    if source in {"synthetic-native", "SIMULATED"}:
        return NativeProvider(config)
    if source == "RUVIEW_STREAM" and settings and settings.legacy_lab_enabled:
        from app.ruview import RuViewProvider

        return RuViewProvider(settings)
    raise ValueError("legacy laboratory disabled; enable explicitly for compatibility testing")
