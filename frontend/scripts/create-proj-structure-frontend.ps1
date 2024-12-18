# Define the folder structure to create
$folderStructure = @(
    "main.py",                # Your main script
    "static",                 # Folder for static assets like images, CSS, JS
    "static\images",          # Sub-folder for images
    "static\css",             # Sub-folder for CSS files
    "static\js",              # Sub-folder for JS files
    "templates",              # Folder for HTML templates
    "logs",                   # Folder for logs
    "config",                 # Folder for configuration files
    "config\settings.json",   # A settings JSON file in the config folder
    "models",                 # Folder for models
    "controllers",            # Folder for controllers
    "tests",                  # Folder for tests
    "tests\unit",             # Sub-folder for unit tests
    "tests\integration"       # Sub-folder for integration tests
)

# Loop through the folder structure and create each folder/file
foreach ($path in $folderStructure) {
    $fullPath = Join-Path -Path (Get-Location) -ChildPath $path
    if ($path -match '\.$') {
        # Skip if the path is just a dot (current directory)
        continue
    }
    if (-not (Test-Path $fullPath)) {
        if ($path -match '\.py$|\.json$') {
            # Create empty files for .py and .json
            New-Item -Path $fullPath -ItemType File -Force
            Write-Host "Created file: $fullPath"
        } else {
            # Create folders
            New-Item -Path $fullPath -ItemType Directory -Force
            Write-Host "Created folder: $fullPath"
        }
    }
}
