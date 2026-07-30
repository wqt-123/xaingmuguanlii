#!/bin/bash
# ============================================
# Atlas PM WebApp - 一键更新脚本
# 用法: 在本地电脑执行 bash update.sh
# 作用: 将最新代码同步到阿里云服务器 8.154.22.214
# ============================================

# ===== 配置区 (按需修改) =====
SERVER_IP="8.154.22.214"
SERVER_USER="root"
REMOTE_DIR="/var/www/atlas-pm-server"
# ==============================

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  Atlas PM WebApp - 同步到云服务器${NC}"
echo -e "${CYAN}  目标: ${SERVER_USER}@${SERVER_IP}${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 检查文件是否存在
if [ ! -f "pm-webapp.html" ]; then
  echo -e "${RED}错误: 找不到 pm-webapp.html${NC}"
  exit 1
fi

# 如果存在 atlas-pm-server 目录, 同步整个项目
if [ -d "atlas-pm-server" ]; then
  echo -e "${YELLOW}[1/3] 同步后端代码...${NC}"
  rsync -avz --delete \
    --exclude 'node_modules' \
    --exclude '.env' \
    --exclude '*.db' \
    --exclude 'logs/' \
    atlas-pm-server/ ${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/
  
  echo -e "${YELLOW}[2/3] 远程安装依赖并重启服务...${NC}"
  ssh ${SERVER_USER}@${SERVER_IP} "cd ${REMOTE_DIR} && npm install --production && pm2 restart atlas-pm || pm2 start ecosystem.config.js"
  
  echo -e "${YELLOW}[3/3] 同步完成!${NC}"
else
  # 纯前端模式: 只同步 HTML 文件
  echo -e "${YELLOW}[1/1] 上传 pm-webapp.html...${NC}"
  scp pm-webapp.html ${SERVER_USER}@${SERVER_IP}:/var/www/atlas-pm/index.html
  echo -e "${GREEN}前端文件已更新!${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  同步完成!${NC}"
echo -e "${GREEN}  访问: http://${SERVER_IP}${NC}"
echo -e "${GREEN}========================================${NC}"
