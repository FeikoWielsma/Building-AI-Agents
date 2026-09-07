# start-jupyter.ps1 — load .env into the environment, then launch JupyterLab.
# Loading .env process-wide means every notebook works even if it doesn't call
# load_dotenv() itself (a few of the course notebooks don't).
$root = $PSScriptRoot
Get-Content "$root\.env" | Where-Object { $_ -match '^\s*[^#].*=' } | ForEach-Object {
    $k, $v = $_ -split '=', 2
    Set-Item -Path "Env:$($k.Trim())" -Value $v.Trim()
}
Write-Host "Loaded .env -> OPENAI_BASE_URL=$($env:OPENAI_BASE_URL)" -ForegroundColor Cyan
& "$root\..\.venv\Scripts\jupyter.exe" lab
