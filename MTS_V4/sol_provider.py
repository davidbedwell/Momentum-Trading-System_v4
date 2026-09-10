from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Mapping, Sequence

from .openai_compatible_provider import ResearchDirectorTransportError
from .research_package_provider import ResearchPackageAwareResearchDirector


class SolResearchPackageAwareResearchDirector(ResearchPackageAwareResearchDirector):
    """Research-package-aware Sol transport using supported Chat Completions parameters.

    The local/Qwen provider retains its existing transport unchanged. Sol currently
    rejects the non-default temperature used by that provider, so the appellate
    transport omits temperature and lets the model use its supported default.
    """

    def _chat_completion(self, messages: Sequence[Mapping[str, str]]) -> str:
        body = json.dumps(
            {
                "model": self._model,
                "messages": list(messages),
            },
            separators=(",", ":"),
        ).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        request = urllib.request.Request(
            f"{self._base_url}/v1/chat/completions",
            data=body,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                document = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            try:
                response_body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                response_body = ""
            detail = f"; response_body={response_body}" if response_body else ""
            raise ResearchDirectorTransportError(
                f"AI Research Director transport failed: HTTPError: {exc}{detail}"
            ) from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ResearchDirectorTransportError(
                f"AI Research Director transport failed: {type(exc).__name__}: {exc}"
            ) from exc

        try:
            message = document["choices"][0]["message"]
            content = message.get("content")
        except (KeyError, IndexError, TypeError, AttributeError) as exc:
            raise ResearchDirectorTransportError(
                "OpenAI-compatible response is missing choices[0].message"
            ) from exc
        if not isinstance(content, str) or not content.strip():
            reasoning_content = message.get("reasoning_content") if isinstance(message, Mapping) else None
            if isinstance(reasoning_content, str) and reasoning_content.strip():
                content = reasoning_content
            else:
                raise ResearchDirectorTransportError(
                    "AI Research Director returned no textual decision"
                )
        return content
