import ipaddress
from app.controllers.log_app import log_app as log


def endereco_ip(end_ip):
    try:
        ipaddress.ip_address(end_ip)
        log(f' endereco_ip - Endereço IP {end_ip} validado com sucesso.', 'info')
        return True
    except ValueError:
        log(f' endereco_ip - Endereço IP {end_ip} inválido. \nMotivo: ', 'exc')
        return False
    except Exception:
        log(f' endereco_ip - Falha catastrófica ao validar o endereço IP. \nMotivo: ', 'exc')
        return False
