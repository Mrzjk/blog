# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# 复制 package.json 和 lock 文件
COPY package*.json ./

# 设置 npm 镜像源并安装依赖
RUN npm config set registry https://registry.npmmirror.com/ && npm install

# 复制项目所有文件
COPY . .

# 执行构建
RUN npm run build

# Production stage
FROM nginx:alpine

# 复制构建产物到 Nginx 目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 Nginx 配置文件 (如果在项目中创建了自定义的 nginx.conf，可以取消下面这行的注释)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露 80 端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]