FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm install

# Copy the rest of the application
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
