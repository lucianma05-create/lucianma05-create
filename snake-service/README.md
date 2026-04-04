# GitHub Contribution Snake Service

这是一个基于 GitHub 贡献日历页面的实时转换服务，将 GitHub 贡献数据渲染成“蛇形”风格的 SVG 图。

## 快速启动

1. 安装依赖

```bash
python -m pip install -r requirements.txt
```

2. 运行服务

```bash
python app.py
```

3. 访问服务

- 浏览器访问: `http://127.0.0.1:5000/`
- 真实 SVG: `http://127.0.0.1:5000/snake/lucianma05-create`

## 用法示例

在 README 中嵌入实时图像：

```md
![GitHub Contributions](https://your-domain.com/snake/lucianma05-create)
```

如果你在本地测试，可直接打开上面的 URL。部署后即可让它成为你 README 的实时贡献图服务。

## 本地部署

```bash
python -m pip install -r requirements.txt
python app.py
```

服务默认监听：`http://127.0.0.1:5000`

## Docker 部署

```bash
docker build -t github-snake-service .
docker run -p 5000:5000 github-snake-service
```

## 云部署

你可以直接将 `snake-service` 目录部署到支持 Docker 或 Python 的云平台，例如：

- Railway
- Heroku
- Fly.io
- Vercel (使用 Serverless / Docker)

如果使用 Heroku / Railway，`Procfile` 已经准备好，服务会读取 `PORT` 环境变量。

## 原理说明

- 服务实时请求 GitHub 用户 `contributions` 页面
- 解析表格中的 `data-date` 和 `data-level`
- 按日期生成贡献格子，并绘制一条蛇形路径
- 返回 SVG 格式结果，支持直接在 README 中引用
