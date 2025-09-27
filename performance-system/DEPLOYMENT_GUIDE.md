# 绩效考核系统部署指南

## 📋 目录

1. [部署概述](#部署概述)
2. [开发环境部署](#开发环境部署)
3. [生产环境部署](#生产环境部署)
4. [Docker部署](#docker部署)
5. [Nginx配置](#nginx配置)
6. [数据库配置](#数据库配置)
7. [监控和日志](#监控和日志)
8. [故障排除](#故障排除)

---

## 🎯 部署概述

### 系统架构
```
┌─────────────────┐    ┌─────────────────┐
│   组织架构系统    │    │   绩效考核系统    │
│   Port: 3002    │    │   Port: 3001    │
│   API: 8000     │    │   API: 8001     │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┘
                    │
            ┌─────────────────┐
            │   共享数据库     │
            │   PostgreSQL   │
            └─────────────────┘
```

### 部署要求
- **操作系统**: Linux (Ubuntu 20.04+), Windows 10+, macOS
- **Python**: 3.8+
- **Node.js**: 16+
- **数据库**: PostgreSQL 12+ (生产环境)
- **Web服务器**: Nginx (生产环境)
- **内存**: 最少 2GB RAM
- **存储**: 最少 10GB 可用空间

---

## 🛠️ 开发环境部署

### 1. 环境准备

#### 安装Python和Node.js
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.8 python3.8-venv python3-pip nodejs npm

# Windows (使用Chocolatey)
choco install python nodejs

# macOS (使用Homebrew)
brew install python@3.8 node
```

#### 安装Git
```bash
# Ubuntu/Debian
sudo apt install git

# Windows
# 下载并安装 Git for Windows

# macOS
brew install git
```

### 2. 克隆项目
```bash
git clone <repository-url>
cd performance-system
```

### 3. 后端部署

#### 安装Python依赖
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

#### 数据库配置
```bash
# 创建数据库
python manage.py migrate
python manage.py createsuperuser
```

#### 启动后端服务
```bash
python manage.py runserver 8001
```

### 4. 前端部署

#### 安装Node.js依赖
```bash
cd frontend
npm install
```

#### 启动前端服务
```bash
npm run dev
```

### 5. 访问系统
- **绩效考核系统**: http://localhost:3001
- **组织架构系统**: http://localhost:3002
- **API文档**: http://localhost:8001/api/docs/

---

## 🚀 生产环境部署

### 1. 服务器准备

#### 系统更新
```bash
sudo apt update && sudo apt upgrade -y
```

#### 安装必要软件
```bash
sudo apt install -y python3.8 python3.8-venv python3-pip nodejs npm nginx postgresql postgresql-contrib
```

### 2. 数据库配置

#### 安装PostgreSQL
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### 创建数据库和用户
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE performance_system;
CREATE USER performance_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE performance_system TO performance_user;
\q
```

#### 配置数据库连接
```python
# backend/performance_system/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'performance_system',
        'USER': 'performance_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 3. 应用部署

#### 创建应用目录
```bash
sudo mkdir -p /opt/performance-system
sudo chown $USER:$USER /opt/performance-system
```

#### 部署代码
```bash
cd /opt/performance-system
git clone <repository-url> .
```

#### 安装依赖
```bash
# 后端依赖
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# 前端依赖
cd ../frontend
npm install
npm run build
```

#### 数据库迁移
```bash
cd backend
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 4. 配置Gunicorn

#### 创建Gunicorn配置文件
```bash
sudo nano /opt/performance-system/backend/gunicorn.conf.py
```

```python
# gunicorn.conf.py
bind = "127.0.0.1:8001"
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

#### 创建systemd服务
```bash
sudo nano /etc/systemd/system/performance-system.service
```

```ini
[Unit]
Description=Performance System Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/performance-system/backend
ExecStart=/opt/performance-system/backend/venv/bin/gunicorn --config gunicorn.conf.py performance_system.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

#### 启动服务
```bash
sudo systemctl daemon-reload
sudo systemctl start performance-system
sudo systemctl enable performance-system
```

---

## 🐳 Docker部署

### 1. 创建Dockerfile

#### 后端Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制应用代码
COPY . .

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 暴露端口
EXPOSE 8001

# 启动命令
CMD ["gunicorn", "performance_system.wsgi:application", "--bind", "0.0.0.0:8001"]
```

#### 前端Dockerfile
```dockerfile
# frontend/Dockerfile
FROM node:16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
```

### 2. 创建docker-compose.yml

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: performance_system
      POSTGRES_USER: performance_user
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=postgresql://performance_user:your_password@db:5432/performance_system
    depends_on:
      - db
    volumes:
      - ./backend:/app
      - static_volume:/app/static

  frontend:
    build: ./frontend
    ports:
      - "3001:80"
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/var/www/static
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  static_volume:
```

### 3. 部署命令

```bash
# 构建和启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 🌐 Nginx配置

### 1. 安装Nginx
```bash
sudo apt install nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 2. 配置Nginx

#### 创建配置文件
```bash
sudo nano /etc/nginx/sites-available/performance-system
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API请求
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件
    location /static/ {
        alias /opt/performance-system/backend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # 媒体文件
    location /media/ {
        alias /opt/performance-system/backend/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 启用配置
```bash
sudo ln -s /etc/nginx/sites-available/performance-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. SSL配置 (可选)

#### 安装Certbot
```bash
sudo apt install certbot python3-certbot-nginx
```

#### 获取SSL证书
```bash
sudo certbot --nginx -d your-domain.com
```

---

## 🗄️ 数据库配置

### 1. PostgreSQL优化

#### 配置文件优化
```bash
sudo nano /etc/postgresql/13/main/postgresql.conf
```

```conf
# 内存配置
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB

# 连接配置
max_connections = 100

# 日志配置
log_statement = 'all'
log_duration = on
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

#### 重启PostgreSQL
```bash
sudo systemctl restart postgresql
```

### 2. 数据库备份

#### 创建备份脚本
```bash
sudo nano /opt/performance-system/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/performance-system/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="performance_system"

mkdir -p $BACKUP_DIR
pg_dump -h localhost -U performance_user $DB_NAME > $BACKUP_DIR/backup_$DATE.sql
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

#### 设置定时备份
```bash
chmod +x /opt/performance-system/backup.sh
crontab -e
```

```cron
# 每天凌晨2点备份
0 2 * * * /opt/performance-system/backup.sh
```

---

## 📊 监控和日志

### 1. 系统监控

#### 安装监控工具
```bash
sudo apt install htop iotop nethogs
```

#### 创建监控脚本
```bash
sudo nano /opt/performance-system/monitor.sh
```

```bash
#!/bin/bash
# 系统资源监控
echo "=== 系统资源使用情况 ==="
echo "CPU使用率:"
top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}'

echo "内存使用率:"
free -m | awk 'NR==2{printf "%.2f%%\n", $3*100/$2}'

echo "磁盘使用率:"
df -h | awk '$NF=="/"{printf "%s\n", $5}'

echo "进程状态:"
ps aux | grep -E "(gunicorn|nginx|postgres)" | grep -v grep
```

### 2. 应用日志

#### Django日志配置
```python
# backend/performance_system/settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/opt/performance-system/logs/django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

#### 创建日志目录
```bash
sudo mkdir -p /opt/performance-system/logs
sudo chown www-data:www-data /opt/performance-system/logs
```

### 3. 日志轮转

#### 配置logrotate
```bash
sudo nano /etc/logrotate.d/performance-system
```

```
/opt/performance-system/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload performance-system
    endscript
}
```

---

## 🔧 故障排除

### 1. 常见问题

#### 服务无法启动
```bash
# 检查服务状态
sudo systemctl status performance-system

# 查看错误日志
sudo journalctl -u performance-system -f

# 检查端口占用
sudo netstat -tlnp | grep :8001
```

#### 数据库连接失败
```bash
# 检查PostgreSQL状态
sudo systemctl status postgresql

# 测试数据库连接
psql -h localhost -U performance_user -d performance_system

# 检查数据库配置
sudo nano /opt/performance-system/backend/performance_system/settings.py
```

#### 前端无法访问
```bash
# 检查Nginx状态
sudo systemctl status nginx

# 检查Nginx配置
sudo nginx -t

# 查看Nginx错误日志
sudo tail -f /var/log/nginx/error.log
```

### 2. 性能优化

#### 数据库优化
```sql
-- 创建索引
CREATE INDEX idx_evaluation_task_evaluator ON evaluations_evaluationtask(evaluator_id);
CREATE INDEX idx_evaluation_task_evaluatee ON evaluations_evaluationtask(evaluatee_id);
CREATE INDEX idx_evaluation_task_status ON evaluations_evaluationtask(status);

-- 分析查询性能
EXPLAIN ANALYZE SELECT * FROM evaluations_evaluationtask WHERE evaluator_id = 1;
```

#### 应用优化
```python
# 使用数据库连接池
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'MAX_CONNS': 20,
            'MIN_CONNS': 5,
        }
    }
}
```

### 3. 安全加固

#### 防火墙配置
```bash
# 安装UFW
sudo apt install ufw

# 配置防火墙规则
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

#### 系统安全
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装安全工具
sudo apt install fail2ban

# 配置fail2ban
sudo nano /etc/fail2ban/jail.local
```

---

## 📞 技术支持

### 联系方式
- **技术支持**: support@example.com
- **文档**: 查看项目文档
- **问题反馈**: 提交GitHub Issue

### 更新维护
```bash
# 更新代码
cd /opt/performance-system
git pull origin main

# 更新依赖
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 重启服务
sudo systemctl restart performance-system
```

---

*部署指南版本: v1.0.0*  
*最后更新: 2025年9月27日*
