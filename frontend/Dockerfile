FROM node:18-alpine AS base

# 1. Install dependencies only when needed
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

# 2. Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# This argument will be passed during the build to bake in the backend URL
ARG NEXT_PUBLIC_API_URL=https://productcheck-backend-896719746400.us-central1.run.app
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

RUN npm run build

# 3. Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000

# Automatically leverage output traces to reduce image size
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]