"""Reviews API routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.user import User
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewOut
from app.utils.pagination import success_response, error_response, make_paginated_response
from app.middleware.auth import get_current_user

router = APIRouter()


@router.get("")
async def list_reviews(
    target_type: str = Query("", max_length=32),
    target_id: int = Query(0),
    status: str = Query("", max_length=16),
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(Review).order_by(Review.created_at.desc())
    count_q = select(func.count(Review.id))
    if target_type:
        q = q.where(Review.target_type == target_type)
        count_q = count_q.where(Review.target_type == target_type)
    if target_id:
        q = q.where(Review.target_id == target_id)
        count_q = count_q.where(Review.target_id == target_id)
    if status:
        q = q.where(Review.status == status)
        count_q = count_q.where(Review.status == status)

    total = (await db.execute(count_q)).scalar()
    reviews = (await db.execute(q.offset((page - 1) * page_size).limit(page_size))).scalars().all()
    return make_paginated_response(
        [ReviewOut.model_validate(r).model_dump() for r in reviews], total, page, page_size
    )


@router.post("")
async def create_review(
    req: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = Review(**req.model_dump())
    db.add(review)
    await db.flush()
    return success_response(ReviewOut.model_validate(review).model_dump(), "审核请求已创建")


@router.put("/{review_id}")
async def update_review(
    review_id: int, req: ReviewUpdate,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    review = await db.get(Review, review_id)
    if not review:
        return error_response(404, "审核记录不存在")
    review.status = req.status
    if req.comment is not None:
        review.comment = req.comment
    await db.flush()
    return success_response(None, f"审核已{'通过' if req.status == 'approved' else '驳回'}")
