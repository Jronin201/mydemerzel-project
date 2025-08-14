import os
import json
import time
import random
from collections import deque
from typing import List, Dict, Any, Tuple, Optional, Iterator, Deque
from openai import OpenAI

# Configuration via env
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")  # Primary GPT-5 family model
OPENAI_FALLBACK_MODEL = "gpt-4o"  # Only fallback allowed
OPENAI_REASONING_EFFORT = os.getenv("OPENAI_REASONING_EFFORT", "low")  # low|medium|high
OPENAI_MAX_OUTPUT_TOKENS = int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "512"))
OPENAI_TOOL_CHOICE = os.getenv("OPENAI_TOOL_CHOICE", "none")  # none unless tools configured
MIN_OUTPUT_TOKENS = 64
OPENAI_STREAM_RESPONSES = os.getenv("OPENAI_STREAM_RESPONSES", "false").lower() in ("1","true","yes","on")
AI_BACKOFF_ENABLED = os.getenv("AI_BACKOFF_ENABLED", "true").lower() in ("1","true","yes","on")

# Circuit breaker settings
_circuit_failures: Deque[float] = deque(maxlen=20)  # timestamps of recent primary hard failures
_circuit_open_until: float = 0.0  # epoch seconds until which primary is skipped
_CIRCUIT_FAIL_WINDOW = 60.0  # seconds window to count failures
_CIRCUIT_OPEN_DURATION = 120.0  # time breaker remains open

try:
    _api_key = os.getenv("OPENAI_API_KEY")
    if not _api_key:
        raise RuntimeError("OPENAI_API_KEY missing (AI client offline)")
    _client = OpenAI(api_key=_api_key, timeout=60.0, max_retries=1)
    print(f"[AI] OpenAI Responses client initialized (primary={OPENAI_MODEL})")
except Exception as _e:  # pragma: no cover
    print(f"[AI] Client unavailable: {_e}")
    _client = None

AI_MODEL_FALLBACKS = [OPENAI_MODEL, OPENAI_FALLBACK_MODEL]

def _now() -> float:
    return time.time()

def _circuit_is_open(now: Optional[float] = None) -> bool:
    global _circuit_open_until
    now = now or _now()
    if _circuit_open_until and now < _circuit_open_until:
        return True
    if _circuit_open_until and now >= _circuit_open_until:
        # auto close
        print(f"[AI] circuit_close open_until_expired={_circuit_open_until}")
        _circuit_open_until = 0.0
    return False

def _record_primary_failure(now: Optional[float] = None):
    global _circuit_open_until
    now = now or _now()
    _circuit_failures.append(now)
    # prune old
    while _circuit_failures and (now - _circuit_failures[0]) > _CIRCUIT_FAIL_WINDOW:
        _circuit_failures.popleft()
    if len(_circuit_failures) >= 3:
        if not _circuit_open_until:  # open once
            _circuit_open_until = now + _CIRCUIT_OPEN_DURATION
            print(f"[AI] circuit_open failures={len(_circuit_failures)} open_until={_circuit_open_until}")

def circuit_state() -> Dict[str, Any]:
    return {
        "open": _circuit_is_open(),
        "open_until": _circuit_open_until,
        "recent_failures": list(_circuit_failures),
    }

def _build_responses_input(messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Convert legacy messages [{'role':..., 'content':...}] to Responses 'input' parts."""
    converted = []
    for m in messages:
        role = m.get('role', 'user')
        text = m.get('content', '')
        converted.append({
            "role": role,
            "content": [{"type": "input_text", "text": text}]
        })
    return converted

def _is_retryable_hard_error(exc: Exception) -> bool:
    s = str(exc).lower()
    status = getattr(exc, 'status_code', None) or getattr(exc, 'http_status', None)
    if status and (status in (401,403,404,409,429) or status >= 500):
        return True
    return any(tok in s for tok in ["model_not_found", "does not exist", "unknown model"])

def is_hard_error(exc: Exception) -> bool:
    """Public helper so app route can classify fallback-worthy streaming errors."""
    return _is_retryable_hard_error(exc)

def request(messages: List[Dict[str,str]],
            reasoning_effort: Optional[str]=None,
            max_output_tokens: Optional[int]=None,
            tool_choice: Optional[str]=None,
            force_model: Optional[str]=None) -> Dict[str, Any]:
    """Perform a GPT-5 Responses API call with structured input and fallback.
    Returns dict with keys: output_text, model, used_fallback(bool), id, usage(dict), raw(response or error).
    Will fallback to gpt-4o only on qualified hard errors.
    """
    reasoning_effort = reasoning_effort or OPENAI_REASONING_EFFORT
    max_output_tokens = max_output_tokens or OPENAI_MAX_OUTPUT_TOKENS
    if max_output_tokens < MIN_OUTPUT_TOKENS:
        max_output_tokens = MIN_OUTPUT_TOKENS
    tool_choice = tool_choice or OPENAI_TOOL_CHOICE
    # Decide model list considering circuit breaker
    if force_model:
        models_to_try = [force_model]
    else:
        if _circuit_is_open():
            print(f"[AI] circuit_skip primary={OPENAI_MODEL} open_until={_circuit_open_until}")
            models_to_try = [OPENAI_FALLBACK_MODEL]
        else:
            models_to_try = AI_MODEL_FALLBACKS

    last_error = None
    offline = _client is None
    for idx, mdl in enumerate(models_to_try):
        if offline:
            break
        try:
            inp = _build_responses_input(messages)
            kwargs = {
                "model": mdl,
                "input": inp,
                "max_output_tokens": max_output_tokens,
                "reasoning": {"effort": reasoning_effort},
                "tool_choice": tool_choice,
            }
            # Expose raw kwargs for test inspection (non-production side effect)
            globals()["_last_ai_kwargs"] = kwargs
            # DO NOT send temperature for GPT-5 (per requirements)
            print(
                "[AI] start "
                f"openai.model={mdl} openai.effort={reasoning_effort} "
                f"openai.max_output_tokens={max_output_tokens} openai.tool_choice={tool_choice} "
                f"openai.fallback={idx>0}"
            )
            primary_retry = False
            while True:
                resp = _client.responses.create(**kwargs)
                output_text = getattr(resp, 'output_text', None)
                # Reasoning-only retry (existing behavior) only once on primary
                if (not output_text) and idx == 0 and not primary_retry:
                    print("[AI] retry_reasoning_only openai.model={mdl} adjusting_effort=low")
                    kwargs["reasoning"] = {"effort": "low"}
                    kwargs["max_output_tokens"] = max(max_output_tokens, 512)
                    resp = _client.responses.create(**kwargs)
                    output_text = getattr(resp, 'output_text', None)
                break
            output_text = getattr(resp, 'output_text', None)
            if (not output_text) and idx == 0:
                # Retry once with adjusted params (reasoning-only case)
                # (Handled above) - kept for clarity
                pass
            if not output_text:
                # Treat as soft failure; do not fallback unless hard error
                return {
                    "output_text": "",
                    "model": getattr(resp, 'model', mdl),
                    "used_fallback": idx>0,
                    "id": getattr(resp, 'id', None),
                    "usage": getattr(resp, 'usage', {}).__dict__ if hasattr(resp, 'usage') else {},
                    "raw": resp,
                    "error": "missing_output_text"
                }
            usage = {}
            if hasattr(resp, 'usage'):
                u = resp.usage
                usage = {
                    "input_tokens": getattr(u, 'input_tokens', None),
                    "output_tokens": getattr(u, 'output_tokens', None),
                    "total_tokens": getattr(u, 'total_tokens', None),
                }
            print(
                "[AI] success "
                f"openai.resp_id={getattr(resp,'id',None)} "
                f"openai.model={getattr(resp,'model',mdl)} "
                f"openai.usage.input_tokens={usage.get('input_tokens')} "
                f"openai.usage.output_tokens={usage.get('output_tokens')} "
                f"openai.fallback={idx>0}"
            )
            return {
                "output_text": output_text,
                "model": getattr(resp, 'model', mdl),
                "used_fallback": idx>0,
                "id": getattr(resp,'id',None),
                "usage": usage,
                "raw": resp,
            }
        except Exception as e:  # capture error
            last_error = e
            print(
                "[AI] error "
                f"openai.model={mdl} openai.fallback={idx>0} error={str(e)}"
            )
            if not _is_retryable_hard_error(e):
                # Non-hard error: do not fallback further
                break
            else:
                if idx == 0 and mdl == OPENAI_MODEL:
                    _record_primary_failure()
                print(
                    "[AI] fallback_trigger "
                    f"openai.model={mdl} openai.next_model={(models_to_try[idx+1] if idx+1 < len(models_to_try) else None)}"
                )
                continue
    # Offline or failed
    return {
        "output_text": "",
        "model": force_model or OPENAI_MODEL,
        "used_fallback": False,
        "id": None,
        "usage": {},
        "error": str(last_error) if last_error else ("offline" if offline else "unknown_error")
    }

# Lightweight health check helper
def health_check() -> Tuple[bool, Dict[str, Any]]:
    if _client is None:
        return False, {"error": "client_offline"}
    probe_messages = [
        {"role": "system", "content": "Health check."},
        {"role": "user", "content": "Respond with the single word: ok"},
    ]
    res = request(probe_messages, reasoning_effort="low", max_output_tokens=64, force_model=OPENAI_MODEL)
    healthy = res.get("output_text", "").strip().lower() == "ok"
    return healthy, res


def request_stream(messages: List[Dict[str,str]],
                   force_model: Optional[str]=None,
                   reasoning_effort: Optional[str]=None,
                   max_output_tokens: Optional[int]=None,
                   tool_choice: Optional[str]=None) -> Iterator[Tuple[str, Any]]:
    """Stream text deltas using Responses API.
    Yields tuples:
      ("delta", text_fragment) for each output_text delta
      ("done", {meta}) once completed with keys model, id, usage, used_fallback(False initial)
    NOTE: Fallback / retry semantics handled by caller (/chat route) which may invoke this twice.
    """
    reasoning_effort = reasoning_effort or OPENAI_REASONING_EFFORT
    max_output_tokens = max(max_output_tokens or OPENAI_MAX_OUTPUT_TOKENS, MIN_OUTPUT_TOKENS)
    tool_choice = tool_choice or OPENAI_TOOL_CHOICE
    if force_model:
        mdl = force_model
    else:
        if _circuit_is_open():
            mdl = OPENAI_FALLBACK_MODEL
        else:
            mdl = OPENAI_MODEL
    offline = _client is None
    if offline:
        raise RuntimeError("client_offline")
    inp = _build_responses_input(messages)
    kwargs = {
        "model": mdl,
        "input": inp,
        "max_output_tokens": max_output_tokens,
        "reasoning": {"effort": reasoning_effort},
        "tool_choice": tool_choice,
        "stream": True,
        "text_format": {"type": "text"},  # enforce plain text channel
    }
    globals()["_last_ai_kwargs"] = kwargs
    print("[AI] stream_start openai.model={mdl} openai.effort={effort} openai.max_output_tokens={tok}".format(
        mdl=mdl, effort=reasoning_effort, tok=max_output_tokens
    ))
    try:
        stream = _client.responses.stream(**kwargs)
    except Exception as e:  # network/setup error before iteration
        print(f"[AI] stream_error openai.model={mdl} error={e}")
        raise
    final_meta: Dict[str, Any] = {}
    try:
        for event in stream:
            etype = getattr(event, 'type', None) or getattr(event, 'event', None)
            # Text delta
            if etype and 'response.output_text.delta' in etype:
                # event might expose delta or text attribute
                delta = getattr(event, 'delta', None) or getattr(event, 'text', None)
                if delta:
                    yield ("delta", delta)
            elif etype and 'response.completed' in etype:
                model = getattr(event, 'model', mdl)
                usage_obj = getattr(event, 'usage', None)
                usage = {}
                if usage_obj is not None:
                    usage = {
                        "input_tokens": getattr(usage_obj, 'input_tokens', None),
                        "output_tokens": getattr(usage_obj, 'output_tokens', None),
                        "total_tokens": getattr(usage_obj, 'total_tokens', None),
                    }
                final_meta = {
                    "model": model,
                    "id": getattr(event, 'id', None),
                    "usage": usage,
                    "used_fallback": False,
                }
            elif etype and 'response.error' in etype:
                # propagate as exception
                err = getattr(event, 'error', None)
                raise RuntimeError(f"stream_error: {err}")
            else:
                # Ignore reasoning or other event types silently
                continue
    finally:
        # attempt to close underlying stream (SDK dependent)
        try:
            if hasattr(stream, 'close'):
                stream.close()
        except Exception:
            pass
    # Yield final meta as done
