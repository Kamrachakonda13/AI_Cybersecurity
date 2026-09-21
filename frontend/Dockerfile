# VEYRA console image: Node 22 + Vite dev server on :3000 (strictPort).
# Help: `VITE_API_URL` points at the backend. Rebuild after src changes.
FROM node:22-alpine
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
CMD ["npm","run","dev"]
