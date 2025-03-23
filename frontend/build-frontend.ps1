# Define CLI parameters (Must be at the top of the script)
param (
    [string]$output_dir = ".",
    [string]$dockerfile_dir = "frontend"
)
# Stop execution if any command fails
$ErrorActionPreference = "Stop"

# Ensure frontend directory exists
if (-not (Test-Path $dockerfile_dir)) {
    Write-Output "Error: Frontend directory '$dockerfile_dir' not found!"
    exit 1
}

# Ensure output directory exists
if (-not (Test-Path $output_dir)) {
    New-Item -ItemType Directory -Path $output_dir | Out-Null
}

# Build the frontend application
Write-Output "Building frontend application from '$dockerfile_dir'..."
if (-not (Test-Path "$dockerfile_dir/package.json")) {
    Write-Output "Error: package.json not found in '$dockerfile_dir'!"
    exit 1
}

Push-Location $dockerfile_dir
npm install
npm run build
Pop-Location

# Build the frontend Docker image
Write-Output "Building Docker image for frontend..."
docker build -t my_frontend $dockerfile_dir

# Verify the image was built successfully
if (-not (docker images -q my_frontend)) {
    Write-Output "Docker image 'my_frontend' build failed!"
    exit 1
}

Write-Output "Docker image 'my_frontend' built successfully."

# Define output file paths
$tar_file = Join-Path -Path $output_dir -ChildPath "my_frontend.tar"
$gzip_file = Join-Path -Path $output_dir -ChildPath "my_frontend.tar.gz"

# Save the Docker image
Write-Output "Saving Docker image to '$tar_file'..."
docker save -o $tar_file my_frontend

# Verify the .tar file was created
if (-not (Test-Path $tar_file)) {
    Write-Output "Failed to save Docker image!"
    exit 1
}

# Compress the Docker image using tar
Write-Output "Compressing Docker image..."
tar -czvf $gzip_file -C $output_dir my_frontend.tar

# Verify the compressed file was created
if (-not (Test-Path $gzip_file)) {
    Write-Output "Failed to compress Docker image!"
    exit 1
}

# Remove the uncompressed .tar file to save space
Write-Output "Cleaning up temporary files..."
Remove-Item -Path $tar_file -Force

Write-Output "Build and save process completed successfully! Output saved to: $gzip_file"