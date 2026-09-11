from __future__ import annotations

import json
import sys
import time
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

    _TRANSIENT_HTTP_CODES = frozenset({408, 429, 500, 502, 503, 504})
    _MAX_TRANSIENT_RETRIES = 6
    _TRANSIENT_RETRY_DELAYS_SECONDS = (2.0, 4.0, 8.0, 16.0, 32.0, 60.0)

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

        document = None
        for attempt in range(self._MAX_TRANSIENT_RETRIES + 1):
            try:
                with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                    document = json.loads(response.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as exc:
                try:
                    response_body = exc.read().decode("utf-8", errors="replace")
                except Exception:
                    response_body = ""
                detail = f"; response_body={response_body}" if response_body else ""
                retryable = exc.code in self._TRANSIENT_HTTP_CODES
                if retryable and attempt < self._MAX_TRANSIENT_RETRIES:
                    delay = self._TRANSIENT_RETRY_DELAYS_SECONDS[attempt]
                    print(
                        f"Sol transport transient HTTP {exc.code}; retry "
                        f"{attempt + 1}/{self._MAX_TRANSIENT_RETRIES} in {delay:g}s",
                        file=sys.stderr,
                        flush=True,
                    )
                    time.sleep(delay)
                    continue
                raise ResearchDirectorTransportError(
                    f"AI Research Director transport failed: HTTPError: {exc}{detail}"
                ) from exc
            except (urllib.error.URLError, TimeoutError) as exc:
                if attempt < self._MAX_TRANSIENT_RETRIES:
                    delay = self._TRANSIENT_RETRY_DELAYS_SECONDS[attempt]
                    print(
                        f"Sol transport transient {type(exc).__name__}; retry "
                        f"{attempt + 1}/{self._MAX_TRANSIENT_RETRIES} in {delay:g}s",
                        file=sys.stderr,
                        flush=True,
                    )
                    time.sleep(delay)
                    continue
                raise ResearchDirectorTransportError(
                    f"AI Research Director transport failed: {type(exc).__name__}: {exc}"
                ) from exc
            except json.JSONDecodeError as exc:
                raise ResearchDirectorTransportError(
                    f"AI Research Director transport failed: {type(exc).__name__}: {exc}"
                ) from exc

        if document is None:
            raise ResearchDirectorTransportError(
                "AI Research Director transport failed without a response document"
            )

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
