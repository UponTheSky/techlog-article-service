from typing import final, Annotated
from uuid import UUID

from fastapi import status as HTTPStatus, HTTPException, Depends

from common.utils.password import hash_password
from adapter.out.persistences import UserPersistenceAdapter, UserAuthPersistenceAdapter

from .port.in_ import (
    SignUpDTO,
    SignUpPort,
    SignOutPort,
    UpdateAccountDTO,
    UpdateAccountPort,
)
from .port.out import (
    CheckUserPort,
    CreateUserDTO,
    CreateUserPort,
    UpdateUserDTO,
    UpdateUserPort,  # noqa: F401
    DeleteUserAuthPort,
)


async def _userinfo_exists(
    *, check_user_port: CheckUserPort, username: str, email: str
) -> bool:
    if await check_user_port.check_by_username(username):
        return True

    if await check_user_port.check_by_email(email):
        return True

    return False


@final
class SignUpService(SignUpPort):
    def __init__(
        self,
        *,
        check_user_port: Annotated[CheckUserPort, Depends(UserPersistenceAdapter)],
        create_user_port: Annotated[CreateUserPort, Depends(UserPersistenceAdapter)]
    ):
        self._check_user_port = check_user_port
        self._create_user_port = create_user_port

    async def sign_up(self, *, dto: SignUpDTO) -> None:
        if await _userinfo_exists(
            check_user_port=self._check_user_port,
            username=dto.username,
            email=dto.email,
        ):
            raise HTTPException(
                status_code=HTTPStatus.HTTP_400_BAD_REQUEST,
                detail="A user with the same username or email already exists",
            )

        await self._create_user_port.create_user(
            dto=CreateUserDTO(
                username=dto.username,
                hashed_password=hash_password(password=dto.password),
                email=dto.email,
            )
        )


@final
class SignOutService(SignOutPort):
    def __init__(
        self,
        delete_user_auth_port: Annotated[
            DeleteUserAuthPort, Depends(UserAuthPersistenceAdapter)
        ],
    ):
        self._delete_user_auth_port = delete_user_auth_port

    async def sign_out(self, *, user_id: UUID) -> None:
        await self._delete_user_auth_port.delete_user_auth(user_id=user_id)

        return None


@final
class UpdateAccountService(UpdateAccountPort):
    def __init__(
        self,
        *,
        check_user_port: Annotated[CheckUserPort, Depends(UserPersistenceAdapter)],
        update_user_port: Annotated[UpdateUserPort, Depends(UserPersistenceAdapter)]
    ):
        self._check_user_port = check_user_port
        self._update_user_port = update_user_port

    async def update_account(self, *, dto: UpdateAccountDTO) -> None:
        if await _userinfo_exists(
            check_user_port=self._check_user_port,
            username=dto.username,
            email=dto.email,
        ):
            raise HTTPException(
                status_code=HTTPStatus.HTTP_400_BAD_REQUEST,
                detail="A user with the same username or email already exists",
            )

        if dto.password:
            dto.password = hash_password(dto.password)

        await self._update_user_port.update_user(
            user_id=dto.user_id,
            dto=UpdateUserDTO(**UpdateAccountDTO.dict(exclude_none=True)),
        )

        return None