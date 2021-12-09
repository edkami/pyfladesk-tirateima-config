import os
import logging
import locale
from datetime import datetime


def log_app(mess, error):
    # Importada a classe logging que trará log ao sistema.
    # Log será gravado em modo Debug, no arquivo ~\log.txt
    # log grava as informações em modo debug enviadas pelo sistema
    locale.setlocale(locale.LC_ALL, 'pt_BR.utf-8')
    data_hora = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    log = logging.getLogger("Tira-Teima")
    log.setLevel(logging.DEBUG)
    # caminho onde será gravado o log do sistema
    caminholog = os.path.join(os.getcwd(), 'log.txt')
    # filelog é a variavel onde os dados de log serão armazenados.
    filelog = logging.FileHandler(caminholog, encoding='UTF-8')
    filelog.setLevel(logging.DEBUG)
    # Criação do formato de saída do arquivo de log.
    formatacaolog = logging.Formatter(f'{data_hora}-%(name)s-%(levelname)s- %(message)s')
    filelog.setFormatter(formatacaolog)
    # Adição de log a filelog
    log.addHandler(filelog)
    if error == 'info':
        log.info(mess)
    elif error == 'error':
        log.error(mess)
    else:
        log.exception(mess)
    # Apagar o handler após gravado no arquivo
    log.handlers.clear()