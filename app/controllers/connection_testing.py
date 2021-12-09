from pythonping import ping
from threading import Thread
from queue import Queue
from app.models.banco_dados import Equipamento
from app import db
from app.controllers.log_app import log_app as log


num_threads = 5
ips_queue = Queue()
saida_queue = Queue()


def thread_ping(i, q):
    while True:
        ip = q.get()
        rping = ping(ip, count=1)
        if "timed out" in str(rping._responses[0]):
            Equipamento.query.filter_by(endereco_ip=ip).update(dict(atividade=0))
            db.session.commit()
            log(f' thread_ping - Teste de ICMP ping executado ao Endereço IP {ip} não respondeu. Terminal inativo.',
                'info')
            saida_queue.put(f"OK {ip} commitado com 0")
        else:
            Equipamento.query.filter_by(endereco_ip=ip).update(dict(atividade=1))
            db.session.commit()
            log(f' thread_ping - Teste de ICMP ping executado ao Endereço IP {ip} respondeu com sucesso. Terminal ativo.',
                'info')
            saida_queue.put(f"OK {ip} commitado com 1")
        q.task_done()


def teste_ping(bd):
    ips = []
    for i in bd:
        ips.append(i.endereco_ip)

    log(f' teste_ping - Lista dos Endereços IP a serem testados: {ips}', 'info')

    for i in range(num_threads):
        worker = Thread(target=thread_ping, args=(i, ips_queue))
        worker.setDaemon(True)
        worker.start()

    for ip in ips:
        ips_queue.put(ip)

    ips_queue.join()


def teste_ping_log_terminal(end_ip):
    """
    Função ira fazer teste de ICMP ping para o endereço IP informado como parametro
    :param end_ip: endereço ip do terminal
    :return: Validação de saida ping
    """
    rping = ping(end_ip, count=1)
    if "timed out" in str(rping._responses[0]):
        log(f' teste_ping_log_terminal - Teste de ICMP ping executado ao Endereço IP {end_ip} não respondeu.'
            f' Terminal inativo.', 'info')
        return False
    else:
        log(f' teste_ping_log_terminal - Teste de ICMP ping executado ao Endereço IP {end_ip} respondeu com sucesso.'
            f' Terminal ativo.', 'info')
        return True
