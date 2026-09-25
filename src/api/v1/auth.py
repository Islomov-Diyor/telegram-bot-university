from fastapi import APIRouter, Depends, HTTPException, status, Response
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import verify_password, create_access_token
from src.repositories.admin_repo import AdminRepository
from src.schemas.auth import LoginRequest, TokenResponse, AdminResponse
from src.models.admin import Admin
from src.api.deps import get_current_admin

router = APIRouter(prefix="/auth", tags=["Authentication"])


class ChatIdUpdateRequest(BaseModel):
    telegram_chat_id: int


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=4)
    new_password: str = Field(..., min_length=8)


@router.put("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    """Securely change current administrator password."""
    if not verify_password(data.current_password, current_admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Joriy parol noto'g'ri kiritildi."
        )

    # Password complexity checks
    new_pwd = data.new_password
    if len(new_pwd) < 8 or not any(c.isdigit() for c in new_pwd) or not any(c.isalpha() for c in new_pwd):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yangi parol kamida 8 ta belgidan iborat bo'lishi hamda raqam va harflarni o'z ichiga olishi shart."
        )

    from src.core.security import get_password_hash
    current_admin.password_hash = get_password_hash(new_pwd)
    await session.commit()
    return {"message": "Parol muvaffaqiyatli o'zgartirildi!"}


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    response: Response,
    session: AsyncSession = Depends(get_db)
):
    """Admin login endpoint, returns JWT token and sets access_token cookie."""
    admin_repo = AdminRepository(session)
    admin = await admin_repo.get_by_username(credentials.username)

    if not admin or not verify_password(credentials.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login yoki parol noto'g'ri kiritildi.",
        )

    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ushbu administrator hisobi faol emas.",
        )

    token = create_access_token(subject=admin.username)

    # Set HTTP-only cookie for seamless browser administration
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=720 * 60,
        samesite="lax"
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        admin=AdminResponse.model_validate(admin)
    )


@router.get("/me", response_model=AdminResponse)
async def get_me(current_admin: Admin = Depends(get_current_admin)):
    """Retrieve details of the currently authenticated administrator."""
    return AdminResponse.model_validate(current_admin)


@router.put("/telegram-chat-id", response_model=AdminResponse)
async def update_telegram_chat_id(
    data: ChatIdUpdateRequest,
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    """Update admin's Telegram chat ID to receive registration alerts."""
    current_admin.telegram_chat_id = data.telegram_chat_id
    await session.commit()
    await session.refresh(current_admin)
    return AdminResponse.model_validate(current_admin)


@router.post("/logout")
async def logout(response: Response):
    """Logout current admin and clear authentication cookie."""
    response.delete_cookie(key="access_token")
    return {"message": "Tizimdan muvaffaqiyatli chiqildi."}
