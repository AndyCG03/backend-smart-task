from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.database_models import User
from app.security.auth import get_current_active_user

# Dependencia para obtener el usuario actual
def get_current_user_dependency():
    return Depends(get_current_active_user)

# Dependencia para verificar si el usuario es admin (opcional)
async def get_current_admin(
    current_user: User = Depends(get_current_active_user)
):
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user