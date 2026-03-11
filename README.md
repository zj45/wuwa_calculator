# 鸣潮伤害计算器

一个基于 Python FastAPI 后端的鸣潮游戏伤害计算器。

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
python backend.py
```

或者使用 uvicorn 直接启动：

```bash
uvicorn backend:app --host 0.0.0.0 --port 5000 --reload
```

服务将在 `http://localhost:5000` 启动

### 3. 访问应用

在浏览器中打开 `http://localhost:5000`

### 4. API 文档

FastAPI 自动生成的 API 文档：
- Swagger UI: `http://localhost:5000/docs`
- ReDoc: `http://localhost:5000/redoc`

## 功能特性

- 完整的角色面板配置（普攻、重击、共鸣技能、共鸣解放4种伤害加成）
- 敌人面板配置
- 场地Buff配置
- 技能管理（支持多种技能类型，声骸技能标记）
- 技能搭配和释放次数设置
- 伤害计算（后端 Python FastAPI 实现）
- CSV 导出功能
- 自动 API 文档

## 项目结构

```
wuwa_calculator/
├── backend.py          # FastAPI 后端服务
├── app.js             # 前端逻辑
├── style.css          # 样式文件
├── index.html         # 主页面
├── requirements.txt   # Python 依赖
└── README.md          # 说明文档
```
