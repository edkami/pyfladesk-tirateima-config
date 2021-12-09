from app.controllers.connection_testing import teste_ping_log_terminal as teste_ping
from app.controllers.log_app import log_app as log


def conecta_terminal(end_ip):
    try:
        if teste_ping(end_ip):
            file = f'\\\\{end_ip}\\Compartilhamento\\tira-teima.log'
            with open(file, mode='r', encoding='utf-8') as f:
                texto = f.readlines()
            log(' conecta_terminal - Log carregado com sucesso.', 'info')
            return texto
        else:
            log('conecta_terminal - Falha ao buscar os dados do log. \nMotivo: Terminal sem conexão.', 'error')
            return "Falha na comunicação de rede. Valide e tente novamente."
    except Exception as exc:
        log('conecta_terminal - Falha catastrófica ao buscar os dados do log. \nMotivo: ', 'exc')
        return f"Falha na busca do log de operação do terminal.<p> Motivo: {exc}"
