from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.core.security import get_hashed_password, verify_password
from app.db.main import get_session
from app.db.models.user import User
from app.schemas.auth import UserCreate, UserLogin
from app.schemas.user import UserUpdate


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_user(self, user_create: UserCreate) -> User:
        """
        Create a new user.
        """
        statement = select(User).where(User.email == user_create.email)
        existing_user = (
            (await self.session.execute(statement)).scalars().first()
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed_password = get_hashed_password(user_create.password)
        db_user = User(
            email=user_create.email,
            password=hashed_password,
            full_name=user_create.full_name,
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        logger.info(f"User created: {db_user.email}")
        return db_user

    async def login(self, user_login: UserLogin) -> User | None:
        """
        Login a user.
        """
        statement = select(User).where(User.email == user_login.email)
        user = (await self.session.execute(statement)).scalars().first()
        if not user:
            return None
        if not verify_password(user_login.password, user.password):
            return None

        return user

    async def get_user_by_id(self, user_id: str) -> User | None:
        """
        Get a user by id.
        """
        return await self.session.get(User, UUID(user_id))

    async def update_user(self, user: User, user_update: UserUpdate) -> User:
        """
        Update a user.
        """
        user_data = user_update.model_dump(exclude_unset=True)
        for key, value in user_data.items():
            setattr(user, key, value)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_user_status(self, user: User, is_active: bool) -> User:
        """
        Update a user status.
        """
        user.is_active = is_active
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user


def get_user_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserService:
    return UserService(session)


user_service = get_user_service
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
