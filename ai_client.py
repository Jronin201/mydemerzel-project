import os
import json
from typing import List, Dict, Any, Tuple, Optional
from openai import OpenAI

# Configuration via env
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")  # Primary GPT-5 family model
OPENAI_FALLBACK_MODEL = "gpt-4o"  # Only fallback allowed
OPENAI_REASONING_EFFORT = os.getenv("OPENAI_REASONING_EFFORT", "low")  # low|medium|high
OPENAI_MAX_OUTPUT_TOKENS = int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "512"))
OPENAI_TOOL_CHOICE = os.getenv("OPENAI_TOOL_CHOICE", "none")  # none unless tools configured
MIN_OUTPUT_TOKENS = 64

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
    models_to_try = [force_model] if force_model else AI_MODEL_FALLBACKS

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
            resp = _client.responses.create(**kwargs)
            output_text = getattr(resp, 'output_text', None)
            if (not output_text) and idx == 0:
                # Retry once with adjusted params (reasoning-only case)
                print("[AI] retry_reasoning_only openai.model={mdl} adjusting_effort=low")
                kwargs["reasoning"] = {"effort": "low"}
                kwargs["max_output_tokens"] = max(max_output_tokens, 512)
                resp = _client.responses.create(**kwargs)
                output_text = getattr(resp, 'output_text', None)
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
