# Projspec Builder 起動スクリプト (PowerShell)
# プロジェクトルートから実行してください: .\scripts\start.ps1

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Set-Location $ProjectRoot
python main.py
