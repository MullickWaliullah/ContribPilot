import base64
import hashlib
import logging
import os
import re
import time
from urllib.parse import quote

import httpx

logger = logging.getLogger(__name__)


GITHUB_API = "https://api.github.com"
TIMEOUT_SECONDS = 15
MAX_ATTEMPTS = 3
MAX_RATE_LIMIT_WAIT = 60

MAX_BODY_CHARS = 3000
MAX_FILE_CHARS = 100_000
MAX_CODE_FILES = 500
LARGE_REPO_KB = 50_000

TTL_REPO = 60 * 60
TTL_TREE = 30 * 60
TTL_FILE = 15 * 60
TTL_ISSUE = 5 * 60


class InvalidRepoError(ValueError):
    """"""


class NotFoundError(ValueError):
    """"""


class RateLimitError(RuntimeError):
    """"""


class AuthError(RuntimeError):
    """"""


class ForbiddenError(RuntimeError):
    """"""


class UpstreamError(RuntimeError):
    """"""


class UpstreamTimeoutError(RuntimeError):
    """"""


_cache: dict[str, tuple[float, object]] = {}


def _cache_get(key: str):
    entry = _cache.get(key)
    if entry is None:
        return None
    expires_at, value = entry
    if time.monotonic() > expires_at:
        _cache.pop(key, None)
        return None
    return value


def _cache_set(key: str, value, ttl: int) -> None:
    _cache[key] = (time.monotonic() + ttl, value)


def token_scope(token: str | None) -> str:
    if not token:
        return "public"
    return hashlib.sha256(token.encode("utf-8")).hexdigest()[:12]


_client: httpx.Client | None = None

_BASE_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "ContribPilot",
}


def _get_client() -> httpx.Client:
    global _client
    if _client is None:
        _client = httpx.Client(
            timeout=TIMEOUT_SECONDS,
            follow_redirects=True,
            headers=_BASE_HEADERS,
        )
    return _client


def _auth_headers(token: str | None) -> dict:
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def _request(method: str, url: str, params: dict | None = None, token: str | None = None):
    if not url.startswith(GITHUB_API + "/"):
        raise ValueError(f"Blocked non-GitHub URL : {url}")

    client = _get_client()
    headers = _auth_headers(token)

    last_exc: Exception | None = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        backoff = 2 ** (attempt - 1)

        try:
            resp = client.request(method, url, params=params, headers=headers)
        except httpx.TimeoutException as e:
            logger.warning("Timeout (attempt %d/%d): %s", attempt, MAX_ATTEMPTS, url)
            last_exc = UpstreamTimeoutError(f"GitHub timeout : {url}")
            last_exc.__cause__ = e
            if attempt < MAX_ATTEMPTS:
                time.sleep(backoff)
            continue

        except httpx.RequestError as e:
            logger.warning("Network error (attempt %d/%d): %s", attempt, MAX_ATTEMPTS, e)
            last_exc = UpstreamError(f"GitHub network error : {e}")
            last_exc.__cause__ = e
            if attempt < MAX_ATTEMPTS:
                time.sleep(backoff)
            continue

        status = resp.status_code

        if 200 <= status < 300:
            if status == 204 or not resp.content:
                return None
            return resp.json()

        if status == 404:
            raise NotFoundError(f"Resource not found : {url}")

        if status == 401:
            raise AuthError("GitHub token invalid")

        if status in (403, 429):
            remaining = resp.headers.get("X-RateLimit-Remaining")
            retry_after = resp.headers.get("Retry-After")
            is_rate_limit = status == 429 or remaining == "0" or retry_after is not None
            if not is_rate_limit:
                raise ForbiddenError(f"GitHub forbidden :{url}")

            if retry_after and retry_after.isdigit():
                wait = int(retry_after)
            else:
                reset = int(resp.headers.get("X-RateLimit-Reset", "0"))
                wait = max(reset - int(time.time()), 0) + 1

            if wait <= MAX_RATE_LIMIT_WAIT and attempt < MAX_ATTEMPTS:
                logger.warning("Rate limited, sleeping %ss", wait)
                time.sleep(wait)
                continue

            if token:
                raise RateLimitError("GitHub rate limit exceeded")
            raise RateLimitError(
                "GitHub rate limit exceeded. Add a GitHub token in Settings to raise the limit."
            )

        if status >= 500:
            logger.warning("GitHub %d (attempt %d/%d)", status, attempt, MAX_ATTEMPTS)
            last_exc = UpstreamError(f"GitHub server error {status}")
            if attempt < MAX_ATTEMPTS:
                time.sleep(backoff)
            continue

        raise UpstreamError(f"Unexpected GitHub response {status} : {url}")

    raise last_exc or UpstreamError("GitHub request failed")


_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


def _parse_repo(repo: str) -> tuple[str, str]:
    if not isinstance(repo, str) or not repo.strip():
        raise InvalidRepoError("Repo must be a non-empty string like 'owner/repo'")

    repo = repo.strip()

    for prefix in ("https://github.com/", "http://github.com/", "github.com/"):
        if repo.startswith(prefix):
            repo = repo[len(prefix):]
            break

    repo = repo.rstrip("/")
    if repo.endswith(".git"):
        repo = repo[:-4]

    parts = repo.split("/")
    if len(parts) != 2:
        raise InvalidRepoError(f"Invalid repo format : '{repo}'. Expected 'owner/repo'")

    owner, name = parts[0].strip(), parts[1].strip()
    if not owner or not name:
        raise InvalidRepoError("Owner and repo name cannot be empty")

    for part in (owner, name):
        if part in (".", "..") or not _NAME_RE.match(part):
            raise InvalidRepoError(f"Invalid characters in repo : '{part}'")

    return owner, name


def _normalize_issue(raw: dict, language: str = "unknown", body_limit: int | None = MAX_BODY_CHARS) -> dict:
    labels = []
    for lb in raw.get("labels") or []:
        name = lb.get("name") if isinstance(lb, dict) else lb
        if name:
            labels.append(str(name).lower())

    body = raw.get("body") or ""

    if body_limit is not None:
        body = body[:body_limit]

    number = raw.get("number")

    return {
        "id": number,
        "number": number,
        "title": raw.get("title", ""),
        "body": body,
        "description": body,
        "state": raw.get("state", "open"),
        "url": raw.get("html_url", ""),
        "labels": labels,
        "language": language or "unknown",
        "difficulty": "unknown",
        "comments_count": raw.get("comments", 0),
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
        "user": (raw.get("user") or {}).get("login"),
        "repository_url": raw.get("repository_url"),
    }


def search_issues_in_repo(
    repo: str,
    labels: list[str] | None = None,
    state: str = "open",
    limit: int = 30,
    token: str | None = None,
) -> list[dict]:
    owner, name = _parse_repo(repo)
    url = f"{GITHUB_API}/repos/{owner}/{name}/issues"

    if state not in ("open", "closed", "all"):
        state = "open"

    params = {
        "state": state,
        "per_page": min(max(int(limit), 1), 100),
        "sort": "created",
        "direction": "desc",
    }

    if labels:
        params["labels"] = ",".join(labels)

    data = _request("GET", url, params=params, token=token)
    if not isinstance(data, list) or not data:
        return []

    try:
        language = get_repository_info(repo, token=token).get("language") or "unknown"
    except (NotFoundError, RuntimeError):
        language = "unknown"

    return [
        _normalize_issue(item, language=language)
        for item in data
        if "pull_request" not in item
    ]


def get_issue(repo: str, issue_number: int, token: str | None = None) -> dict:
    owner, name = _parse_repo(repo)

    try:
        issue_number = int(issue_number)
    except (TypeError, ValueError):
        raise InvalidRepoError("issue_number must be an integer")

    scope = token_scope(token)
    cache_key = f"issue:{scope}:{owner}/{name}:{issue_number}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    url = f"{GITHUB_API}/repos/{owner}/{name}/issues/{issue_number}"
    raw = _request("GET", url, token=token)

    if "pull_request" in raw:
        raise ValueError("This is a PR, not an issue")

    try:
        language = get_repository_info(repo, token=token).get("language") or "unknown"
    except (NotFoundError, RuntimeError):
        language = "unknown"

    issue = _normalize_issue(raw, language=language, body_limit=None)

    _cache_set(cache_key, issue, TTL_ISSUE)

    return issue


def get_repository_info(repo: str, token: str | None = None) -> dict:
    owner, name = _parse_repo(repo)

    scope = token_scope(token)
    cache_key = f"repo:{scope}:{owner}/{name}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    raw = _request("GET", f"{GITHUB_API}/repos/{owner}/{name}", token=token)

    size = raw.get("size", 0)
    info = {
        "name": raw.get("name"),
        "full_name": raw.get("full_name"),
        "description": raw.get("description") or "",
        "language": raw.get("language") or "unknown",
        "default_branch": raw.get("default_branch") or "main",
        "size": size,
        "is_large": size > LARGE_REPO_KB,
        "stargazers_count": raw.get("stargazers_count", 0),
        "open_issues_count": raw.get("open_issues_count", 0),
        "topics": raw.get("topics") or [],
    }

    _cache_set(cache_key, info, TTL_REPO)

    return info


_CODE_EXTENSION = {".py", ".js", ".jsx", ".ts", ".tsx", ".toml", ".cfg", ".ini"}
_SPECIAL_FILES = {"requirements.txt", "package.json"}
_SKIP_DIRS = {
    "node_modules", ".git", "dist", "build", "venv", ".venv", "env",
    "__pycache__", ".pytest_cache", "coverage", "migrations", "vendor",
}


def _filter_code_files(paths: list[str]) -> list[str]:
    results = []
    for path in paths:
        parts = path.split("/")
        filename = parts[-1]

        if any(part in _SKIP_DIRS for part in parts[:-1]):
            continue

        ext = os.path.splitext(filename)[1].lower()

        if filename in _SPECIAL_FILES or ext in _CODE_EXTENSION:
            results.append(path)

        if len(results) >= MAX_CODE_FILES:
            break

    return results


def _resolve_branch(repo: str, branch: str | None, token: str | None = None) -> str:
    if branch:
        return branch

    try:
        return get_repository_info(repo, token=token).get("default_branch") or "main"
    except NotFoundError:
        return "main"


def get_repository_tree(repo: str, branch: str | None = None, token: str | None = None) -> dict:
    owner, name = _parse_repo(repo)
    branch = _resolve_branch(repo, branch, token=token)

    scope = token_scope(token)
    cache_key = f"tree:{scope}:{owner}/{name}:{branch}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    url = f"{GITHUB_API}/repos/{owner}/{name}/git/trees/{quote(branch, safe='')}"
    data = _request("GET", url, params={"recursive": "1"}, token=token)

    tree = data.get("tree") or []
    blob_paths = [item["path"] for item in tree if item.get("type") == "blob"]

    truncated = bool(data.get("truncated"))
    if truncated:
        logger.warning("Tree truncated for %s/%s - file list incomplete", owner, name)

    result = {
        "files": _filter_code_files(blob_paths),
        "truncated": truncated,
        "branch": branch,
    }

    _cache_set(cache_key, result, TTL_TREE)
    return result


def get_file_content(
    repo: str,
    path: str,
    branch: str | None = None,
    token: str | None = None,
) -> str:
    owner, name = _parse_repo(repo)

    if not path or path.startswith("/") or ".." in path.split("/"):
        raise InvalidRepoError(f"Invalid file path : '{path}'")

    branch = _resolve_branch(repo, branch, token=token)

    scope = token_scope(token)
    cache_key = f"file:{scope}:{owner}/{name}:{path}:{branch}"
    cached = _cache_get(cache_key)

    if cached is not None:
        return cached

    url = f"{GITHUB_API}/repos/{owner}/{name}/contents/{quote(path, safe='/')}"
    raw = _request("GET", url, params={"ref": branch}, token=token)

    if isinstance(raw, list):
        raise ValueError(f"'{path}' is a directory, not a file")

    if raw.get("encoding") != "base64" or not raw.get("content"):
        _cache_set(cache_key, "", TTL_FILE)
        return ""

    try:
        text = base64.b64decode(raw["content"]).decode("utf-8")
    except (UnicodeDecodeError, ValueError):
        text = ""

    text = text[:MAX_FILE_CHARS]
    _cache_set(cache_key, text, TTL_FILE)

    return text