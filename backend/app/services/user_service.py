from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import get_hashed_password, verify_password
from app.models.user import User
from app.schema.auth import UserCreate, UserLogin
from app.schema.user import UserUpdate


class UserService:
    async def create_user(self, session: AsyncSession, user_create: UserCreate) -> User:
        """
        Create a new user.
        """
        # -----
        """
        Pydantic(SQLModel) validate the data.
        check is user with email already exists.
        if yes say -> Email exists
        no ?
        hash the password
        create user
        return user
        """
        statement = select(User).where(User.email == user_create.email)
        existing_user = (await session.exec(statement)).first()

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
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return db_user

    async def login(
        self, session: AsyncSession, user_login: UserLogin
    ) -> Optional[User]:
        """
        Login a user.
        """

        """
        check email exists or not no say no
        if yes verify the password . can't say no
        if email exists and password is correct then return the user
        """
        statement = select(User).where(User.email == user_login.email)
        user = (await session.exec(statement)).first()
        if not user:
            return None
        if not verify_password(user_login.password, user.password):
            return None

        return user

    async def get_user_by_id(
        self, session: AsyncSession, user_id: str
    ) -> Optional[User]:
        """
        Get a user by id.
        """
        return await session.get(User, UUID(user_id))

    async def update_user(
        self, session: AsyncSession, user: User, user_update: UserUpdate
    ) -> User:
        """
        Update a user.
        """
        user_data = user_update.model_dump(exclude_unset=True)
        for key, value in user_data.items():
            setattr(user, key, value)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def update_user_status(
        self, session: AsyncSession, user: User, is_active: bool
    ) -> User:
        """
        Update a user status.
        """
        user.is_active = is_active
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
