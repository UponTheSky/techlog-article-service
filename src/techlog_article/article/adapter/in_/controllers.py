from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Query,
    Path,
    Body,
    status as HTTPStatus,
    Depends,
    HTTPException,
)

from common.tags import Tags
from auth.application.services import CurrentUserIdDependency

from application.services import CreateArticleService, ReadArticeService

from application.port.in_ import (
    CreateArticleInDTO,
    CreateArticleInPort,
    ReadArticleListInDTO,
    ReadArticleInPort,
    ReadArticleResponse,
    ReadArticleListResponse,
)

from ._dtos import CreateArticleBody


router = APIRouter(
    prefix="/article",
    tags=[Tags.article],
    responses={HTTPStatus.HTTP_404_NOT_FOUND: {"description": "Not Found"}},
)


# CREATE
@router.post("/", status_code=HTTPStatus.HTTP_201_CREATED)
async def create_article(
    *,
    author_id: CurrentUserIdDependency,
    body: CreateArticleBody = Body(),
    create_article_service: Annotated[
        CreateArticleInPort, Depends(CreateArticleService)
    ],
) -> None:
    await create_article_service.create_article(
        dto=CreateArticleInDTO(
            title=body.title, content=body.content, author_id=author_id
        )
    )

    return None


# READ
@router.get("/", status_code=HTTPStatus.HTTP_200_OK)
async def read_articles(
    *,
    offset: int = Query(),
    limit: int = Query(),
    order_by: str = "created_at",
    read_article_in_port: Annotated[ReadArticleInPort, Depends(ReadArticeService)],
) -> ReadArticleListResponse:
    return await read_article_in_port.read_article_list(
        dto=ReadArticleListInDTO(offset=offset, limit=limit, order_by=order_by)
    )


@router.get("/{id}", status_code=HTTPStatus.HTTP_200_OK)
async def read_article_by_id(
    *,
    id: UUID = Path(),
    read_article_in_port: Annotated[ReadArticleInPort, Depends(ReadArticeService)],
) -> ReadArticleResponse:
    article_response = await read_article_in_port.read_article_by_id(id)
    if not article_response:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_404_NOT_FOUND,
            detail=f"The article of id {id} doesn't exist in the DB",
        )

    return article_response


# # UPDATE
# @router.patch("/{id}", status_code=HTTPStatus.HTTP_200_OK)
# async def update_article(
#     *,
#     id: UUID = Path(),
#     user: CurrentUserDependency,
#     data: UpdateArticle = Body(
#         description="data required for updating an article item"
#     ),
# ) -> ArticleResponse:
#     raise NotImplementedError()


# # DELETE
# @router.delete("/{id}", status_code=HTTPStatus.HTTP_200_OK)
# async def delete_article(
#     *,
#     id: UUID = Path(),
#     user: CurrentUserDependency,
# ) -> ArticleResponse:
#     raise NotImplementedError()