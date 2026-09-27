from pathlib import Path
import re

MAX_PATCH_SIZE = 200 * 1024

FORBIDDEN =["..","/etc/","/root",".ssh",".aws",".env","id_rsa","authorized_keys"]

ALLOWED_REPO_PREFIXES =(
    "https://github.com/",
    "git@github.com:",
)

SHELL_METACHARACTERS = re.compile(r"[;&|`$(){}<>\\\n\r]")

class SandboxSecurityError(Exception):
    pass



def validate_patch_content(patch_text : str, sandbox_repo_path:Path) -> list[str]:

    if not patch_text:
        raise SandboxSecurityError("Empty Patch")

    if len(patch_text.encode("utf-8")) >MAX_PATCH_SIZE:
        raise SandboxSecurityError("Patch too large")

    target : set[str] =set()

    Pattern = re.compile(r"^(?:---|\+\+\+)\s+([ab]/(.+?))(?:\t|$)", re.MULTILINE)

    row_paths=[m.group(2) for m in Pattern.finditer(patch_text)]

    for row in row_paths:
        low = row.lower().replace("\\","/")

        if any(marker in low for marker in FORBIDDEN):
            raise SandboxSecurityError(f"Forbidden path : {row}")

        if Path(row).is_absolute():
            raise SandboxSecurityError(f"Absolute path: {row}")

        target.add(row)

    if not target:
        raise SandboxSecurityError("No file targets in patch")

    resolved_sandbox = sandbox_repo_path.resolve()

    for t in target:
        candidate = (resolved_sandbox/t).resolve()
        if candidate.is_relative_to(resolved_sandbox):
            raise SandboxSecurityError("Path escapes repo")

    return sorted(target)


def get_sandbox_env()->dict[str,str]:
    return {
        "PYTHONDONTWRITEBYTECODE" : "1",
        "PYTHONUNBUFFERED" : "1",
        "PYTHONIOENCODING" : "utf-8",
        "PIP_DISABLE_PIP_VERSION_CHECK" : "1",
        "PIP_NO_INPUT" : "1", 
    }


def validate_repo_url(repo_url : str | None) -> str:
    if not repo_url:
        raise SandboxSecurityError("Empty repo url")

    if not repo_url.startswith(ALLOWED_REPO_PREFIXES):
        raise SandboxSecurityError(f"Only github repos allowed : {repo_url}")

    if ".." in repo_url:
        raise SandboxSecurityError(f"Suspicious url : {repo_url}")

    if SHELL_METACHARACTERS.search(repo_url):
        raise SandboxSecurityError(f"Suspicious url : {repo_url}")

    return repo_url