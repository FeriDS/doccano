#!/usr/bin/env bash
#===================================================================
# Script para parar e iniciar o serviço PostgreSQL
#===================================================================
# Uso:
#   ./manage_postgres.sh stop   -> Para o serviço PostgreSQL
#   ./manage_postgres.sh start  -> Inicia o serviço PostgreSQL
#   ./manage_postgres.sh restart-> Reinicia o serviço PostgreSQL
#===================================================================

# Função para exibir ajuda
usage() {
    echo "Uso: $0 {stop|start|restart}" 1>&2
    exit 1
}

# Verifica se foi passado um parâmetro
if [ $# -ne 1 ]; then
    usage
fi

# Nome do serviço PostgreSQL (pode variar conforme a distribuição)
SERVICE_NAME="postgresql"

# Detecta gerenciador de serviço
if command -v systemctl > /dev/null; then
    CMD="systemctl"
elif command -v service > /dev/null; then
    CMD="service"
else
    echo "Nenhum gerenciador de serviços compatível encontrado (systemctl ou service)." >&2
    exit 1
fi

# Executa ação
case "$1" in
    stop)
        echo "Parando o serviço $SERVICE_NAME..."
        sudo $CMD stop $SERVICE_NAME
        ;;
    start)
        echo "Iniciando o serviço $SERVICE_NAME..."
        sudo $CMD start $SERVICE_NAME
        ;;
    restart)
        echo "Reiniciando o serviço $SERVICE_NAME..."
        sudo $CMD restart $SERVICE_NAME
        ;;
    *)
        usage
        ;;
esac

# Verifica status
echo "Status atual do serviço $SERVICE_NAME:"
sudo $CMD status $SERVICE_NAME
