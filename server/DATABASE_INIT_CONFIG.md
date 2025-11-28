# 数据库初始化配置说明

## 环境模式

GameVault 支持两种数据库初始化模式，通过 `.env` 文件中的 `ENVIRONMENT` 配置项控制：

### 1. 开发模式 (Development)

```bash
ENVIRONMENT=development
```

**特点：**
- 使用 `Base.metadata.create_all()` 直接创建数据库表
- 不使用 Alembic 迁移系统
- 快速启动，适合频繁修改数据模型
- 每次启动自动同步模型到数据库

**适用场景：**
- 本地开发环境
- 数据库结构频繁变更
- 测试和原型开发

### 2. 生产模式 (Production)

```bash
ENVIRONMENT=production
```

**特点：**
- 使用 Alembic 迁移系统管理数据库变更
- 自动备份数据库（保留最近 10 个备份）
- 支持版本控制和回滚
- 更安全的数据库升级流程

**适用场景：**
- 生产环境部署
- 需要保留数据的环境
- 多人协作开发

## 配置文件

项目提供了三个配置文件模板：

1. **`.env.example`** - 配置模板，包含所有可配置项
2. **`.env.development`** - 开发环境配置
3. **`.env.production`** - 生产环境配置

## 使用方法

### 开发环境

```bash
# 复制开发配置
cp .env.development .env

# 或直接创建 .env 文件并设置
echo "ENVIRONMENT=development" > .env

# 启动服务器
uvicorn app.main:app --reload
```

### 生产环境

```bash
# 复制生产配置
cp .env.production .env

# 修改敏感信息（SECRET_KEY、API Keys 等）
# 然后启动服务器
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 数据库初始化流程

应用启动时会自动执行 `init_db()` 函数：

```
启动应用
    ↓
调用 init_db()
    ↓
检查 ENVIRONMENT 配置
    ↓
┌──────────────────────┬──────────────────────┐
│   development 模式    │   production 模式     │
├──────────────────────┼──────────────────────┤
│ 直接创建/更新表结构   │ 运行 Alembic 迁移    │
│ Base.metadata.create  │ auto_migrate()       │
└──────────────────────┴──────────────────────┘
    ↓
初始化默认数据
    ↓
插入 ContentRating 默认分级
    ↓
启动完成
```

## 默认数据

系统会自动初始化以下默认数据：

### 内容分级 (Content Ratings)

| Age Limit | Name | Description |
|-----------|------|-------------|
| 0 | E - Everyone | 全年龄 |
| 3 | EC - Early Childhood | 幼儿 |
| 7 | E7+ - Everyone 7+ | 7岁以上 |
| 10 | E10+ - Everyone 10+ | 10岁以上 |
| 12 | T - Teen (PEGI 12) | 青少年 |
| 13 | T - Teen | 青少年 |
| 16 | M16+ - Mature 16+ | 成熟内容 |
| 17 | M - Mature 17+ | 成熟17+ |
| 18 | AO - Adults Only | 仅限成人 |

## 注意事项

1. **首次运行前**：确保已配置好 `.env` 文件
2. **切换模式**：修改 `ENVIRONMENT` 后需要重启应用
3. **生产环境**：务必修改 `SECRET_KEY` 为随机字符串
4. **备份**：生产模式会自动备份，备份文件位于 `storage/backups/`
5. **迁移文件**：如果在生产模式下修改了模型，需要创建 Alembic 迁移文件

## 创建迁移文件（生产模式）

当修改了数据模型后：

```bash
# 自动生成迁移文件
alembic revision --autogenerate -m "描述你的修改"

# 查看将要执行的迁移
alembic upgrade --sql head

# 应用迁移（应用启动时会自动执行，也可手动执行）
alembic upgrade head
```

## 故障排查

### 数据库初始化失败

1. 检查 `.env` 文件是否存在且配置正确
2. 检查 `storage/` 目录权限
3. 查看日志输出的详细错误信息

### 默认数据未插入

- 数据只会在首次启动时插入
- 如需重新插入，删除 `content_ratings` 表中的数据后重启

### 生产模式迁移失败

1. 检查 `alembic/versions/` 目录是否有迁移文件
2. 查看 `storage/backups/` 中的备份文件
3. 如需回滚，手动运行 `alembic downgrade -1`
