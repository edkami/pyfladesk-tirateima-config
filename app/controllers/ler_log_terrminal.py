from app.controllers.connection_testing import teste_ping_log_terminal as teste_ping


def conecta_terminal(end_ip):
    try:
       if teste_ping(end_ip):
            file = f'\\\\{end_ip}\\Compartilhamento\\tira-teima.log'
            with open(file, mode='r', encoding='utf-8') as f:
                texto = f.readlines()
            return texto
       else:
           return "Falha na comunicação de rede. Valide e tente novamente."
    except Exception as exc:
        return f"Falha na busca do log de operação do terminal.<p> Motivo: {exc}"
