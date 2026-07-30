"""Role-based access control dependency."""
from fastapi import Depends, HTTPException, status
from app.models.user import User, UserRole
from app.middleware.auth import get_current_user


class RoleChecker:
    """Factory that creates a dependency to check user roles."""

    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user


# Pre-built checkers
require_admin = RoleChecker([UserRole.ADMIN])
require_admin_or_pm = RoleChecker([UserRole.ADMIN, UserRole.PM])
