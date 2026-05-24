"""
ResuMatch AI — Admin Routes
Admin-only endpoints for user management, session tracking, and system stats.
"""

from fastapi import APIRouter, Depends, HTTPException
from auth import get_admin_user
from database import (
    get_all_users, delete_user, update_user_role,
    get_recent_sessions, get_activity_log, get_stats,
)
from memory_manager import get_system_info

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
async def admin_stats(admin: dict = Depends(get_admin_user)):
    """Get platform statistics."""
    db_stats = get_stats()
    sys_info = get_system_info()
    return {**db_stats, "system": sys_info}


@router.get("/users")
async def admin_users(admin: dict = Depends(get_admin_user)):
    """List all registered users."""
    users = get_all_users()
    return {"users": users, "total": len(users)}


@router.delete("/users/{user_id}")
async def admin_delete_user(user_id: int, admin: dict = Depends(get_admin_user)):
    """Delete a user (cannot delete admin accounts)."""
    if user_id == admin["id"]:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    success = delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found or is admin")
    return {"message": "User deleted"}


@router.put("/users/{user_id}/role")
async def admin_change_role(
    user_id: int, role: str, admin: dict = Depends(get_admin_user)
):
    """Change a user's role (user/admin)."""
    if user_id == admin["id"]:
        raise HTTPException(status_code=400, detail="Cannot change your own role")
    success = update_user_role(user_id, role)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid role or user not found")
    return {"message": f"Role updated to {role}"}


@router.get("/sessions")
async def admin_sessions(
    limit: int = 50, admin: dict = Depends(get_admin_user)
):
    """Get recent login/logout sessions."""
    sessions = get_recent_sessions(limit)
    return {"sessions": sessions, "total": len(sessions)}


@router.get("/activity")
async def admin_activity(
    limit: int = 100, admin: dict = Depends(get_admin_user)
):
    """Get activity log."""
    log = get_activity_log(limit)
    return {"activity": log, "total": len(log)}
