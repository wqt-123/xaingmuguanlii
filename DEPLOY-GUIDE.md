# Atlas PM WebApp — 阿里云部署指南

## 概述

本指南将帮助你在阿里云 ECS 服务器上部署 Atlas PM WebApp，使其可以通过公网 IP 或域名在任何电脑/浏览器上访问。

---

## 前置条件

1. **阿里云 ECS 服务器** — 已购买并可正常连接
2. **操作系统** — CentOS 7/8、Ubuntu 18/20/22、Alibaba Cloud Linux 2/3
3. **安全组** — 已开放 80 端口（HTTP）和 443 端口（HTTPS）
4. **SSH 连接工具** — 如 PuTTY、Xshell、终端等

---

## 方法一：一键脚本部署（推荐）

### 第 1 步：上传文件到服务器

在你的**本地电脑**终端执行：

```bash
# Windows PowerShell / Git Bash / Mac/Linux Terminal
scp pm-webapp.html root@你的服务器IP:/root/
```

例如：
```bash
scp pm-webapp.html root@47.96.123.456:/root/
```

输入服务器密码后文件即上传完成。

### 第 2 步：上传部署脚本

```bash
scp deploy-to-aliyun.sh root@你的服务器IP:/root/
```

### 第 3 步：SSH 连接服务器并运行脚本

```bash
# 连接服务器
ssh root@你的服务器IP

# 运行部署脚本
cd /root
sudo bash deploy-to-aliyun.sh
```

脚本会自动完成：安装 Nginx → 创建目录 → 部署文件 → 配置 Nginx → 开放防火墙 → 启动服务

### 第 4 步：配置阿里云安全组

1. 登录 [阿里云控制台](https://ecs.console.aliyun.com)
2. 找到你的 ECS 实例 → 点击实例 ID
3. 左侧菜单 → **安全组** → 点击安全组 ID
4. **入方向** → **手动添加**
5. 添加规则：
   - 协议类型：TCP
   - 端口范围：80/80
   - 授权对象：0.0.0.0/0
   - 描述：HTTP
6. 再添加一条 443 端口规则（用于 HTTPS）

### 第 5 步：访问

浏览器打开 `http://你的服务器IP`，即可看到应用界面。

登录账号：`admin` / 密码：`admin`

---

## 方法二：手动部署（分步骤）

### 1. 安装 Nginx

**CentOS / Alibaba Cloud Linux:**
```bash
sudo yum install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

**Ubuntu / Debian:**
```bash
sudo apt update
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 2. 创建网站目录

```bash
sudo mkdir -p /var/www/atlas-pm
```

### 3. 上传 HTML 文件

在本地电脑执行：
```bash
scp pm-webapp.html root@你的服务器IP:/var/www/atlas-pm/index.html
```

### 4. 设置权限

```bash
sudo chown -R nginx:nginx /var/www/atlas-pm    # CentOS
# 或
sudo chown -R www-data:www-data /var/www/atlas-pm  # Ubuntu
sudo chmod -R 755 /var/www/atlas-pm
```

### 5. 配置 Nginx

创建配置文件：
```bash
sudo nano /etc/nginx/conf.d/atlas-pm.conf
```

粘贴以下内容：
```nginx
server {
    listen 80;
    server_name _;

    root /var/www/atlas-pm;
    index index.html;

    gzip on;
    gzip_types text/plain text/css application/javascript;
    gzip_min_length 1000;

    location / {
        try_files $uri $uri/ =404;
    }

    location ~* \.(js|css|png|jpg|svg|woff2?)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

保存并退出（`Ctrl+X` → `Y` → `Enter`）。

### 6. 测试并重载 Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 7. 开放防火墙

```bash
# CentOS
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload

# Ubuntu
sudo ufw allow 80/tcp
```

### 8. 配置安全组（同方法一第 4 步）

### 9. 访问

浏览器打开 `http://你的服务器IP`

---

## 方法三：配置 HTTPS（可选但推荐）

如果你有域名，可以配置 HTTPS 免费证书：

### 1. 绑定域名

在阿里云控制台 → **云解析 DNS** → 添加 A 记录：
- 记录类型：A
- 主机记录：pm（或你想要的子域名）
- 记录值：你的服务器公网 IP

### 2. 申请免费 SSL 证书

**方式 A — Let's Encrypt（免费）：**
```bash
# 安装 certbot
sudo yum install -y certbot python3-certbot-nginx   # CentOS
# 或
sudo apt install -y certbot python3-certbot-nginx   # Ubuntu

# 修改 nginx 配置中的 server_name 为你的域名
sudo nano /etc/nginx/conf.d/atlas-pm.conf
# 将 server_name _; 改为 server_name pm.你的域名.com;
sudo nginx -t && sudo systemctl reload nginx

# 申请证书
sudo certbot --nginx -d pm.你的域名.com
```

**方式 B — 阿里云免费证书：**
1. 阿里云控制台 → **数字证书管理服务** → **SSL 证书**
2. 申请免费证书 → 填写域名 → 验证
3. 下载 Nginx 格式证书
4. 上传到服务器并配置 Nginx

---

## 常见问题

### Q: 访问不了怎么办？

按顺序检查：
1. **安全组** — 确认 80 端口已开放（最常见原因）
2. **防火墙** — `sudo firewall-cmd --list-all` 或 `sudo ufw status`
3. **Nginx 状态** — `sudo systemctl status nginx`
4. **Nginx 配置** — `sudo nginx -t`
5. **文件权限** — `ls -la /var/www/atlas-pm/`

### Q: 修改了 HTML 文件怎么更新？

```bash
# 重新上传文件
scp pm-webapp.html root@你的服务器IP:/var/www/atlas-pm/index.html

# 不需要重启 Nginx，直接刷新浏览器即可
```

### Q: 数据会丢失吗？

本应用使用浏览器 localStorage 存储数据，数据保存在**访问者的浏览器**中。
不同电脑/浏览器访问时数据是独立的，这是纯前端应用的特性。

如果需要多用户共享数据，后续需要升级为后端+数据库方案。

### Q: 如何查看访问日志？

```bash
sudo tail -f /var/log/nginx/atlas-pm-access.log
```

---

## 文件清单

| 文件 | 说明 |
|------|------|
| `pm-webapp.html` | 主应用文件（128K，单文件包含全部前端代码） |
| `deploy-to-aliyun.sh` | 一键部署脚本 |
| `DEPLOY-GUIDE.md` | 本部署指南 |

---

## 技术架构

```
用户浏览器 (任何设备)
    ↓ HTTP/HTTPS
阿里云 ECS (公网 IP)
    ↓ :80
Nginx Web Server
    ↓ 静态文件
/var/www/atlas-pm/index.html
```

纯前端单文件应用，无需数据库、无需后端服务，Nginx 直接提供静态文件服务，性能极高。
