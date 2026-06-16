$ErrorActionPreference = "Stop"
$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 프로젝트 루트 경로 확보
if ($MyInvocation.MyCommand.Path) {
    $CurrentDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
    Set-Location $CurrentDir
}

$App = "TOKIMEKI BOARD"
$RootPath = Get-Location

# 이전 빌드 아티팩트 정리
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path build | Out-Null

# 의존성 설치 및 테스트
pip install -e .
# python -m unittest discover -s tests -p "test_*.py"

# 경로 절대 경로화 (PyInstaller 경로 꼬임 방지)
$AssetsSourcePath = Join-Path $RootPath "assets"
$IconIcoPath = Join-Path $RootPath "build\icon.ico"

# PyInstaller 기본 인자 설정
$PyArgs = @(
    "--noconfirm",
    "--clean",
    "--onefile",
    "--specpath", "build\spec",
    "--workpath", "build\work",
    "--distpath", "dist",
    "--noconsole",
    "--name", $App,
    "--add-data", "$($AssetsSourcePath);assets",
    "--add-data", "$($RootPath)\version.json;."
)

# 아이콘 처리
if (Test-Path "assets\icon.png") {
    Write-Host "Converting icon.png to icon.ico..."
    # 아이콘 생성을 위한 Pillow 실행
    python -c "from PIL import Image; Image.open('assets/icon.png').save(r'$IconIcoPath', format='ICO', sizes=[(16,16),(32,32),(48,48),(256,256)])"

    # 아이콘 경로를 절대 경로($IconIcoPath)로 전달
    $PyArgs += "--icon", "$IconIcoPath"
}

# 최종 빌드 실행
$PyArgs += "main.py"
Write-Host "Running PyInstaller..."
python -m PyInstaller @PyArgs

Write-Host "Build success!"
