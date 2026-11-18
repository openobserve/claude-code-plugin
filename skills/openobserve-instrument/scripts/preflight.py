#!/usr/bin/env python3
"""Check that OpenObserve accepts the trace credentials in a project's .env.

Sends an empty OTLP/HTTP trace batch (no spans, nothing is stored) to
<OPENOBSERVE_URL>/api/<org>/v1/traces with the .env token and stream. The .env
token can only send data, so this is the one check it can make; the first trace
and the AI data health checks show on the OpenObserve page the user copied the
prompt from.

Python 3 standard library only. The script prints variable names, never values.

Exit codes:
  0  OpenObserve accepted the credentials
  2  configuration problem: a variable is missing, the URL is unreachable or not an
     OpenObserve API, or the token or org was rejected
"""

import argparse
import http.client
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

REQUIRED_VARS = ("OPENOBSERVE_URL", "OPENOBSERVE_ORG", "OPENOBSERVE_AUTH_TOKEN")
STREAM_VARS = ("OPENOBSERVE_TRACES_STREAM_NAME", "OPENOBSERVE_STREAM")


def parse_env_file(path):
    """Parse KEY=VALUE lines (optional `export`, quotes and comments)."""
    values = {}
    with open(path, encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            if line.startswith("export "):
                line = line[len("export ") :].lstrip()
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                value = value[1:-1]
            elif " #" in value:
                value = value.split(" #", 1)[0].rstrip()
            values[key] = value
    return values


def load_config(env_file):
    file_values = {}
    if os.path.isfile(env_file):
        file_values = parse_env_file(env_file)
        found = [k for k in REQUIRED_VARS + STREAM_VARS + ("OPENOBSERVE_UI_URL",) if k in file_values]
        print(f"  .env found ({env_file}): {', '.join(found) if found else 'no OPENOBSERVE_* variables'}")
    else:
        print(f"  No .env at {env_file}; using the process environment")

    def get(name):
        return os.environ.get(name) or file_values.get(name) or ""

    missing = [name for name in REQUIRED_VARS if not get(name)]
    if missing:
        print(f"✗ Missing {', '.join(missing)}. Download the .env from the AI integration card.")
        sys.exit(2)
    return get


def auth_header(token):
    token = token.strip()
    if token.split(" ", 1)[0] in ("Basic", "Bearer"):
        return token
    return f"Basic {token}"


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Report a redirect instead of following it: urllib would resend the token to the new URL as a GET."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def send_empty_batch(base_url, org, stream, token):
    """POST an OTLP/JSON request with no spans; return (http_status, json_body, detail)."""
    url = f"{base_url}/api/{urllib.parse.quote(org, safe='')}/v1/traces"
    try:
        req = urllib.request.Request(url, data=json.dumps({"resourceSpans": []}).encode(), method="POST")
        req.add_header("Authorization", auth_header(token))
        req.add_header("Content-Type", "application/json")
        req.add_header("stream-name", stream)
        with _OPENER.open(req, timeout=30) as resp:
            status = resp.status
            body = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as err:
        return err.code, None, err.headers.get("Location")
    except urllib.error.URLError as err:
        return None, None, str(err.reason)
    except ValueError:
        # str(err) can quote a header value, which would print the token.
        return None, None, "the request could not be built; check OPENOBSERVE_URL and OPENOBSERVE_AUTH_TOKEN"
    except (OSError, http.client.HTTPException) as err:
        return None, None, str(err) or type(err).__name__
    try:
        return status, json.loads(body or "{}"), None
    except ValueError:
        # OpenObserve answers JSON; an HTML page means the URL points at something else.
        return status, None, None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--env-file", default=".env", help="path to the project .env (default: ./.env)")
    parser.add_argument("--stream", help="traces stream (default: OPENOBSERVE_TRACES_STREAM_NAME, OPENOBSERVE_STREAM, then 'default')")
    args = parser.parse_args()

    get = load_config(args.env_file)
    base_url = get("OPENOBSERVE_URL").rstrip("/")
    org = get("OPENOBSERVE_ORG")
    stream = args.stream or next((get(v) for v in STREAM_VARS if get(v)), "") or "default"
    print(f"  {base_url} · org {org} · stream {stream}")
    if not base_url.startswith(("http://", "https://")):
        print(f"✗ OPENOBSERVE_URL must start with http:// or https:// (got {base_url}).")
        return 2

    status, body, detail = send_empty_batch(base_url, org, stream, get("OPENOBSERVE_AUTH_TOKEN"))
    if status is not None and 200 <= status < 300 and body is not None:
        print("✓ OpenObserve accepts these credentials for traces.")
        return 0
    if status is None:
        print(f"✗ Cannot reach {base_url} ({detail}). Check OPENOBSERVE_URL and the network.")
    elif 300 <= status < 400:
        print(f"✗ {base_url} redirects (HTTP {status}) to {detail or 'another address'}. "
              "Set OPENOBSERVE_URL to the address it redirects to.")
    elif status in (401, 403):
        print(f"✗ OpenObserve rejected the token for org '{org}' (HTTP {status}). "
              "Check OPENOBSERVE_ORG, or download the .env again from the AI integration card.")
    elif status < 300 or status in (404, 405):
        print(f"✗ {base_url} is not an OpenObserve API (HTTP {status} without an OpenObserve answer). "
              "OPENOBSERVE_URL must be the API root, without /web or /api.")
    else:
        print(f"✗ OpenObserve answered HTTP {status} to an empty trace batch.")
    return 2


if __name__ == "__main__":
    sys.exit(main())
