# GameVault 数据库管理 - 用户指南

## 概述

GameVault 使用自动化的数据库迁移系统，**无需手动操作**。当您启动服务器时，系统会自动：

1. ✅ 检查数据库是否需要更新
2. ✅ 自动备份现有数据库
3. ✅ 应用最新的数据库结构
4. ✅ 保留您的所有数据

---

## 🎯 普通用户（99% 的情况）

### 只需要做这些：

```bash
# 1. 激活环境
conda activate game-vault

# 2. 启动服务器
cd server
uvicorn app.main:app --reload
```

**就这么简单！** 数据库会自动更新，您无需任何其他操作。

---

## 📁 自动备份

每次数据库更新时，系统会自动创建备份文件：

```
storage/
├── gamevault.db              # 当前数据库
└── backups/                  # 自动备份目录
    ├── gamevault_20251128_143022.db
    ├── gamevault_20251128_150315.db
    └── gamevault_20251129_091245.db
```

- 系统自动保留最近 10 个备份
- 旧备份会被自动清理
- 文件名包含日期和时间，方便识别

---

## 🔧 开发者（需要修改数据库结构时）

### 修改数据库表结构的流程

#### 1. 修改 Model 文件

例如，为 `Game` 添加新字段：

```python
# server/app/models/game.py

class Game(Base):
    __tablename__ = "games"
    
    # ...现有字段...
    
    # 新增字段
    genre = Column(String(100), nullable=True)
```

#### 2. 生成迁移脚本

```bash
cd server
conda activate game-vault
alembic revision --autogenerate -m "Add genre to games"
```

#### 3. 提交代码

```bash
git add app/models/ alembic/versions/
git commit -m "feat: Add genre field to games"
```

#### 4. 完成

下次启动服务器时，数据库会自动更新！

---

## ⚠️ 故障恢复

### 如果数据库更新失败

1. **查看日志**：启动日志会显示错误信息
2. **恢复备份**：
   ```bash
   # 停止服务器
   # 复制最新的备份文件
   cp storage/backups/gamevault_YYYYMMDD_HHMMSS.db storage/gamevault.db
   # 重新启动服务器
   ```

### 如果需要回滚数据库

```bash
cd server
conda activate game-vault

# 回滚一个版本
alembic downgrade -1

# 或者恢复备份文件
cp storage/backups/gamevault_20251128_143022.db storage/gamevault.db
```

---

## 📊 查看数据库状态（可选）

```bash
cd server
conda activate game-vault

# 查看当前数据库版本
alembic current

# 查看迁移历史
alembic history

# 查看是否有待应用的更新
alembic heads
```

---

## 🎓 技术细节（高级用户）

### 工作原理

1. **启动检查**：应用启动时，`MigrationManager` 检查数据库版本
2. **自动备份**：如果需要更新，先创建备份
3. **应用迁移**：执行 Alembic 迁移脚本
4. **清理备份**：保留最近 10 个备份，删除旧备份

### 配置文件

- `alembic.ini` - Alembic 配置
- `alembic/env.py` - 迁移环境配置
- `app/core/migration.py` - 自动迁移管理器

### 禁用自动迁移（不推荐）

如果确实需要手动控制，可以修改 `app/main.py`：

```python
@app.on_event("startup")
async def startup_event():
    # 注释掉自动迁移
    # success = auto_migrate(backup=True)
    pass
```

---

## 📞 常见问题

### Q: 我的数据会丢失吗？
A: 不会。系统每次更新前都会自动备份，并且 Alembic 的迁移是非破坏性的。

### Q: 备份文件可以删除吗？
A: 可以。系统自动保留最近 10 个，您也可以手动删除更旧的备份。

### Q: 如何查看备份？
A: 备份文件是标准的 SQLite 数据库，可以用任何 SQLite 工具打开。

### Q: 多久备份一次？
A: 只在数据库结构需要更新时才备份，不是定期备份。

### Q: 团队协作时如何同步数据库？
A: 拉取最新代码后，重启服务器即可。系统会自动应用新的迁移。

---

## 🔗 相关资源

- **开发者详细文档**：`DATABASE_MIGRATION.md`（如需深入了解 Alembic）
- **项目配置**：`alembic.ini`
- **迁移脚本**：`alembic/versions/`

---

**提示**：对于 99% 的用户，您只需要启动服务器。数据库管理完全自动化！

**最后更新**：2025-11-28
