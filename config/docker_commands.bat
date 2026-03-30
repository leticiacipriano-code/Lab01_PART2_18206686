@echo off
REM Script de utilidade para gerenciar Docker containers
REM MacOS e Linux: renomeie esse arquivo para Makefile

echo.
echo ========================================
echo  Fertility DataWarehouse - Docker CLI
echo ========================================
echo.

IF "%1"=="" goto :usage
IF "%1"=="up" goto :up
IF "%1"=="down" goto :down
IF "%1"=="logs" goto :logs
IF "%1"=="status" goto :status
IF "%1"=="db" goto :db
IF "%1"=="build" goto :build
IF "%1"=="clean" goto :clean
IF "%1"=="help" goto :help

:usage
echo Uso: docker_commands.bat [comando]
echo.
echo Comandos disponíveis:
echo   up        - Subir containers
echo   down      - Parar containers
echo   logs      - Ver logs da aplicação
echo   status    - Verificar status dos containers
echo   db        - Acessar console PostgreSQL
echo   build     - Rebuild das imagens
echo   clean     - Remover tudo (CUIDADO!)
echo   help      - Este menu
echo.
goto :end

:up
echo.
echo [*] Subindo containers...
docker-compose up -d
timeout /t 3 /nobreak
echo [OK] Containers em execução!
docker-compose ps
goto :end

:down
echo.
echo [*] Parando containers...
docker-compose stop
echo [OK] Containers parados!
goto :end

:logs
echo.
echo [*] Mostrando logs da aplicação (pressione Ctrl+C para sair)...
docker-compose logs -f app
goto :end

:status
echo.
docker-compose ps
goto :end

:db
echo.
echo [*] Acessando PostgreSQL...
docker-compose exec postgres psql -U postgres -d fertility_db
goto :end

:build
echo.
echo [*] Reconstruindo imagens...
docker-compose up -d --build
echo [OK] Imagens reconstruídas!
docker-compose ps
goto :end

:clean
echo.
echo [!] AVISO: Isso vai remover TUDO incluindo dados!
set /p confirm="Tem certeza? (S/N): "
if /i "%confirm%"=="S" (
    echo [*] Removendo containers e volumes...
    docker-compose down -v
    echo [OK] Tudo removido!
) else (
    echo [X] Operação cancelada
)
goto :end

:help
goto :usage

:end
echo.
