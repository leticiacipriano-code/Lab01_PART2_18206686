#!/bin/bash

# Script de utilidade para gerenciar Docker containers
# Use: chmod +x docker_commands.sh && ./docker_commands.sh [comando]

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

show_usage() {
    echo -e "${YELLOW}======================================${NC}"
    echo -e "${YELLOW} Fertility DataWarehouse - Docker CLI${NC}"
    echo -e "${YELLOW}======================================${NC}"
    echo
    echo "Uso: $0 [comando]"
    echo
    echo "Comandos disponíveis:"
    echo "  up        - Subir containers"
    echo "  down      - Parar containers"
    echo "  logs      - Ver logs da aplicação"
    echo "  status    - Verificar status dos containers"
    echo "  db        - Acessar console PostgreSQL"
    echo "  build     - Rebuild das imagens"
    echo "  clean     - Remover tudo (CUIDADO!)"
    echo "  help      - Este menu"
    echo
}

case "$1" in
    up)
        echo -e "${GREEN}[*] Subindo containers...${NC}"
        docker-compose up -d
        sleep 3
        echo -e "${GREEN}[OK] Containers em execuçao!${NC}"
        docker-compose ps
        ;;
    down)
        echo -e "${GREEN}[*] Parando containers...${NC}"
        docker-compose stop
        echo -e "${GREEN}[OK] Containers parados!${NC}"
        ;;
    logs)
        echo -e "${GREEN}[*] Mostrando logs da aplicação (Ctrl+C para sair)...${NC}"
        docker-compose logs -f app
        ;;
    status)
        echo
        docker-compose ps
        ;;
    db)
        echo -e "${GREEN}[*] Acessando PostgreSQL...${NC}"
        docker-compose exec postgres psql -U postgres -d fertility_db
        ;;
    build)
        echo -e "${GREEN}[*] Reconstruindo imagens...${NC}"
        docker-compose up -d --build
        echo -e "${GREEN}[OK] Imagens reconstruídas!${NC}"
        docker-compose ps
        ;;
    clean)
        echo -e "${RED}[!] AVISO: Isso vai remover TUDO incluindo dados!${NC}"
        read -p "Tem certeza? (s/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            echo -e "${GREEN}[*] Removendo containers e volumes...${NC}"
            docker-compose down -v
            echo -e "${GREEN}[OK] Tudo removido!${NC}"
        else
            echo -e "${YELLOW}[X] Operação cancelada${NC}"
        fi
        ;;
    help| -h | --help | "")
        show_usage
        ;;
    *)
        echo -e "${RED}Comando desconhecido: $1${NC}"
        show_usage
        exit 1
        ;;
esac
