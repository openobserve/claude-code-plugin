---
name: openobserve-instrument
description: Instrument an LLM or AI-agent app to send OpenTelemetry traces to OpenObserve, run one sample request, and give the user a link to the OpenObserve AI Insights page for that request (the OpenObserve page the prompt came from confirms the first trace and runs the AI data health checks; run those checks yourself when the OpenObserve MCP server is connected). Use when the user asks to instrument, trace, or connect an AI app to OpenObserve, or to check that its AI telemetry is complete.
---

# Instrument an AI app for OpenObserve

You edit the user's project so every LLM call is traced to OpenObserve, prove it with one real
request, and point the user at what is still missing. Work in the project root. Print what you
change at each step; leave the diff for the user to review and commit.

The `.env` token can only **send** data: OpenObserve rejects it on every read API. The OpenObserve
page the user copied the prompt from watches for the first span and shows the data health checks
with the user's own login. Never try to read traces with the `.env` token; read them yourself only
through the OpenObserve MCP server (step 6).

Helper script: `scripts/preflight.py` next to this file (Python 3 standard library only). If you
fetched this file by URL, or your tool installed it as a single rules file without `scripts/`,
fetch the script from the `@openobserve/skills` npm package:
`https://cdn.jsdelivr.net/npm/@openobserve/skills@1/skills/openobserve-instrument/scripts/preflight.py`
and save it outside the project (for example `/tmp/openobserve-preflight.py`).

## Rules

- Never print, echo, log or paste a secret value. Mention variable **names** only. Do not `cat` the
  `.env`; read it with code that prints names, or let `preflight.py` read it.
- Never put the token in source code, the chat, or a command line you show. The app reads it from
  the environment (`load_dotenv()`).
- Do not commit. Do not change unrelated code.
- The org and stream named in the user's prompt win over values in `.env`.

## 1. Read the configuration

The user downloads a `.env` from the OpenObserve AI integration card into the project root. It holds:

| Variable | Required | Meaning |
|---|---|---|
| `OPENOBSERVE_URL` | yes | OpenObserve API base URL, e.g. `https://api.openobserve.ai` |
| `OPENOBSERVE_ORG` | yes | Organization identifier |
| `OPENOBSERVE_AUTH_TOKEN` | yes | `Basic <base64>` (or `Bearer <token>`) |
| `OPENOBSERVE_TRACES_STREAM_NAME` | no | Traces stream; `OPENOBSERVE_STREAM` is accepted too. Default `default` |
| `OPENOBSERVE_UI_URL` | no | Web UI root when it differs from `OPENOBSERVE_URL`, used for links only (links are `<root>/web/…`) |

Check which names exist, for example:

```bash
python3 -c "import re;print(', '.join(m.group(1) for l in open('.env') if (m:=re.match(r'\s*(?:export\s+)?(OPENOBSERVE_\w+)\s*=',l))))"
```

Print `✓ .env found: <names>`. If there is no `.env` but an `env.txt` or `env` holding these names,
the browser renamed the download: rename it to `.env`. If a required name is missing, stop and tell
the user to download the `.env` from the integration card (Data Sources → AI Integrations → *their
SDK* → *With a coding agent*). If the user named an org or a stream, set `OPENOBSERVE_ORG=<org>` or
`OPENOBSERVE_TRACES_STREAM_NAME=<stream>` in `.env` (the SDK reads these names). Make sure `.env`
is listed in `.gitignore`; add it if not.

Then check that OpenObserve accepts these credentials before you change any code:

```bash
python3 <skill dir>/scripts/preflight.py --env-file .env
```

It sends an empty trace batch (no spans, nothing is stored) to `<url>/api/<org>/v1/traces` with the
token and stream from `.env`, and prints one line. Exit `0`: credentials accepted. Exit `2`: it
names the problem (unreachable URL, a redirect, not an OpenObserve endpoint, token or org
rejected); stop and show the line to the user, since instrumenting cannot work until the `.env` is
fixed.

## 2. Read the project

Find and print one line, e.g. `Python 3.12 · openai 1.54 · entry point app/main.py · agent name "research-agent"`:

- **Language and runtime**: `pyproject.toml`, `requirements*.txt`, `setup.py`, `package.json`, `go.mod`, …
- **LLM SDK / framework** in use: imports and dependencies (`openai`, `anthropic`, `google-genai`,
  `langchain`, `crewai`, `google-adk`, `openai-agents`, `litellm`, `claude-agent-sdk`, OpenRouter
  via the `openai` client, …).
- **Entry point**: the module that starts the app (`__main__`, `main.py`, CLI script in
  `pyproject.toml`, server startup file).
- **Agent name**: the project or service name (`[project].name`, package name, directory name).
- **Version source**: `[project].version`, `__version__`, `package.json` `version`, or the git
  short SHA (`git rev-parse --short HEAD`) when nothing else exists.
- **Session id**: whatever identifies one conversation or request in the app (chat/thread/session
  id, request id). If the app has none, generate one per run with `uuid.uuid4()`.

## 3. Install

### Python, supported SDK — use the OpenObserve installer

Run the installer the integration card uses, pinned to a reviewed commit: download it to a temp
directory, check its SHA-256 against the one below, and run it from there only if they match;
never pipe a URL into a shell. A mismatch means the file is not the reviewed one: stop and tell
the user instead of running it or retrying another way. It installs the packages into the
interpreter it finds and verifies the imports. It takes the token only as a command-line argument,
which other local processes can read, so it never gets the real one: the project's `.env` already
holds the token. Give it a placeholder and point its env file into the temp directory, so it
cannot overwrite the project's `.env`. The URL is not a secret; read it from `.env` inside the
command. Do not `source` the `.env`: the token value `Basic <base64>` contains an unquoted space,
which a shell reads as a command.

```bash
env_get() { python3 -c 'import sys
for l in open(".env"):
    k, _, v = l.strip().removeprefix("export ").partition("=")
    if k.strip() == sys.argv[1]: print(v.strip().strip("\"'\''")); break' "$1"; }
O2_INSTALLER_RAW=https://raw.githubusercontent.com/openobserve/o2-datasource/9fdf2ca60b03a43273677a875140cfd19e29262b/ai
O2_INSTALLER_SHA256=307c0d275c8b91f270d557d41524d438f799934fe8502b513e3a22e6b2fcb0af
O2_INSTALLER_DIR="$(mktemp -d)"
mkdir "$O2_INSTALLER_DIR/frameworks"
curl -fsSL "$O2_INSTALLER_RAW/frameworks/setup.sh" -o "$O2_INSTALLER_DIR/frameworks/setup.sh"
if command -v sha256sum >/dev/null; then o2_sha256() { sha256sum "$@"; }
else o2_sha256() { shasum -a 256 "$@"; }; fi
if echo "$O2_INSTALLER_SHA256  $O2_INSTALLER_DIR/frameworks/setup.sh" | o2_sha256 -c -; then
  REPO_RAW="$O2_INSTALLER_RAW" bash "$O2_INSTALLER_DIR/frameworks/setup.sh" \
    --integration=<integration> \
    --url="$(env_get OPENOBSERVE_URL)" \
    --org=<org> \
    --token="Bearer placeholder" \
    --env-file="$O2_INSTALLER_DIR/.env" \
    --quiet
else
  echo "setup.sh does not match the reviewed SHA-256; not running it" >&2
fi
```

The SHA-256 is that of `ai/frameworks/setup.sh` at the pinned commit. Moving the pin to a newer
reviewed commit means updating both lines: `O2_INSTALLER_RAW`, and `O2_INSTALLER_SHA256` from
`gh api -H "Accept: application/vnd.github.raw"
"repos/openobserve/o2-datasource/contents/ai/frameworks/setup.sh?ref=<commit>" | shasum -a 256`.

`REPO_RAW` makes the installer fetch its helper library and integration list from the same
commit. `<integration>` is one of `openai`, `anthropic`, `gemini`, `langchain`, `crewai`,
`google-adk`, `claude-agent-sdk`, `openai-agents`, `openrouter`, `litellm`. If the project uses a
virtualenv, uv, poetry or pipenv, install into that environment instead and add the packages to
the project's dependency file. Packages and init lines per integration:

| Integration | Packages (plus `openobserve-telemetry-sdk python-dotenv`) | Instrumentor |
|---|---|---|
| openai | `opentelemetry-instrumentation-openai` | `from opentelemetry.instrumentation.openai import OpenAIInstrumentor` |
| anthropic | `opentelemetry-instrumentation-anthropic` | `from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor` |
| gemini | `opentelemetry-instrumentation-google-generativeai` | `from opentelemetry.instrumentation.google_generativeai import GoogleGenerativeAiInstrumentor` |
| langchain | `opentelemetry-instrumentation-langchain` | `from opentelemetry.instrumentation.langchain import LangchainInstrumentor` |
| crewai | `openinference-instrumentation-crewai` | `from openinference.instrumentation.crewai import CrewAIInstrumentor` (set `CREWAI_TELEMETRY_OPT_OUT=true`; call `openobserve_init()` first) |
| google-adk | `openinference-instrumentation-google-adk` | `from openinference.instrumentation.google_adk import GoogleADKInstrumentor` |
| openai-agents | `openinference-instrumentation-openai-agents` | `from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor` |
| openrouter | `openinference-instrumentation-openai` | `from openinference.instrumentation.openai import OpenAIInstrumentor` |
| litellm | `openinference-instrumentation-litellm` | `from openinference.instrumentation.litellm import LiteLLMInstrumentor` |
| claude-agent-sdk | — | wrap each `query()` in a span (see the snippet the installer saves, below) |

The installer's env file holds the placeholder token; never copy its `OPENOBSERVE_*` lines.
Merge only the integration's extra variables (for example `CREWAI_TELEMETRY_OPT_OUT`) into the
project's `.env`, keep the snippet it saved (`paste_me_<integration>.py`) if you need it, then
remove the temp directory:

```bash
python3 - "$O2_INSTALLER_DIR/.env" <<'PY'
import sys
def name(line):
    return line.strip().removeprefix("export ").partition("=")[0].strip()
text = open(".env").read()
have = {name(l) for l in text.splitlines() if "=" in l}
extra = [l.strip() for l in open(sys.argv[1])
         if "=" in l and not l.lstrip().startswith("#")
         and not name(l).startswith("OPENOBSERVE_") and name(l) not in have]
if extra:
    with open(".env", "a") as f:
        f.write(("" if not text or text.endswith("\n") else "\n") + "\n".join(extra) + "\n")
print("extra env:", ", ".join(name(x) for x in extra) or "none")
PY
cat "$O2_INSTALLER_DIR/paste_me_<integration>.py"
rm -rf "$O2_INSTALLER_DIR"
```

Print `✓ setup.sh@9fdf2ca --integration=<integration>` and the extra env names (no values).

### Anything else — plain OTLP/HTTP

For other languages or SDKs without an instrumentor, use the standard OpenTelemetry SDK with the
OTLP/HTTP exporter and an OpenInference or OpenTelemetry GenAI instrumentor where one exists:

- Endpoint: `<OPENOBSERVE_URL>/api/<org>/v1/traces` (protobuf or JSON over HTTP).
- Headers: `Authorization: <OPENOBSERVE_AUTH_TOKEN>` and `stream-name: <stream>`.
- Environment form, read by every OpenTelemetry SDK:
  `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=<url>/api/<org>/v1/traces`,
  `OTEL_EXPORTER_OTLP_TRACES_HEADERS=Authorization=Basic%20<base64>,stream-name=<stream>`
  (write these into `.env` from the existing values; do not print them).
- If no instrumentor exists, wrap each LLM call in a span named `chat <model>` with
  `gen_ai.operation.name=chat`, `gen_ai.provider.name`, `gen_ai.request.model`,
  `gen_ai.response.model`, `gen_ai.usage.input_tokens` and `gen_ai.usage.output_tokens`.
- Set `gen_ai.agent.name` on **every span**, and `gen_ai.conversation.id` on every span of one
  request (a span processor that stamps both in `on_start`, like `ConversationIdProcessor` in
  step 4). A resource attribute alone is not enough: the open-source edition stores it as
  `service_gen_ai_agent_name`, and the health checks read `gen_ai_agent_name`.

## 4. Edit the entry point

Put the init lines at the very top of the entry point, **before** any import of the LLM client
(instrumentors patch the client at import time). Python with the OpenAI SDK:

```python
import os
import uuid
from contextlib import contextmanager
from typing import Optional  # Python 3.9: no `str | None`

from dotenv import load_dotenv
load_dotenv()  # openobserve_init() reads OPENOBSERVE_* from the environment

from opentelemetry import baggage, context
from opentelemetry.sdk.trace import SpanProcessor
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
from openobserve import get_tracer_provider, openobserve_init

AGENT_NAME = "research-agent"          # from step 2
AGENT_VERSION = "1.4.0"                # from step 2 (read it at runtime when you can)


class ConversationIdProcessor(SpanProcessor):
    """Copy the request's conversation id onto every span started inside it."""

    def on_start(self, span, parent_context=None):
        conversation_id = baggage.get_baggage("gen_ai.conversation.id", parent_context)
        if conversation_id:
            span.set_attribute("gen_ai.conversation.id", str(conversation_id))


OpenAIInstrumentor().instrument()
openobserve_init(
    agent_name=AGENT_NAME,
    resource_attributes={
        "service.name": AGENT_NAME,
        "gen_ai.agent.name": AGENT_NAME,
        "gen_ai.agent.version": AGENT_VERSION,
    },
)
get_tracer_provider().add_span_processor(ConversationIdProcessor())


@contextmanager
def conversation(conversation_id: Optional[str] = None):
    """Wrap one request / chat turn: `with conversation(session_id): ...`."""
    token = context.attach(
        baggage.set_baggage("gen_ai.conversation.id", conversation_id or str(uuid.uuid4()))
    )
    try:
        yield
    finally:
        context.detach(token)


from openai import OpenAI  # client imports come after the init lines
```

Then wrap the code that handles one request or conversation turn in `with conversation(<the app's
session id>):`. These three attributes are what two of the data health checks look for:
`gen_ai.agent.name` (missing agent identity), `gen_ai.agent.version`, and
`gen_ai.conversation.id` (spans without session id). Short-lived scripts must exit normally (the
SDK flushes at exit) or call `openobserve_flush()` before exiting.

Print each edit, e.g.:

```
✓ OpenAIInstrumentor().instrument() and openobserve_init() above "from openai import"
✓ gen_ai.agent.name = research-agent, version from pyproject.toml
✓ gen_ai.conversation.id = the request's session id
```

## 5. Run one sample request

Record the start time, then run the smallest real request the app supports (a CLI flag, a test
script, or one HTTP call to the running server). Use the app's own credentials (`OPENAI_API_KEY`
etc.); never ask for them in chat.

```bash
START=$(date +%s)
python -m app.main --once "Summarize the EU AI Act disclosure rules"
```

If the app cannot make a real call (no API key), tell the user and stop; do not fake spans.
`load_dotenv()` never overrides a variable that is already set, even to an empty string; if the
app reports a missing key that `.env` has, `unset` the empty variable in the shell first.

Read the app's output: the OpenTelemetry exporter logs `Failed to export` (with the HTTP status)
when OpenObserve refuses a batch. If you see it, rerun the preflight and fix that first. Short-lived
scripts must exit normally or call `openobserve_flush()`, or the batch is never sent.

## 6. Confirm the data

The OpenObserve page the user copied the prompt from shows the result by itself: it turns green
when the first span lands in `<stream>`, then lists the AI data health checks. You give the user a
link to the AI Insights page, which shows the cost, tokens, latency and data health of the stream.

### Always: the Insights link

Print this link (`<ui root>` is `OPENOBSERVE_UI_URL`, else `OPENOBSERVE_URL`; times are
microseconds, from one minute before `START` to now):

```bash
FROM_US=$(( (START - 60) * 1000000 )); TO_US=$(( $(date +%s) * 1000000 ))
```

`<ui root>/web/ai/llm-insights?type=stream&stream=<stream>&from=<FROM_US>&to=<TO_US>&org_identifier=<org>`

Always include `from` and `to`: without them the page opens on the time range the user last
picked and can miss the request. Tell the user that the OpenObserve tab they copied the prompt
from also turns green and lists the data health checks.

### If the OpenObserve MCP server is connected: check it yourself too

Use this only when your tools include the OpenObserve MCP server (tools named `SearchSQL`,
`tool_search` and `tools_call`). It signs in with the user's own credentials, so reads work: on
Enterprise and Cloud through OAuth as the user, on the open-source edition with a service-account
token that can read and change everything in the org. Never point it, or any request, at the
`.env` token. Times are microseconds; start one minute before `START` to cover clock skew.

1. **First GenAI span.** Call `SearchSQL` with `type: "traces"` and
   `SELECT trace_id, count(*) AS spans FROM "<stream>" WHERE gen_ai_operation_name IS NOT NULL AND service_name = '<agent name>' GROUP BY trace_id ORDER BY min(_timestamp) ASC LIMIT 1`.
   Spans can take a few seconds to become searchable: retry every 5 s for up to 2 minutes. No row,
   or an error that `gen_ai_operation_name` is not a field of the stream, means the LLM client is
   not instrumented (HTTP or database spans alone do not count): confirm the instrumentor is
   installed, the init lines run before the client import, the process exits cleanly, and the
   stream name matches. Print the trace link, always with `from` and `to` (one minute before
   `START` to now, in µs); without them the page searches its default time range and can miss the
   trace:
   `<ui root>/web/traces/trace-details?stream=<stream>&trace_id=<trace_id>&from=<start µs>&to=<end µs>&org_identifier=<org>`.
2. **Data health.** Call `tools_call` with `tool: "GetGenAiDataHealth"` and `args` holding
   `stream_name`, `start_time`, `end_time`, `agent: "<agent name>"`, `refresh: true` and
   `include_samples: true`; the org is the one in the MCP server URL (find the tool with
   `tool_search` "data health" if the name differs). Print each check as
   `✓`/`✗ <check>  <affected> of <total> spans`. If the server has no such tool, it predates the
   checks: say so and rely on the OpenObserve page.

### What each check means and where to fix it

| Check | Fix |
|---|---|
| Missing agent identity | Set `gen_ai.agent.name` on every span (step 4). Enterprise and Cloud can also map an existing attribute in Settings → GenAI Agent Mapping |
| Spans without session id | Wrap each request in `conversation(...)` (step 4) |
| Zero-duration spans | Spans ended before the work did — usually a span closed before a streamed response was consumed. See the AI integration docs |
| Unpriced models | Enterprise and Cloud: add the model's price in Settings → LLM Model Pricing (`<ui root>/web/settings/model_pricing/gaps?stream=<stream>&org_identifier=<org>`). The open-source edition has no pricing page: tell the user that the cost of this model reads $0 |

When the user reports a failing check from the page, fix the code for it, run one more request,
and ask them to press *Check again* on the page (or rerun the MCP checks).

## 7. Report

End with: the files you changed, the preflight result, that the sample request ran, the first
trace link and health summary if you checked through MCP, the Insights link, and the fixes left
for the user. Then ask the user to share any failing check from the OpenObserve page.
