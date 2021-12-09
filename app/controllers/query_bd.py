from app.models.banco_dados import Equipamento, Temporizador, Server, Configuracao
from app.controllers.log_app import log_app as log


def lista_equipamento():
    retorno = Equipamento.query.order_by('equipamento').all()
    lista_equip = []
    for i in retorno:
        tupla = (i.id, i.equipamento)
        lista_equip.append(tupla)
    log(f' lista_equipamento - Retorno da lista de equipamentos: {lista_equip}', 'info')
    return lista_equip


def lista_equipamento_carga():
    retorno_eq = Equipamento.query.order_by('equipamento').all()
    lista_equip_carga = []
    for i in retorno_eq:
        mens_configuracao = Configuracao.query.with_entities(Configuracao.data_envio)\
                                              .filter(Configuracao.equipamento == i.id).one()
        if mens_configuracao[0] is None:
            mens_configuracao = "Nenhuma configuração foi enviada"
            tupla = (i.id, i.equipamento, i.endereco_ip, mens_configuracao)
        else:
            tupla = (i.id, i.equipamento, i.endereco_ip, mens_configuracao[0])
        lista_equip_carga.append(tupla)
    log(f' lista_equipamento_carga - Retorno da lista de equipamentos selecionados para'
        f' carga: {lista_equip_carga}', 'info')
    return lista_equip_carga


def lista_temporizador():
    retorno = Temporizador.query.order_by('temp_nome').all()
    lista_temp = []
    for i in retorno:
        tupla = (i.id, i.temp_nome)
        lista_temp.append(tupla)
    log(f' lista_temporizador - Retorno da lista de temporizadores: {lista_temp}', 'info')
    return lista_temp


def lista_servidor():
    retorno = Server.query.order_by('id').all()
    lista_serv = []
    for i in retorno:
        tupla = (i.id, i.descricao)
        lista_serv.append(tupla)
    log(f' lista_servidor - Retorno da lista de Servidores: {lista_serv}', 'info')
    return lista_serv
