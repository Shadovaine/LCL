#=========================================================
# _is_admin() - Check if the user is an admin
#=========================================================

#-----------------Standard Library-----------------
import os
from .paths import _repo_root

#-----------------Admin Check-----------------
def _is_admin() -> bool:
    """
    Admin ON if:
      - LCL_ADMIN in {"1","true","yes"}  OR
      - LCL_ADMIN_TOKEN matches contents of <repo>/.lcl_admin_token
    """
    flag = os.getenv("LCL_ADMIN", "").lower()
    if flag in {"1", "true", "yes"}:
        return True
    token_env = os.getenv("LCL_ADMIN_TOKEN")
    if not token_env:
        return False
    token_file = _repo_root() / ".lcl_admin_token"
    try:
        if token_file.is_file() and token_file.read_text(encoding="utf-8").strip() == token_env.strip():
            return True
    except Exception:
        pass
    return False
