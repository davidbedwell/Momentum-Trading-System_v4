# Trader Interface Architecture Addition Audit

## Scope

This audit records the addition of future trader-facing graphical-interface
readiness to canonical MTS architecture.

## System Architecture

Added a trader-facing graphical-interface requirement under Human Control and
Automation.

The architecture now requires support for simultaneous visualization of the six
highest-ranked active Decision candidates, including historical and
live-forming candlesticks, prospective action levels/zones, current Decision
state, and the material evidence, constraints, uncertainty, and conditions
influencing each Decision.

The interface remains a presentation and authorized control surface. It does
not own scientific or Decision logic.

## Decision Architecture

Added explicit Decision-output projection requirements so future interface work
does not need to reverse-engineer or duplicate Decision logic.

Decision/current-state contracts must expose sufficient structured information
for the graphical interface to render candidate rank, Decision state,
prospective action levels, risk/horizon information, material reasons, and
state-change conditions.

## Deferred Design

This architecture change intentionally does not select:

- frontend framework;
- charting library;
- visual layout beyond the six-candidate simultaneous capability;
- candle interval;
- colors or styling;
- exact schema field names;
- transport protocol.

Those choices remain subordinate implementation/specification concerns.
