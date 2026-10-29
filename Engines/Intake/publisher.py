from __future__ import annotations

from typing import Protocol

from .models import IntakeArtifact


class NexusPublisher(Protocol):
    """Port implemented by the Research Nexus integration adapter.

    Intake owns no durable scientific store. Publication through this port is
    the only supported durable handoff.
    """

    def publish_intake_artifact(self, artifact: IntakeArtifact) -> object:
        ...


class PublicationNotConfigured(RuntimeError):
    pass
