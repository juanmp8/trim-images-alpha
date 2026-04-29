@echo off
echo ================================================
echo  Trim Images PNG - Gerando executavel (.exe)
echo ================================================
echo.

echo [1/3] Instalando dependencias...
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install pyinstaller
echo.

echo [2/3] Compilando com PyInstaller...
.venv\Scripts\python.exe -m PyInstaller ^
  --onefile ^
  --windowed ^
  --name "TrimImages" ^
  --collect-all customtkinter ^
  app.py
echo.

echo [3/3] Verificando resultado...
if exist "dist\TrimImages.exe" (
    echo  Sucesso! Executavel criado em: dist\TrimImages.exe
) else (
    echo  ERRO: Executavel nao foi gerado. Verifique as mensagens acima.
    exit /b 1
)

echo.
pause
