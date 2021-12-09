import os
from app.controllers.log_app import log_app as log

dir_ce = os.path.join('D:\\dev\\tira-teima-config\\app\\static\\client-img-folder\\', 'central')
dir_fs = os.path.join('D:\\dev\\tira-teima-config\\app\\static\\client-img-folder\\', 'fullscreen')
dir_lg = os.path.join('D:\\dev\\tira-teima-config\\app\\static\\client-img-folder\\', 'logo')


def lista_fullscreen():
    lista = [i for i in os.listdir(dir_fs)]
    log(f' lista_fullscreen - Lista de imagens FullScreen = {lista}', 'info')
    return lista


def excluir_fullscreen():
    try:
        [os.remove(os.path.join(dir_fs, i)) for i in os.listdir(dir_fs)]
        log(' excluir_fullscreen - Excluindo imagens FullScreen', 'info')
        return True
    except Exception:
        log(f" excluir_fullscreen - Falha na tentativa de exclusão das imagens FullScreen.\n Motivo: ", 'exc')
        return False


def lista_central():
    lista = [i for i in os.listdir(dir_ce)]
    log(f' lista_central - Lista de imagens Central = {lista}', 'info')
    return lista


def excluir_central():
    try:
        [os.remove(os.path.join(dir_ce, i)) for i in os.listdir(dir_ce)]
        log(' excluir_central - Excluindo imagens Central', 'info')
        return True
    except Exception:
        log(f" excluir_central - Falha na tentativa de exclusão das imagens Central.\n Motivo: ", 'exc')
        return False


def lista_logo():
    lista = [i for i in os.listdir(dir_lg)]
    log(f' lista_logo - Imagem Logo = {lista}', 'info')
    return lista


def excluir_logo():
    try:
        [os.remove(os.path.join(dir_lg, i)) for i in os.listdir(dir_lg)]
        log(' excluir_logo - Excluindo imagem Logo', 'info')
        return True
    except Exception:
        log(f" excluir_central - Falha na tentativa de exclusão da imagem Logo.\n Motivo: ", 'exc')
        return False
