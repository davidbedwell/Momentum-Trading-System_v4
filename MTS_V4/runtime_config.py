from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


class RuntimeConfigurationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ResearchDirectorRuntimeConfig:
    base_url: str
    model: str
    api_key: str = ""
    timeout_seconds: int = 180

    def __post_init__(self) -> None:
        if not self.base_url.strip():
            raise RuntimeConfigurationError("Research Director base_url is required")
        if not self.model.strip():
            raise RuntimeConfigurationError("Research Director model is required")
        if self.timeout_seconds <= 0:
            raise RuntimeConfigurationError("Research Director timeout_seconds must be positive")


@dataclass(frozen=True, slots=True)
class ProductionRuntimeConfig:
    state_dir: Path
    research_director: ResearchDirectorRuntimeConfig
    max_contract_repairs: int = 3

    def __post_init__(self) -> None:
        if self.max_contract_repairs < 0:
            raise RuntimeConfigurationError("max_contract_repairs cannot be negative")

    @property
    def nexus_path(self) -> Path:
        return self.state_dir / "research_nexus.json"

    @property
    def checkpoint_path(self) -> Path:
        return self.state_dir / "active_campaign.json"

    @classmethod
    def from_env(cls) -> "ProductionRuntimeConfig":
        """Load runtime wiring only; this performs no network calls.

        Credentials remain external to source control. MTS_RD_API_KEY may be
        empty for local OpenAI-compatible servers that do not require one.
        """
        state_dir_raw = os.getenv("MTS_V4_STATE_DIR", "").strip()
        base_url = os.getenv("MTS_RD_BASE_URL", "").strip()
        model = os.getenv("MTS_RD_MODEL", "").strip()
        api_key = os.getenv("MTS_RD_API_KEY", "")
        timeout_raw = os.getenv("MTS_RD_TIMEOUT_SECONDS", "180")
        repairs_raw = os.getenv("MTS_V4_MAX_CONTRACT_REPAIRS", "3")

        missing = [
            name
            for name, value in (
                ("MTS_V4_STATE_DIR", state_dir_raw),
                ("MTS_RD_BASE_URL", base_url),
                ("MTS_RD_MODEL", model),
            )
            if not value
        ]
        if missing:
            raise RuntimeConfigurationError(
                "missing required runtime environment variables: " + ", ".join(missing)
            )
        try:
            timeout = int(timeout_raw)
            repairs = int(repairs_raw)
        except ValueError as exc:
            raise RuntimeConfigurationError(
                "MTS_RD_TIMEOUT_SECONDS and MTS_V4_MAX_CONTRACT_REPAIRS must be integers"
            ) from exc

        return cls(
            state_dir=Path(state_dir_raw).expanduser(),
            research_director=ResearchDirectorRuntimeConfig(
                base_url=base_url,
                model=model,
                api_key=api_key,
                timeout_seconds=timeout,
            ),
            max_contract_repairs=repairs,
        )
