FROM node:20-slim
WORKDIR /app
COPY package.json pnpm-lock.yaml* ./
RUN npm i -g pnpm && pnpm install
COPY tsconfig.json ./
COPY prisma ./prisma
RUN npx prisma generate
COPY src ./src
RUN pnpm run build
EXPOSE 3001
ENV NODE_ENV=production
CMD ["node","dist/index.js"]