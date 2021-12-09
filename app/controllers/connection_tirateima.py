import datetime
from pythonping import ping
from sqlalchemy.sql import select
from sqlalchemy import MetaData, Table, create_engine, desc, or_
from sqlalchemy.exc import OperationalError
from threading import Thread
from queue import Queue
from app.models.banco_dados import Equipamento
from app.controllers.log_app import log_app as log

num_threads = 5
ips_queue = Queue()
finalizador_queue = object()


def dados_leitor(i, dict_dados, ips_queue):
    """
    Função executa a thread enviada pela queue para ser executada
    :param i: thread
    :param dict_dados: dicionario contendo os dados de leitura de cada terminal
    :param ips_queue: queue
    :return:
    """
    while True:
        item = ips_queue.get()
        print(item)
        if item is finalizador_queue:
            ips_queue.task_done()
            break
        else:
            rping = ping(item.endereco_ip, count=1)
            if "timed out" in str(rping._responses[0]):
                print('falha ao pingar')
                sem_conexao = [(1, "Terminal Sem Conexão", datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"))]
                dict_dados[item.equipamento] = sem_conexao
            else:
                print('pingou')
                dict_dados[item.equipamento] = dados_lidos(item.endereco_ip, item.tipo_equipamento)
                print(dict_dados)
            ips_queue.task_done()


def queue_leitor():
    """
    Função irá executar,por meio de queue, as threads da operaçao de consulta dos dados de leitura dos eans nos terminais
    :return:
    """
    try:
        obj_equip = []
        dict_dados = {}
        for i in Equipamento.query.order_by('equipamento').filter(or_(Equipamento.modo_operacao == 1, Equipamento.modo_operacao == 3)):
            obj_equip.append(i)

        for i in range(num_threads):
            worker = Thread(target=dados_leitor, args=(i, dict_dados, ips_queue))
            worker.setDaemon(True)
            worker.start()

        for i in obj_equip:
            ips_queue.put(i)

        for i in range(num_threads):
            ips_queue.put(finalizador_queue)

        ips_queue.join()

        log(' queue_leitor - Execução realizada com sucesso.', 'info')
        return dict_dados
    except Exception:
        log(' queue_leitor - Falha na execução.\n Motivo: ', 'exc')
        return "Falha"


def dados_lidos(ip, tipo_equipamento):
    """
    Função irá ler os dados enviados pelo terminal.
    :param ip:endereço ip do terminal
    :return:
    """
    # Conectar ao banco de dados
    try:
        user = 'tirateima'
        passwd = '#Pr0c3Ss4**Ml'
        bd = 'tirateimaml'
        # conexão com o banco de dados do terminal 1(se computador) 2 (se raspberry)
        if tipo_equipamento == 1:
            engine = create_engine(f'mysql+mysqldb://{user}:{passwd}@{ip}/{bd}')
        else:
            engine = create_engine(f'mariadb+mariadbconnector://{user}:{passwd}@{ip}/{bd}')
        meta = MetaData(engine)
        tb_leitor = Table('leitor', meta, autoload=True, autoload_with=engine)
        conn = engine.connect()
        s = select([tb_leitor]).order_by(desc(tb_leitor.c.id)).limit(5)
        result = conn.execute(s)
        retorno = result.fetchall()
        conn.close()
        return retorno
    except UnboundLocalError:
        log(f' dados_lidos - Falha na conexão com o terminal.\n Motivo: ', 'exc')
    except OperationalError:
        log(f' dados_lidos - Falha na operação de busca dos dados.\n Motivo: ', 'exc')
    except Exception:
        log(f' dados_lidos - Falha castrófica.\n Motivo: ', 'exc')
