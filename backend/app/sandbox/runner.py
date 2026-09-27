import time
from e2b import Sandbox

from app.core.config import settings
from app.sandbox.security import (
    get_sandbox_env,
    SandboxSecurityError,
    validate_repo_url,
)



SESSION_IDLE_TIMEOUT = 600      
SESSION_MAX_AGE = 3600          
CLONE_TIMEOUT = 60             
PIP_INSTALL_TIMEOUT = 120       



_sessions: dict[str, dict] = {}



def _gc() -> None:
    
    now = time.time()
    expired: list[str] = []

    for session_id, sess in _sessions.items():
        idle_time = now - sess["last_used_at"]
        age = now - sess["created_at"]

        if idle_time > SESSION_IDLE_TIMEOUT or age > SESSION_MAX_AGE:
            expired.append(session_id)

    for session_id in expired:
        sess = _sessions.pop(session_id)
        try:
            sess["sandbox"].kill()
        except Exception:
            pass 


def create_session(repository_path: str, timeout: int = 300) -> str:
   
    repository_path = validate_repo_url(repository_path)

    _gc()

    sandbox = Sandbox.create(
        template="code-interpreter-v1",
        timeout=timeout,
        api_key=settings.E2B_API_KEY,
        envs=get_sandbox_env(),
    )
    session_id = sandbox.sandbox_id

    
    try:
        result = sandbox.commands.run(
            f"git clone {repository_path} /home/user/repo",
            timeout=CLONE_TIMEOUT,
        )
        if result.exit_code != 0:
            raise SandboxSecurityError("Clone failed")

        if sandbox.files.exists("/home/user/repo/requirements.txt"):
            result = sandbox.commands.run(
                "cd /home/user/repo && pip install -r requirements.txt -q",
                timeout=PIP_INSTALL_TIMEOUT,
            )
            if result.exit_code != 0:
                raise SandboxSecurityError("Dependency install failed")

    except Exception:
        sandbox.kill()
        raise

    now = time.time()
    _sessions[session_id] = {
        "sandbox": sandbox,
        "repo_path": "/home/user/repo",
        "created_at": now,
        "last_used_at": now,
        "baseline": None,
        "patched_applied": False,
    }

    return session_id