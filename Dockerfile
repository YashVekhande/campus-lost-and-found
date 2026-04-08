# ---- STAGE 1: The Kitchen (Building the App) ----
FROM node:22-alpine AS builder

# Create a working folder inside the container
WORKDIR /app

# Copy your package files first (helps with caching)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy all the rest of your React code into the container
COPY . .

# Build the final, optimized version of your site
RUN npm run build


# ---- STAGE 2: The Display Case (Serving the App) ----
FROM nginx:alpine

# Take the finished website from "The Kitchen" and put it in the web server
COPY --from=builder /app/dist /usr/share/nginx/html

# Open port 80 so the internet can see it
EXPOSE 80

# Turn the web server on
CMD ["nginx", "-g", "daemon off;"]