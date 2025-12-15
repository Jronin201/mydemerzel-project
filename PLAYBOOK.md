# Production AI Resilience & Streaming Playbook

## Environment Variables

| Category      | Variable                 | Default | Notes                                   |
| ------------- | ------------------------ | ------- | --------------------------------------- |
| Core          | OPENAI_MODEL             | gpt-5.2 | Primary model (Responses API)           |
| Core          | OPENAI_REASONING_EFFORT  | medium  | low, medium, high (default medium)      |
| Core          | OPENAI_MAX_OUTPUT_TOKENS | 20000   | Min 64; no artificial upper clamp       |
| Core          | MODEL_CONTEXT_WINDOW     | 128000  | Approx context window for preflight     |
| Core          | OPENAI_TOOL_CHOICE       | none    | none or auto                            |
| Streaming     | OPENAI_STREAM_RESPONSES  | false   | Enable SSE (requires Accept header)     |
| Resilience    | AI_BACKOFF_ENABLED       | true    | One full-jitter retry (429/5xx primary) |
| Resilience    | AI_BACKOFF_BASE_MS       | 250     | Base backoff (ms)                       |
| Resilience    | AI_BACKOFF_CAP_MS        | 2000    | Max backoff cap (ms)                    |
| Observability | OBS_VERBOSE              | false   | Extra debug logging                     |

## API Behavior (Responses-only)

Primary path: Responses API + GPT-5.2 using typed parts (input_text / output_text) and text.format.

Fallback: single fallback to gpt-4o only on hard errors (401/403/404/409/429/5xx, model_not_found).

Retry: for 429 and 5xx on primary only, perform one full-jitter backoff retry before fallback.

Circuit breaker: opens after ≥3 hard primary failures within 60s, stays open 120s; after that, one half-open probe decides close/reopen.

Streaming: SSE emits only token (text deltas), ping (heartbeat ~15s), and one enriched done event. Near-cap / truncation annotations may appear in the final done meta.

## Health Check

```bash
bash -lc 'curl -s http://<HOST>/health/ai | jq'
```

Returns 200 only if a GPT-5.2 Responses call yields output_text:"OK" (no fallback needed).

## Streaming (SSE) Client Example

```javascript
const es = new EventSource("/chat/stream");
es.addEventListener("token", (e) => {
  // Append e.data to your UI
});
es.addEventListener("ping", () => {
  /* ignore */
});
es.addEventListener("done", (e) => {
  const meta = JSON.parse(e.data);
  es.close();
  // meta = { model, resp_id, usage:{input_tokens,output_tokens}, fallback, latency_ms, breaker_state, backoff_ms, near_cap?, truncated? }
});
es.onerror = () => {
  es.close(); /* optional reconnect with backoff */
};
```

## Resilience Semantics

Retry (primary): On 429/5xx → sleep once using full jitter:

```
sleep = random(0, min(cap, base * 2^1))
```

Fallback: If retry fails hard, swap to gpt-4o exactly once.

Circuit breaker:

- Open: ≥3 hard failures in 60s → skip primary for 120s.
- Half-open: after 120s, allow one probe; success → close, failure → reopen 120s.

Abort handling (SSE): client disconnect stops upstream immediately; logs stream.aborted=true; no done event emitted.

## Logging (Structured)

Every request emits one completion log line with at least:

```text
req.id=<uuid> openai.model=<id> openai.resp_id=resp_... \
openai.usage.input_tokens=<n> openai.usage.output_tokens=<m> \
openai.latency_ms=<ms> openai.fallback=<true|false> \
breaker.state=<open|half_open|closed> backoff.ms=<ms or 0>
```

Use req.id to correlate with OpenAI platform logs.

Near-cap warning: when output_tokens / OPENAI_MAX_OUTPUT_TOKENS ≥ 0.95 you will see `WARN:output_near_cap` plus `near_cap=true` in streaming done meta.

Truncation warning: if upstream signals incomplete output or output_tokens equals the configured cap, logs include `WARN:truncated` and streaming done meta includes `truncated:true`.

High-effort override: request JSON may include `"high_effort": true` to force `reasoning.effort=high` for that call only. Use sparingly (higher latency & cost).

Context preflight (non-stream & stream): Before dispatch, an approximate token estimate (chars / 3.5) sums all message contents. If `estimated_input + max_output_tokens > MODEL_CONTEXT_WINDOW`, the system reduces `max_output_tokens` to fit; if impossible (input alone exceeds window), it rejects with a polite context-too-large error.

## Operational Playbook

Enable streaming: set OPENAI_STREAM_RESPONSES=true, redeploy, verify SSE token and single enriched done.
Monitor near-cap/truncated: investigate if you see frequent near_cap or truncated flags—either raise OPENAI_MAX_OUTPUT_TOKENS, trim historical context, or split user prompts.

Verify fallback: temporarily force 429/5xx in staging; observe one retry (logged backoff.ms) then fallback.

Breaker drill: trigger 3 hard failures in <60s; confirm breaker.state=open and immediate fallback; after 120s, half-open probe decides.

Tuning:

- Larger outputs → increase OPENAI_MAX_OUTPUT_TOKENS (never <64). If regularly near-cap, consider raising or summarizing history sooner.
- More/less “thinking” → adjust OPENAI_REASONING_EFFORT (default medium). For one-off deep reasoning use `high_effort` request flag.
- Tools off by default via OPENAI_TOOL_CHOICE=none.
- Adjust MODEL_CONTEXT_WINDOW if upstream models expand.

Timeouts: Client timeout set to 180s; for very large 20k-token generations consider server/proxy idle timeouts ≥300s. Heartbeat pings every ~15s keep connections warm.

## Render Deployment Checklist

```bash
OPENAI_MODEL=gpt-5.2
OPENAI_REASONING_EFFORT=medium
OPENAI_MAX_OUTPUT_TOKENS=20000
MODEL_CONTEXT_WINDOW=128000
OPENAI_TOOL_CHOICE=none
OPENAI_STREAM_RESPONSES=true   # if you want streaming live
AI_BACKOFF_ENABLED=true
AI_BACKOFF_BASE_MS=250
AI_BACKOFF_CAP_MS=2000
OBS_VERBOSE=false
```

Save env; restart service.

- GET /health/ai → 200.
- Non-stream /chat → returns text; logs show latency + breaker state + optional WARN near-cap.
- Stream /chat → see token deltas and a single enriched done (with near_cap/truncated flags when applicable).
- Staging: simulate 429/5xx; confirm one backoff retry then fallback, and breaker behavior after 3 failures.

Migration Notes:

- Removed legacy Chat Completions paths and shims.
- Unified on Responses API + GPT-5.2.
- Single enriched done event; no duplicate finals.
- Deterministic text via typed input_text + text.format.
