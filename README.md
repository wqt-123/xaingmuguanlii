# 晴天天 Atlas PM — 项目管理平台

基于 PRD 文档构建的全栈项目管理系统，覆盖计划制定、甘特图、需求管理、缺陷跟踪全生命周期。

## 技术架构

| 层 | 技术 | 说明 |
|----|------|------|
| 前端 | Vue 3 + Vite + TypeScript + Tailwind CSS | 驾驶舱暗色主题, 玻璃拟态面板 |
| 后端 | Python FastAPI + SQLAlchemy 2.0 | 异步 REST API, JWT 认证 |
| 数据库 | MySQL 8.0 | 15 张核心表, InnoDB 引擎 |
| 部署 | Nginx + systemd | ECS 云服务器, 单端口 80 |

## 功能模块

### ✅ V1.0 已完成
- **仪表盘**: KPI 指标卡片, 项目进度条, 风险预警, 我的待办
- **甘特图**: 时间轴视图, 任务拖拽排期, 里程碑标记, 依赖连线
- **计划管理**: 计划 CRUD, WBS 任务分解(多级), 提交审核
- **需求管理**: 需求池, 优先级/来源/标签, 需求变更追踪
- **缺陷管理**: 缺陷录入, 状态流转(新建→已分配→修复中→已修复→已验证→已关闭), 统计分析
- **团队管理**: 成员列表, 角色权限
- **消息中心**: 站内通知, 已读/未读

### 🔜 计划中
- 审核批复流程 (计划/需求/变更/里程碑)
- 模板体系 (敏捷/瀑布/产品迭代/运维/市场活动)
- IM 集成 (飞书/企业微信)
- 自定义字段与工作流

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- MySQL 8.0

### 后端启动
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # 编辑数据库连接信息
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 前端启动
```bash
cd frontend
npm install
npm run dev  # 开发模式 http://localhost:5173/qingtian/
npm run build  # 生产构建到 dist/
```

### 部署
```bash
# 构建前端
cd frontend && npm run build

# Nginx 配置 (示例)
server {
    listen 80;
    location /qingtian/ {
        alias /path/to/frontend/dist/;
        try_files $uri $uri/ /qingtian/index.html;
    }
    location /qingtian/api/ {
        rewrite ^/qingtian/api/v1(/.*)$ $1 break;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

## 数据库表

| 模块 | 表名 | 说明 |
|------|------|------|
| 用户 | users | 用户账号/角色/部门 |
| 项目 | projects, project_members | 项目与成员关联 |
| 计划 | plans, tasks, milestones, task_dependencies | WBS 任务分解与依赖 |
| 需求 | requirements, requirement_changes | 需求池与变更记录 |
| 缺陷 | defects, defect_attachments | 缺陷与附件 |
| 审核 | reviews | 多态审核 (计划/需求/变更/里程碑) |
| 通用 | notifications, audit_logs, templates | 通知/审计/模板 |

## 访问地址

> 🌐 **http://8.154.22.214/qingtian/**

默认账号: `admin` / `wqt158205`

## License

MIT
