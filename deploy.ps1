# Stop execution if any command fails
$ErrorActionPreference = "Stop"

# Set Variables
$ServerUser = "user"
$ServerIP = "your-windows-server-ip"
$ServerPath = "C:\Deployment\"

Write-Output "Starting deployment process..."

# === STEP 1: BUILD BACKEND ===
Write-Output "Building the backend..."
& ".\build_backend.ps1"

# === STEP 2: BUILD FRONTEND ===
Write-Output "Building the frontend..."
Set-Location -Path "frontend"
npm install
npm run build

Write-Output "Building frontend Docker image..."
docker build -t my_frontend .

Write-Output "Saving frontend Docker image..."
docker save my_frontend | gzip > my_frontend.tar.gz

# Verify frontend image is saved
if (-not (Test-Path "my_frontend.tar.gz")) {
    Write-Output "Frontend Docker image save failed!"
    exit 1
}
Set-Location -Path ".."

# === STEP 3: TRANSFER IMAGES TO SERVER ===
Write-Output "Transferring images to the server..."
scp my_api.tar.gz my_frontend.tar.gz "$ServerUser@$ServerIP:$ServerPath"

# === STEP 4: DEPLOY ON WINDOWS SERVER ===
Write-Output "Deploying containers on Windows Server..."
ssh "$ServerUser@$ServerIP" << 'EOF'
cd C:\Deployment\

# Load Docker Images
Write-Output "Loading backend image..."
docker load < my_api.tar.gz
docker tag my_api my_api:latest

Write-Output "Loading frontend image..."
docker load < my_frontend.tar.gz
docker tag my_frontend my_frontend:latest

# Restart Backend (LAN-Only)
Write-Output "Restarting backend..."
docker stop my_api || true
docker rm my_api || true
docker network create my_lan -d bridge || true
docker run -d --name my_api --network my_lan --restart always -p 192.168.1.100:8000:8000 my_api

# Restart Frontend (Public)
Write-Output "Restarting frontend..."
docker stop my_frontend || true
docker rm my_frontend || true
docker run -d --name my_frontend -p 80:80 my_frontend
EOF

Write-Output "Deployment Complete!"
