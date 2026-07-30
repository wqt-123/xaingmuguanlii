"""Templates API routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.user import User
from app.models.template import Template
from app.schemas.template import TemplateCreate, TemplateUpdate, TemplateOut
from app.utils.pagination import success_response, error_response, make_paginated_response
from app.middleware.auth import get_current_user

router = APIRouter()


BUILTIN_TEMPLATES = [
    {
        "name": "敏捷开发模板", "type": "project", "is_builtin": True, "scope": "team",
        "content": {
            "phases": ["需求池", "Sprint计划", "开发", "测试", "回顾"],
            "default_roles": ["Product Owner", "Scrum Master", "开发", "测试"],
            "task_statuses": ["Backlog", "Todo", "In Progress", "Review", "Done"],
        },
    },
    {
        "name": "瀑布开发模板", "type": "project", "is_builtin": True, "scope": "team",
        "content": {
            "phases": ["需求分析", "系统设计", "编码实现", "测试验证", "上线部署", "维护"],
            "default_roles": ["项目经理", "需求分析师", "架构师", "开发", "测试", "运维"],
            "task_statuses": ["未开始", "进行中", "已完成", "已延期"],
        },
    },
    {
        "name": "产品迭代模板", "type": "project", "is_builtin": True, "scope": "team",
        "content": {
            "phases": ["版本规划", "需求评审", "迭代开发", "验收测试", "发布"],
            "default_roles": ["产品经理", "设计师", "前端", "后端", "测试"],
            "task_statuses": ["规划中", "待开发", "开发中", "待测试", "已完成"],
        },
    },
    {
        "name": "运维项目模板", "type": "project", "is_builtin": True, "scope": "team",
        "content": {
            "phases": ["变更管理", "故障处理", "巡检", "优化"],
            "default_roles": ["运维经理", "DBA", "网络", "安全"],
            "task_statuses": ["待处理", "处理中", "已解决", "已关闭"],
        },
    },
    {
        "name": "市场活动模板", "type": "project", "is_builtin": True, "scope": "team",
        "content": {
            "phases": ["活动策划", "物料准备", "执行", "效果追踪"],
            "default_roles": ["市场总监", "策划", "设计师", "文案", "数据分析"],
            "task_statuses": ["待开始", "进行中", "待审核", "已完成"],
        },
    },
    {
        "name": "通用项目模板", "type": "project", "is_builtin": True, "scope": "team",
        "content": {
            "phases": ["启动", "计划", "执行", "监控", "收尾"],
            "default_roles": ["项目经理", "团队成员"],
            "task_statuses": ["todo", "in_progress", "review", "done"],
        },
    },
]


@router.get("")
async def list_templates(
    type: str = Query("", max_length=32),
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(Template).order_by(Template.created_at.desc())
    count_q = select(func.count(Template.id))
    if type:
        q = q.where(Template.type == type)
        count_q = count_q.where(Template.type == type)

    total = (await db.execute(count_q)).scalar()
    user_templates = (await db.execute(q.offset((page - 1) * page_size).limit(page_size))).scalars().all()

    # Merge built-in templates on first page with no type filter
    items = []
    if page == 1 and not type:
        items = [t for t in BUILTIN_TEMPLATES]
        items.extend([TemplateOut.model_validate(ut).model_dump() for ut in user_templates])
    else:
        items = [TemplateOut.model_validate(ut).model_dump() for ut in user_templates]

    return make_paginated_response(items, total + len(BUILTIN_TEMPLATES), page, page_size)


@router.post("")
async def create_template(
    req: TemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    template = Template(**req.model_dump(), created_by=current_user.id)
    db.add(template)
    await db.flush()
    return success_response(TemplateOut.model_validate(template).model_dump(), "模板创建成功")


@router.get("/{template_id}")
async def get_template(template_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check built-in first
    if template_id <= len(BUILTIN_TEMPLATES):
        return success_response(BUILTIN_TEMPLATES[template_id - 1])
    template = await db.get(Template, template_id)
    if not template:
        return error_response(404, "模板不存在")
    return success_response(TemplateOut.model_validate(template).model_dump())


@router.put("/{template_id}")
async def update_template(
    template_id: int, req: TemplateUpdate,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    template = await db.get(Template, template_id)
    if not template:
        return error_response(404, "模板不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(template, k, v)
    await db.flush()
    return success_response(TemplateOut.model_validate(template).model_dump(), "模板更新成功")


@router.delete("/{template_id}")
async def delete_template(template_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    template = await db.get(Template, template_id)
    if not template:
        return error_response(404, "模板不存在")
    await db.delete(template)
    await db.flush()
    return success_response(None, "模板已删除")
