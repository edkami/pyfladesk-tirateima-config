import os
from app.controllers.log_app import log_app as log

dir_ce = os.path.join(os.getcwd(), 'app\\static\\client-img-folder\\', 'central')
dir_lg = os.path.join(os.getcwd(), 'app\\static\\client-img-folder\\', 'logo')


def lista_central():
    os.makedirs(dir_ce, exist_ok=True)
    lista = [i for i in os.listdir(dir_ce)]
    log(f' lista_central - Lista de imagem Central = {lista}', 'info')
    return lista


def excluir_central():
    try:
        os.makedirs(dir_ce, exist_ok=True)
        [os.remove(os.path.join(dir_ce, i)) for i in os.listdir(dir_ce)]
        log(' excluir_central - Excluindo imagem Central', 'info')
        return True
    except Exception:
        log(f" excluir_central - Falha na tentativa de exclusão da imagem Central.\n Motivo: ", 'exc')
        return False


def lista_logo():
    os.makedirs(dir_lg, exist_ok=True)
    lista = [i for i in os.listdir(dir_lg)]
    log(f' lista_logo - Imagem Logo = {lista}', 'info')
    return lista


def excluir_logo():
    try:
        os.makedirs(dir_lg, exist_ok=True)
        [os.remove(os.path.join(dir_lg, i)) for i in os.listdir(dir_lg)]
        log(' excluir_logo - Excluindo imagem Logo', 'info')
        return True
    except Exception:
        log(f" excluir_central - Falha na tentativa de exclusão da imagem Logo.\n Motivo: ", 'exc')
        return False
