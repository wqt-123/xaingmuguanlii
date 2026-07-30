const Database = require('better-sqlite3');
const bcrypt = require('bcryptjs');
const path = require('path');
const fs = require('fs');

const DB_PATH = process.env.DB_PATH || path.join(__dirname, 'atlas-pm.db');

let db = null;

function getDB() {
  if (db) return db;
  
  const dir = path.dirname(DB_PATH);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  
  db = new Database(DB_PATH);
  db.pragma('journal_mode = WAL');
  db.pragma('foreign_keys = ON');
  
  return db;
}

function initSchema() {
  const d = getDB();
  
  d.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      phone TEXT UNIQUE NOT NULL,
      name TEXT NOT NULL,
      name_en TEXT,
      email TEXT,
      dept TEXT,
      password_hash TEXT NOT NULL,
      role TEXT NOT NULL DEFAULT 'member',
      permissions TEXT DEFAULT '[]',
      color TEXT DEFAULT '#7C6FF0',
      avatar TEXT,
      avatar_en TEXT,
      title TEXT,
      title_en TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS projects (
      id TEXT PRIMARY KEY,
      key TEXT NOT NULL,
      name TEXT NOT NULL,
      name_en TEXT,
      color TEXT DEFAULT '#5B9BF2',
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS issues (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      title_en TEXT,
      project_id TEXT,
      priority TEXT DEFAULT 'medium',
      status TEXT DEFAULT 'backlog',
      assignee_id TEXT,
      points INTEGER DEFAULT 0,
      due TEXT,
      start_time TEXT,
      end_time TEXT,
      created_at TEXT,
      labels TEXT DEFAULT '[]',
      description TEXT,
      description_en TEXT,
      FOREIGN KEY (project_id) REFERENCES projects(id),
      FOREIGN KEY (assignee_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      from_id TEXT NOT NULL,
      to_id TEXT NOT NULL,
      subject TEXT,
      body TEXT,
      sent_at TEXT,
      is_read INTEGER DEFAULT 0,
      FOREIGN KEY (from_id) REFERENCES users(id),
      FOREIGN KEY (to_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS reviews (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      issue_id TEXT NOT NULL,
      reviewer_id TEXT NOT NULL,
      type TEXT NOT NULL,
      content TEXT,
      coordinate_id TEXT,
      contact_id TEXT,
      created_at TEXT,
      FOREIGN KEY (issue_id) REFERENCES issues(id),
      FOREIGN KEY (reviewer_id) REFERENCES users(id),
      FOREIGN KEY (coordinate_id) REFERENCES users(id),
      FOREIGN KEY (contact_id) REFERENCES users(id)
    );

    CREATE INDEX IF NOT EXISTS idx_issues_status ON issues(status);
    CREATE INDEX IF NOT EXISTS idx_issues_assignee ON issues(assignee_id);
    CREATE INDEX IF NOT EXISTS idx_issues_project ON issues(project_id);
    CREATE INDEX IF NOT EXISTS idx_messages_to ON messages(to_id);
    CREATE INDEX IF NOT EXISTS idx_reviews_issue ON reviews(issue_id);
  `);
}

function seedData() {
  const d = getDB();
  
  const userCount = d.prepare('SELECT COUNT(*) as c FROM users').get();
  if (userCount.c > 0) return;

  const saltRounds = 10;
  const adminHash = bcrypt.hashSync('admin', saltRounds);
  const memberHash = bcrypt.hashSync('123456', saltRounds);

  const stmtUser = d.prepare(`INSERT INTO users (id, phone, name, name_en, email, dept, password_hash, role, permissions, color, avatar, avatar_en, title, title_en) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)`);
  
  stmtUser.run('admin', '00000000000', '管理员', 'Administrator', 'admin@atlas.io', '管理部', adminHash, 'admin', '["all"]', '#7C6FF0', '管', 'AD', '系统管理员', 'System Admin');
  stmtUser.run('cy', '13800000001', '陈宇', 'Chen Yu', 'chenyu@atlas.io', '产品部', memberHash, 'member', '["dashboard","board","tasks","projects","newIssue","inbox"]', '#7C6FF0', '陈', 'CY', '项目经理', 'Project Manager');
  stmtUser.run('zm', '13800000002', '张明', 'Zhang Ming', 'zhangming@atlas.io', '研发部', memberHash, 'member', '["dashboard","board","tasks","newIssue","inbox"]', '#5B9BF2', '张', 'ZM', '前端工程师', 'Frontend Dev');
  stmtUser.run('wh', '13800000003', '王浩', 'Wang Hao', 'wanghao@atlas.io', '研发部', memberHash, 'member', '["dashboard","board","tasks","newIssue","inbox"]', '#F06292', '王', 'WH', '后端工程师', 'Backend Dev');
  stmtUser.run('ln', '13800000004', '李娜', 'Li Na', 'lina@atlas.io', '设计部', memberHash, 'member', '["dashboard","board","tasks","projects","inbox"]', '#3DCCC7', '李', 'LN', '产品设计师', 'Product Designer');
  stmtUser.run('zx', '13800000005', '赵雪', 'Zhao Xue', 'zhaoxue@atlas.io', '测试部', memberHash, 'member', '["dashboard","tasks","inbox"]', '#F5A623', '赵', 'ZX', '测试工程师', 'QA Engineer');
  stmtUser.run('ly', '13800000006', '刘洋', 'Liu Yang', 'liuyang@atlas.io', '运维部', memberHash, 'member', '["dashboard","board","tasks","projects","inbox"]', '#4CB782', '刘', 'LY', 'DevOps', 'DevOps');

  const stmtProj = d.prepare(`INSERT INTO projects (id, key, name, name_en, color) VALUES (?,?,?,?,?)`);
  stmtProj.run('website', 'WEB', '官网重构', 'Website Redesign', '#5B9BF2');
  stmtProj.run('mobile', 'MOB', '移动端 v2.0', 'Mobile App v2.0', '#F06292');
  stmtProj.run('data', 'DAT', '数据平台', 'Data Platform', '#F5A623');
  stmtProj.run('tools', 'INT', '内部工具', 'Internal Tools', '#4CB782');

  const stmtIssue = d.prepare(`INSERT INTO issues (id, title, title_en, project_id, priority, status, assignee_id, points, due, start_time, end_time, created_at, labels, description, description_en) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`);
  
  const issues = [
    ['ATL-141','设计首页 Hero 区域交互稿','Design homepage hero section interaction','website','high','in-review','ln',5,'2026-08-05','2026-07-28T09:00','2026-08-05T18:00','2026-07-25T10:00','["design","frontend"]','完成首页 Hero 区域的交互设计稿，包含动效说明和响应式适配方案。','Complete interaction design for hero section including animation specs and responsive layout.'],
    ['ATL-142','实现 OAuth2 认证流程','Implement OAuth2 authentication flow','website','urgent','in-progress','wh',8,'2026-08-08','2026-07-29T09:00','2026-08-08T18:00','2026-07-24T14:00','["backend","auth"]','实现完整的 OAuth2 认证流程，支持 GitHub、Google 登录，包含 token 刷新机制。','Implement full OAuth2 flow with GitHub and Google login, including token refresh.'],
    ['ATL-143','搭建项目 CI/CD 流水线','Set up CI/CD pipeline','tools','high','done','ly',5,'2026-08-01','2026-07-26T09:00','2026-08-01T18:00','2026-07-23T09:00','["devops","ci"]','使用 GitHub Actions 搭建自动化构建、测试、部署流水线。','Set up automated build, test, deploy pipeline using GitHub Actions.'],
    ['ATL-144','编写认证模块单元测试','Write unit tests for auth module','website','medium','todo','zx',3,'2026-08-10','2026-08-06T09:00','2026-08-10T18:00','2026-07-26T11:00','["testing","auth"]','为认证模块编写覆盖率达 80% 的单元测试。','Write unit tests for auth module with 80% coverage.'],
    ['ATL-145','移动端列表页虚拟滚动优化','Mobile list virtual scroll optimization','mobile','high','in-progress','zm',5,'2026-08-09','2026-07-30T09:00','2026-08-09T18:00','2026-07-25T16:00','["frontend","performance"]','优化长列表性能，实现虚拟滚动，目标 FPS > 55。','Optimize long list performance with virtual scroll, target FPS > 55.'],
    ['ATL-146','数据看板可视化组件开发','Data dashboard visualization components','data','medium','backlog','zm',8,'2026-08-15','2026-08-10T09:00','2026-08-15T18:00','2026-07-22T09:00','["frontend","chart"]','开发折线图、柱状图、饼图等可视化组件，支持数据实时更新。','Develop line, bar, pie chart components with real-time data updates.'],
    ['ATL-147','设计移动端导航交互方案','Design mobile navigation interaction','mobile','medium','in-review','ln',3,'2026-08-06','2026-07-31T09:00','2026-08-06T18:00','2026-07-24T10:00','["design","mobile"]','完成底部 Tab 导航和侧滑菜单的交互方案。','Complete bottom tab nav and side drawer interaction design.'],
    ['ATL-148','修复时间戳字段 API 超时问题','Fix API timeout on timestamp field','data','urgent','in-progress','wh',2,'2026-08-04','2026-07-28T14:00','2026-08-04T18:00','2026-07-23T15:00','["bug","backend"]','查询时间戳字段时 API 响应超时，需优化数据库索引和查询逻辑。','API timeout when querying timestamp field, optimize DB index and query logic.'],
    ['ATL-149','配置 Nginx 反向代理与负载均衡','Configure Nginx reverse proxy and load balancing','tools','medium','done','ly',3,'2026-08-02','2026-07-27T09:00','2026-08-02T18:00','2026-07-22T11:00','["devops","nginx"]','配置 Nginx 反向代理，实现多实例负载均衡。','Configure Nginx reverse proxy with multi-instance load balancing.'],
    ['ATL-150','编写 API 接口文档','Write API documentation','data','low','todo','wh',2,'2026-08-12','2026-08-08T09:00','2026-08-12T18:00','2026-07-26T09:00','["docs","api"]','使用 Swagger 编写完整的 API 接口文档。','Write complete API documentation using Swagger.'],
    ['ATL-151','移动端推送通知功能开发','Mobile push notification feature','mobile','high','backlog','zm',5,'2026-08-14','2026-08-11T09:00','2026-08-14T18:00','2026-07-21T09:00','["mobile","feature"]','实现移动端推送通知功能，支持 Android 和 iOS。','Implement push notifications for Android and iOS.'],
    ['ATL-152','内部工具权限管理系统','Internal tools permission system','tools','high','in-progress','wh',8,'2026-08-11','2026-07-30T09:00','2026-08-11T18:00','2026-07-20T09:00','["backend","auth"]','实现基于角色的权限管理系统（RBAC）。','Implement role-based access control (RBAC) system.'],
    ['ATL-153','首页响应式适配','Homepage responsive adaptation','website','medium','todo','zm',3,'2026-08-10','2026-08-05T09:00','2026-08-10T18:00','2026-07-25T13:00','["frontend","responsive"]','完成首页在移动端、平板、桌面端的响应式适配。','Complete responsive adaptation for mobile, tablet, desktop.'],
    ['ATL-154','数据平台 ETL 流程优化','Data platform ETL optimization','data','medium','backlog','ly',8,'2026-08-20','2026-08-13T09:00','2026-08-20T18:00','2026-07-19T09:00','["data","etl"]','优化 ETL 数据处理流程，提升处理速度 50%。','Optimize ETL pipeline to improve processing speed by 50%.'],
    ['ATL-155','移动端崩溃率监控接入','Mobile crash rate monitoring','mobile','urgent','done','ly',3,'2026-08-03','2026-07-26T09:00','2026-08-03T18:00','2026-07-22T14:00','["mobile","monitoring"]','接入 Sentry 进行移动端崩溃监控。','Integrate Sentry for mobile crash monitoring.'],
    ['ATL-156','官网 SEO 优化','Website SEO optimization','website','low','backlog','ln',3,'2026-08-18','2026-08-12T09:00','2026-08-18T18:00','2026-07-18T09:00','["seo","frontend"]','优化页面 Meta 标签、结构化数据、站点地图。','Optimize meta tags, structured data, sitemap.'],
    ['ATL-157','编写端到端测试用例','Write E2E test cases','mobile','medium','todo','zx',5,'2026-08-13','2026-08-06T09:00','2026-08-13T18:00','2026-07-24T16:00','["testing","e2e"]','使用 Playwright 编写核心流程的 E2E 测试。','Write E2E tests for core flows using Playwright.'],
    ['ATL-158','数据平台监控告警配置','Data platform monitoring alerts','data','high','in-review','ly',3,'2026-08-07','2026-08-02T09:00','2026-08-07T18:00','2026-07-23T11:00','["devops","monitoring"]','配置 Prometheus + Grafana 监控告警。','Configure Prometheus + Grafana monitoring alerts.']
  ];
  for (const i of issues) stmtIssue.run(...i);

  const stmtMsg = d.prepare(`INSERT INTO messages (from_id, to_id, subject, body, sent_at, is_read) VALUES (?,?,?,?,?,?)`);
  stmtMsg.run('cy', 'admin', '本周任务分配', '管理员你好，本周的任务已分配完成，请查看看板。', '2026-08-04T09:30', 0);
  stmtMsg.run('admin', 'wh', 'OAuth2 进度确认', '王浩，OAuth2 的 token 刷新机制是否已经完成？', '2026-08-04T10:00', 0);
  stmtMsg.run('ln', 'admin', 'Hero 设计稿已上传', '首页 Hero 区域的交互稿已上传到 Figma，请查收。', '2026-08-03T16:45', 0);

  const stmtRev = d.prepare(`INSERT INTO reviews (issue_id, reviewer_id, type, content, coordinate_id, contact_id, created_at) VALUES (?,?,?,?,?,?,?)`);
  stmtRev.run('ATL-142', 'admin', 'coordination', '此任务紧急，协调张明协助后端联调，优先完成 token 刷新模块', 'zm', null, '2026-08-04T10:30');
  stmtRev.run('ATL-148', 'admin', 'contactCall', 'API 超时影响生产，电话联系刘洋确认服务器状态，赵雪同步加紧测试', 'zx', 'ly', '2026-08-04T11:00');
  stmtRev.run('ATL-141', 'admin', 'guidance', '设计稿注意移动端适配，参考移动端 v2.0 的导航交互方案，避免重复设计', null, null, '2026-08-03T15:00');

  console.log('[DB] Seed data inserted successfully');
}

function init() {
  initSchema();
  seedData();
  console.log('[DB] Database initialized at', DB_PATH);
}

module.exports = { getDB, init, initSchema, seedData };
