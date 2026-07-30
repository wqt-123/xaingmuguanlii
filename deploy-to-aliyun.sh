#!/bin/bash
# ============================================
# Atlas PM WebApp - 阿里云 ECS 部署脚本
# 适用系统: CentOS 7/8, Ubuntu 18/20/22, Alibaba Cloud Linux
# 使用方法: sudo bash deploy-to-aliyun.sh
# ============================================

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  Atlas PM WebApp 部署脚本${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# 检查 root 权限
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}请使用 root 用户或 sudo 运行此脚本${NC}"
  echo -e "  sudo bash deploy-to-aliyun.sh"
  exit 1
fi

# 检测系统类型
if [ -f /etc/os-release ]; then
  . /etc/os-release
  OS=$ID
  echo -e "${GREEN}检测到系统: $PRETTY_NAME${NC}"
else
  echo -e "${YELLOW}无法检测系统类型，默认使用 CentOS 模式${NC}"
  OS="centos"
fi

# ===== 第 1 步: 安装 Nginx =====
echo ""
echo -e "${YELLOW}[1/5] 安装 Nginx...${NC}"

if command -v nginx &> /dev/null; then
  echo -e "${GREEN}Nginx 已安装, 跳过${NC}"
else
  if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt-get update -y
    apt-get install -y nginx
  else
    # CentOS / Alibaba Cloud Linux / RHEL
    if command -v dnf &> /dev/null; then
      dnf install -y nginx
    else
      yum install -y nginx
    fi
  fi
  echo -e "${GREEN}Nginx 安装完成${NC}"
fi

# ===== 第 2 步: 创建网站目录 =====
echo ""
echo -e "${YELLOW}[2/5] 创建网站目录...${NC}"

WEB_DIR="/var/www/atlas-pm"
mkdir -p "$WEB_DIR"
echo -e "${GREEN}网站目录: $WEB_DIR${NC}"

# ===== 第 3 步: 部署 HTML 文件 =====
echo ""
echo -e "${YELLOW}[3/5] 部署网页文件...${NC}"
echo -e "请将 pm-webapp.html 复制到此服务器后重命名为 index.html"
echo -e "或者将文件内容粘贴到下方提示处"
echo ""
echo -e "方法一 (SCP 上传):"
echo -e "  在本地电脑执行:"
echo -e "  scp pm-webapp.html root@你的服务器IP:$WEB_DIR/index.html"
echo ""
echo -e "方法二 (手动复制):"
echo -e "  如果文件已在本服务器, 执行:"
echo -e "  cp pm-webapp.html $WEB_DIR/index.html"
echo ""

# 如果当前目录有 pm-webapp.html 或 index.html, 自动复制
if [ -f "./pm-webapp.html" ]; then
  cp ./pm-webapp.html "$WEB_DIR/index.html"
  echo -e "${GREEN}已自动复制 ./pm-webapp.html${NC}"
elif [ -f "./index.html" ]; then
  cp ./index.html "$WEB_DIR/index.html"
  echo -e "${GREEN}已自动复制 ./index.html${NC}"
elif [ -f "$WEB_DIR/index.html" ]; then
  echo -e "${GREEN}index.html 已存在于 $WEB_DIR${NC}"
else
  echo -e "${YELLOW}未找到 HTML 文件, 请上传后重新运行此脚本${NC}"
  echo -e "${YELLOW}或手动执行: cp 你的文件.html $WEB_DIR/index.html${NC}"
fi

# 设置权限
chown -R nginx:nginx "$WEB_DIR" 2>/dev/null || chown -R www-data:www-data "$WEB_DIR" 2>/dev/null || true
chmod -R 755 "$WEB_DIR"
echo -e "${GREEN}权限设置完成${NC}"

# ===== 第 4 步: 配置 Nginx =====
echo ""
echo -e "${YELLOW}[4/5] 配置 Nginx...${NC}"

NGINX_CONF="/etc/nginx/conf.d/atlas-pm.conf"

cat > "$NGINX_CONF" << 'EOF'
server {
    listen 80;
    server_name _;

    root /var/www/atlas-pm;
    index index.html;

    # gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/javascript text/xml application/xml;
    gzip_min_length 1000;
    gzip_comp_level 6;

    # 主页面
    location / {
        try_files $uri $uri/ =404;
    }

    # 静态文件缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 访问日志
    access_log /var/log/nginx/atlas-pm-access.log;
    error_log /var/log/nginx/atlas-pm-error.log;
}
EOF

echo -e "${GREEN}Nginx 配置已写入: $NGINX_CONF${NC}"

# 测试 Nginx 配置
nginx -t
echo -e "${GREEN}Nginx 配置测试通过${NC}"

# ===== 第 5 步: 启动服务并配置防火墙 =====
echo ""
echo -e "${YELLOW}[5/5] 启动服务并配置防火墙...${NC}"

# 启动并设置开机自启
systemctl start nginx
systemctl enable nginx
echo -e "${GREEN}Nginx 已启动并设为开机自启${NC}"

# 配置防火墙
if command -v firewall-cmd &> /dev/null; then
  firewall-cmd --permanent --add-service=http
  firewall-cmd --permanent --add-service=https
  firewall-cmd --reload
  echo -e "${GREEN}firewalld 已开放 80/443 端口${NC}"
elif command -v ufw &> /dev/null; then
  ufw allow 80/tcp
  ufw allow 443/tcp
  echo -e "${GREEN}ufw 已开放 80/443 端口${NC}"
else
  echo -e "${YELLOW}未检测到防火墙, 请手动开放 80 和 443 端口${NC}"
fi

# ===== 获取服务器公网 IP =====
PUBLIC_IP=$(curl -s http://ifconfig.me 2>/dev/null || curl -s http://ip.sb 2>/dev/null || echo "未知")

# ===== 完成 =====
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}  部署完成!${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "访问地址: ${GREEN}http://$PUBLIC_IP${NC}"
echo -e "或使用域名: ${GREEN}http://你的域名${NC}"
echo -e "登录账号: ${GREEN}admin${NC}"
echo -e "登录密码: ${GREEN}admin${NC}"
echo ""
echo -e "${YELLOW}重要提醒:${NC}"
echo -e "  1. 请在阿里云控制台 -> 安全组 -> 添加入方向规则"
echo -e "     协议: TCP  端口: 80/443  授权对象: 0.0.0.0/0"
echo -e "  2. 如需 HTTPS, 运行: sudo bash deploy-to-aliyun.sh --ssl"
echo -e "  3. 如需绑定域名, 修改 $NGINX_CONF 中的 server_name"
echo ""

# ===== HTTPS 选项 =====
if [ "$1" = "--ssl" ]; then
  echo -e "${YELLOW}[附加] 配置 HTTPS (Let's Encrypt)...${NC}"

  DOMAIN=""
  read -p "请输入你的域名 (如 pm.example.com): " DOMAIN

  if [ -z "$DOMAIN" ]; then
    echo -e "${RED}域名不能为空, 跳过 HTTPS 配置${NC}"
    exit 0
  fi

  # 安装 certbot
  if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt-get install -y certbot python3-certbot-nginx
  else
    if command -v dnf &> /dev/null; then
      dnf install -y certbot python3-certbot-nginx
    else
      yum install -y certbot python3-certbot-nginx
    fi
  fi

  # 更新 Nginx 配置中的 server_name
  sed -i "s/server_name _;/server_name $DOMAIN;/" "$NGINX_CONF"
  nginx -t && systemctl reload nginx

  # 申请证书
  certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --register-unsafely-without-email

  echo -e "${GREEN}HTTPS 配置完成!${NC}"
  echo -e "访问地址: ${GREEN}https://$DOMAIN${NC}"
fi
