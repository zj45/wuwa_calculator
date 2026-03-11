# 鸣潮伤害计算器

一个基于 Python FastAPI 后端的鸣潮游戏伤害计算器。

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
python main.py
```

或者使用 uvicorn 直接启动：

```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

服务将在 `http://localhost:5000` 启动

### 3. 访问应用

在浏览器中打开 `http://localhost:5000`

### 4. API 文档

FastAPI 自动生成的 API 文档：
- Swagger UI: `http://localhost:5000/docs`
- ReDoc: `http://localhost:5000/redoc`

## 功能特性

- 完整的角色面板配置（自身面板、武器面板、声骸面板）
- 敌人面板配置
- 场地Buff配置（包含守岸人选项）
- 技能管理（支持多种技能类型，声骸技能标记）
- 技能搭配和释放次数设置
- 伤害计算（后端 Python FastAPI 实现）
- 从 encore.moe 自动获取角色和武器数据
- CSV 导出功能
- 计算过程展开查看
- 自动 API 文档

## 项目结构

```
wuwa_calculator/
├── main.py           # FastAPI 主模块
├── models.py          # 数据建模模块
├── calculator.py       # 计算逻辑模块
├── api_client.py      # API 数据获取模块
├── app.js             # 前端逻辑
├── style.css          # 样式文件
├── index.html         # 主页面
├── requirements.txt   # Python 依赖
└── README.md          # 说明文档
```

### 模块说明

- **main.py**: FastAPI 应用主入口，API 路由定义
- **models.py**: 所有 Pydantic 数据模型定义
- **calculator.py**: 伤害计算核心逻辑
- **api_client.py**: 外部 API 数据获取（encore.moe）
