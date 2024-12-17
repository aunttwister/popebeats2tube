# Define the base directory for the project (change as needed)
$baseDir = "C:\Users\pavle\Documents\Hobby\MyProjects\Soundframe\backend"

# Define the folder structure
$folders = @(
    "$baseDir/app/auth",
    "$baseDir/app/controllers",
    "$baseDir/app/services",
    "$baseDir/app/models",
    "$baseDir/app/utils",
    "$baseDir/tests"
)

# Define the files to be created
$files = @(
    "$baseDir/app/main.py",
    "$baseDir/requirements.txt",
    "$baseDir/Dockerfile",
    "$baseDir/README.md"
)

# Create the folders
foreach ($folder in $folders) {
    if (!(Test-Path -Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Output "Created folder: $folder"
    } else {
        Write-Output "Folder already exists: $folder"
    }
}

# Create the files
foreach ($file in $files) {
    if (!(Test-Path -Path $file)) {
        New-Item -ItemType File -Path $file -Force | Out-Null
        Write-Output "Created file: $file"
    } else {
        Write-Output "File already exists: $file"
    }
}

Write-Output "Folder structure created successfully."
