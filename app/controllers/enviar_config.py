import datetime
import os
import ntpath
import shutil
from pythonping import ping
from app.controllers.conexao_ssh import exec_reboot_pdv, permissao_imagens
from app.models.banco_dados import Equipamento, Configuracao, Temporizador, Server
from threading import Thread
from queue import Queue
from app import db
from sqlalchemy.sql import select
from sqlalchemy import MetaData, Table, create_engine
from app.controllers.log_app import log_app as log

# Propriedade da Queue
num_threads = 5
queue = Queue()
finalizador_queue = object()

# Caminho dos arquivos
dir_ce = os.path.join('D:\\dev\\tira-teima-config\\app\\static\\client-img-folder\\', 'central')
dir_fs = os.path.join('D:\\dev\\tira-teima-config\\app\\static\\client-img-folder\\', 'fullscreen')
dir_lg = os.path.join('D:\\dev\\tira-teima-config\\app\\static\\client-img-folder\\', 'logo')

# Criação da conexão
user = 'tirateima'
passwd = '#Pr0c3Ss4**Ml'
bd = 'tirateimaml'


def config_servidor(terminal):
    """
    Função irá executar insert/update na tabela conexão do terminal.
    :param terminal: objeto equipamento
    :return:
    """
    try:
        query = Server.query.filter_by(id=terminal.servidor).all()
        dados = query[0]
        if terminal.tipo_equipamento == 1:
            # conexão com o banco de dados do terminal pc
            engine = create_engine(f'mysql+mysqldb://{user}:{passwd}@{terminal.endereco_ip}/{bd}')
            log(f' config_servidor - Montando engine para terminal {terminal.equipamento} (PC)', 'info')
        else:
            # conexão com banco de daados do terminal raspberry
            engine = create_engine(f"mariadb+mariadbconnector://{user}:{passwd}@{terminal.endereco_ip}/{bd}")
            log(f' config_servidor - Montando engine para terminal {terminal.equipamento} (Raspberry)', 'info')

        meta = MetaData(engine)
        tb_conexao = Table('conexao', meta, autoload=True, autoload_with=engine)
        conn = engine.connect()
        # Validação de insert ou update
        s = select([tb_conexao])
        result = conn.execute(s)
        retorno = result.fetchall()
        if not retorno:
            # Insert dados
            stmt = tb_conexao.insert().values({'tipo': dados.tipo,
                                               'end_ip': dados.endereco_ip,
                                               'passwd': dados.password})
            conn.execute(stmt)
            log(f' config_servidor - Inserido dados do Servidor no banco de dados do Terminal {terminal.equipamento}.',
                'info')
        else:
            # Update dados
            stmt = tb_conexao.update().values({'tipo': dados.tipo,
                                               'end_ip': dados.endereco_ip,
                                               'passwd': dados.password})
            conn.execute(stmt)
            log(f' config_servidor - Atualizado dados do Servidor no banco de dados do Terminal {terminal.equipamento}.'
                , 'info')
        conn.close()
    except Exception:
        log(f' config_servidor - Falha catastrófica ao fazer a inserção/atualização dos dados do '
            f'Servidor no Terminal {terminal.equipamento}. \nMotivo: ', 'exc')


def config_temporizador(terminal):
    """
    Função irá executar insert/update na tabela temporizador do terminal.
    :param terminal: objeto equipamento
    :return:
    """
    try:
        query = Temporizador.query.filter_by(id=terminal.temporizador).all()
        dados = query[0]
        if terminal.tipo_equipamento == 1:
            # conexão com o banco de dados do terminal pc
            engine = create_engine(f'mysql+mysqldb://{user}:{passwd}@{terminal.endereco_ip}/{bd}')
            log(f' config_temporizador - Montando engine para terminal {terminal.equipamento} (PC)', 'info')
        else:
            # conexão com banco de daados do terminal raspberry
            engine = create_engine(f"mariadb+mariadbconnector://{user}:{passwd}@{terminal.endereco_ip}/{bd}")
            log(f' config_temporizador -Montando engine para terminal {terminal.equipamento} (Raspberry)', 'info')

        meta = MetaData(engine)
        tb_temporizador = Table('temporizador', meta, autoload=True, autoload_with=engine)
        conn = engine.connect()
        # Validação de insert ou update
        s = select([tb_temporizador])
        result = conn.execute(s)
        retorno = result.fetchall()
        if not retorno:
            # Insert dados
            stmt = tb_temporizador.insert().values({'temp_nome': dados.temp_nome,
                                                    'pdt_ne': dados.pdt_ne,
                                                    'pdt_falha': dados.pdt_falha,
                                                    'pdt_sp': dados.pdt_sp,
                                                    'pdt_ep': dados.pdt_ep,
                                                    'pdt_uf': dados.pdt_uf,
                                                    'pdt_df': dados.pdt_df,
                                                    'scr_sav': dados.scr_sav})
            conn.execute(stmt)
            log(f' config_temporizador - Inserido dados do Temporizador no banco de dados do '
                f'Terminal {terminal.equipamento}.', 'info')
        else:
            # Update dados
            stmt = tb_temporizador.update().values({'temp_nome': dados.temp_nome,
                                                    'pdt_ne': dados.pdt_ne,
                                                    'pdt_falha': dados.pdt_falha,
                                                    'pdt_sp': dados.pdt_sp,
                                                    'pdt_ep': dados.pdt_ep,
                                                    'pdt_uf': dados.pdt_uf,
                                                    'pdt_df': dados.pdt_df,
                                                    'scr_sav': dados.scr_sav})
            conn.execute(stmt)
            log(f' config_temporizador - Atualizado dados do Temporizador no banco de dados do '
                f'Terminal {terminal.equipamento}.', 'info')
        conn.close()
    except Exception:
        log(f' config_temporizador - Falha catastrófica ao fazer a inserção/atualização dos dados do '
            f'Temporizador no Terminal {terminal.equipamento}. \nMotivo: ', 'exc')


def update_bd(terminal, info):
    """
    Função irá executar update na tabela configuracoes no banco de dados, afim de atualizar o campo de mensagem.
    :param terminal: objeto Equipamento
    :param info: string para ser atualizada no campo data_envio da tabela configuracoes
    :return:
    """
    try:
        Configuracao.query.filter_by(equipamento=terminal.id).update(dict(data_envio=info))
        db.session.commit()
        db.session.close()
        log(f' update_bd - Salvando informações no banco de dados da App para o terminal {terminal.equipamento}',
            'info')
    except Exception:
        log(f' update_bd - Falha catastrófica ao tentar salvar os dados no banco de dados da App .'
            f'\n Motivo: ', 'exc')


def envio_imagens_logo(terminal):
    """
    Função irá enviar o arquivo da pasta app/static/client-img-folder/logo para a pasta do terminal
    :param terminal: objeto equipamento
    :return:
    """
    try:
        destino = ntpath.join(r'\\', terminal.endereco_ip, 'Imagem_TiraTeima', 'logo')
        # Existe arquivos na pasta
        if len(os.listdir(destino)) > 0:
            log(f' envio_imagens_logo - Existe dados anteriores na pasta Logo do Terminal {terminal.equipamento}', 'info')
            # Apagar arquivos existentes
            for i in os.listdir(destino):
                os.remove(os.path.join(destino, i))
                log(f' envio_imagens_logo - Removendo dados da pasta Logo do Terminal {terminal.equipamento}', 'info')
            # Enviar novos arquivos
            for i in os.listdir(dir_lg):
                origem = os.path.join(dir_lg, i)
                shutil.copy(origem, destino)
                log(f' envio_imagens_logo - Enviando novos dados para pasta Logo do Terminal {terminal.equipamento}', 'info')
        else:
            # Enviar novos arquivos
            for i in os.listdir(dir_lg):
                origem = os.path.join(dir_lg, i)
                shutil.copy(origem, destino)
                log(f' envio_imagens_logo - Enviando novos dados para pasta Logo do Terminal {terminal.equipamento}', 'info')
    except Exception:
        log(f' envio_imagens_logo - Falha catastrófica na durante a execução dos processos de manipulação '
            f'do diretório Logo do Terminal {terminal.equipamento}. \n Motivo:  ', 'exc')


def envio_imagens_central(terminal):
    """
    Função irá enviar os arquivos da pasta app/static/client-img-folder/central para a pasta do terminal
    :param terminal: objeto equipamento
    :return:
    """
    try:
        destino = ntpath.join(r'\\', terminal.endereco_ip, 'Imagem_TiraTeima', 'propaganda')
        # Existe arquivos na pasta
        if len(os.listdir(destino)) > 0:
            log(f' envio_imagens_central - Existe dados anteriores na pasta Central do Terminal {terminal.equipamento}', 'info')
            # Apagar arquivos existentes
            for i in os.listdir(destino):
                os.remove(os.path.join(destino, i))
                log(f' envio_imagens_central - Removendo dados da pasta Central do Terminal {terminal.equipamento}', 'info')
            # Enviar novos arquivos
            for i in os.listdir(dir_ce):
                origem = os.path.join(dir_ce, i)
                shutil.copy(origem, destino)
                log(f' envio_imagens_central - Enviando novos dados para pasta Central do Terminal {terminal.equipamento}', 'info')
        else:
            # Enviar novos arquivos
            for i in os.listdir(dir_ce):
                origem = os.path.join(dir_ce, i)
                shutil.copy(origem, destino)
                log(f' envio_imagens_central - Enviando novos dados para pasta Central do Terminal {terminal.equipamento}', 'info')
    except Exception:
        log(f' envio_imagens_central - Falha catastrófica na durante a execução dos processos de manipulação '
            f'do diretório Central do Terminal {terminal.equipamento}. \n Motivo:  ', 'exc')


def envio_imagens_desktop(terminal):
    """
    Função irá enviar os arquivos da pasta app/static/client-img-folder/fullscreen para a pasta do terminal
    :param terminal: objeto equipamento
    :return:
    """
    destino = ntpath.join(r'\\', terminal.endereco_ip, 'Imagem_TiraTeima', 'desktop')
    try:
        # Existe arquivos na pasta
        if len(os.listdir(destino)) > 0:
            log(f' envio_imagens_desktop - Existe dados anteriores na pasta Desktop do Terminal {terminal.equipamento}', 'info')
            # Apagar arquivos existentes
            for i in os.listdir(destino):
                os.remove(os.path.join(destino, i))
                log(f' envio_imagens_desktop - Removendo dados da pasta Desktop do Terminal {terminal.equipamento}', 'info')
            # Enviar novos arquivos
            for i in os.listdir(dir_fs):
                origem = os.path.join(dir_fs, i)
                shutil.copy(origem, destino)
                log(f' envio_imagens_desktop - Enviando novos dados para pasta Desktop do Terminal {terminal.equipamento}', 'info')
        else:
            for i in os.listdir(dir_fs):
                origem = os.path.join(dir_fs, i)
                shutil.copy(origem, destino)
                log(f' envio_imagens_desktop - Enviando dados para pasta Desktop do Terminal {terminal.equipamento}', 'info')
    except Exception:
        log(f' envio_imagens_desktop - Falha catastrófica na durante a execução dos processos de manipulação '
            f'do diretório Desktop do Terminal {terminal.equipamento}. \n Motivo:  ', 'exc')


def transacao_arquivos(i, queue):
    """
    Esta função executará todos os processos enviados pela queue
    :param i: thread
    :param queue: objeto queue
    :return:
    """
    while True:
        item = queue.get()
        if item is finalizador_queue:
            queue.task_done()
            break
        else:
            rping = ping(item.endereco_ip, count=1)
            if "timed out" in str(rping._responses[0]):
                sem_conexao = f'Terminal Sem Conexão - {datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")}'
                log(f' transacao_arquivos - Não foi possivel enviar configuração para o terminal {item.equipamento}. '
                    f'\nMotivo: Não há comunicação de rede.', 'error')
                update_bd(item, sem_conexao)
            else:
                log(f' transacao_arquivos - Terminal {item.equipamento} possui conexão de rede, '
                    f'continuando processo de envio de dados.', 'info')
                if item.tipo_equipamento == 1:
                    permissao_imagens(item.endereco_ip, item.equipamento, 'processa')
                else:
                    permissao_imagens(item.endereco_ip,  item.equipamento, 'ubuntu')
                envio_imagens_logo(item)
                envio_imagens_central(item)
                envio_imagens_desktop(item)
                config_servidor(item)
                config_temporizador(item)
                if item.tipo_equipamento == 1:
                    exec_reboot_pdv(item.endereco_ip, 'processa')
                else:
                    exec_reboot_pdv(item.endereco_ip, 'ubuntu')
                mensagem = f'Atualização enviada - {datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")}'
                update_bd(item, mensagem)
                log(f' transacao_arquivos - Processo de carga enviado para o Terminal {item.equipamento}', 'info')
            queue.task_done()


def enviar_terminal(lista_selecao):
    terminais = []
    for i in lista_selecao:
        terminal = Equipamento.query.filter(Equipamento.id == i).one()
        terminais.append(terminal)

    for i in range(num_threads):
        worker = Thread(target=transacao_arquivos, args=(i, queue))
        worker.setDaemon(True)
        worker.start()

    for i in terminais:
        queue.put(i)

    for i in range(num_threads):
        queue.put(finalizador_queue)

    queue.join()
