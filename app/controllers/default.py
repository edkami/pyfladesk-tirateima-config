import os
from app import app, db
from werkzeug.utils import secure_filename
from app.controllers.connection_tirateima import queue_leitor
from app.controllers.connection_testing import teste_ping
from app.controllers.ler_log_terminal import conecta_terminal
from app.controllers.consulta_imagens import (lista_fullscreen, excluir_fullscreen, lista_logo, lista_central,
                                              excluir_central, excluir_logo)
from app.controllers.log_app import log_app as log
from app.controllers.validar_ip import endereco_ip
from app.controllers.enviar_config import enviar_terminal
from app.controllers.query_bd import lista_temporizador, lista_servidor, lista_equipamento_carga
from app.models.banco_dados import Temporizador, Equipamento, Server, Configuracao
from app.models.form_cadastro import FormEquipamento, FormBusca, FormTemporizador, FormServer
from flask import render_template, request

from sqlalchemy.exc import IntegrityError


@app.errorhandler(404)
def not_found(e):
    log('Renderizando template 404.html', 'error')
    return render_template('404.html'), {"Refresh": f"5, url = index"}


@app.errorhandler(500)
def not_found(e):
    log('Renderizando template 500.html', 'error')
    return render_template('500.html'), {"Refresh": f"5, url = index"}


@app.errorhandler(503)
def not_found(e):
    log('Renderizando template 503.html', 'error')
    return render_template('503.html'), {"Refresh": f"5, url = index"}


@app.route("/")
@app.route("/index")
def index():
    local_db = os.path.join(os.getcwd(), 'app', "DBTirateima.db")
    if os.path.exists(local_db):
        bd = Equipamento.query.order_by('equipamento').all()
        bt = Temporizador.query.order_by('id').all()
        bs = Server.query.order_by('id').all()
        # Nenhum dado cadastrado
        if (len(bd) == 0) and (len(bt) == 0) and (len(bs) == 0):
            dict_dados = {'card_title': 'Não temos Temporizador, Servidor e Terminal cadastrados!',
                          'card_message': f"Para iniciar o processo de configuração, precisamos cadastrar um "
                                          f"<b>Temporizador</b> e um <b>Servidor</b>. "
                                          f"Com os dois cadastrados podemos criar um <b>Terminal</b>."
                                          f"<br>Inicie o processo utilizando o menu <b>Cadastro</b>."
                          }
            log(' index - Aplicação não possui cadastro dos componentes básicos. Solicitado cadastro.', 'info')
            return render_template('index.html', dados=dict_dados)
        # Tentativa de cadastro de um Terminal, sem ter cadastrado um Temporizador e um Servidor
        elif (len(bd) > 0) and (len(bt) == 0) and (len(bs) == 0):
            dict_dados = {'card_title': 'Ainda não temos Temporizador e Servidor cadastrados!',
                          'card_message': f"Faça o cadastro de um <b>Temporizador</b> e de um <b>Servidor</b>."
                                          f"<br>Para isto utilize o menu <b>Cadastro</b>."
                          }
            log(' index - Aplicação não possui cadastro dos componentes Temporizador e Servidor. Solicitado cadastro.', 'info')
            return render_template('index.html', dados=dict_dados)
        # Realizado cadastro de pelo menos 1 Temporizador, mas nao cadastrado um Servidor
        elif (len(bd) == 0) and (len(bt) > 0) and (len(bs) == 0):
            dict_dados = {'card_title': 'Ainda não temos nenhum Servidor cadastrado.',
                          'card_message': f"Precisa ser cadastrado um <b>Servidor</b>."
                                          f"<br>Para isto, utilize o menu <b>Cadastro</b>."
                          }
            log(' index - Aplicação não possui cadastro do componente Servidor. Solicitado cadastro.',
                'info')
            return render_template('index.html', dados=dict_dados, temp=True, bt=bt)
        # Realizado cadastro de pelo menos 1 Servidor, mas nao cadastrado um Temporizador
        elif (len(bd) == 0) and (len(bt) == 0) and (len(bs) > 0):
            dict_dados = {'card_title': 'Ainda não temos nenhum Temporizador cadastrado.',
                          'card_message': f"Precisa ser cadastrado um <b>Temporizador</b>."
                                          f"<br>Para isto, utilize o menu <b>Cadastro</b>."
                          }
            log(' index - Aplicação não possui cadastro do componente Temporizador. Solicitado cadastro.',
                'info')
            return render_template('index.html', dados=dict_dados, serv=True, bs=bs, temp=False)
        # Realizado cadastro de pelo menos 1 Servidor e um Temporizador, mas nao cadastrado Terminal
        elif (len(bd) == 0) and (len(bt) > 0) and (len(bs) > 0):
            dict_dados = {'card_title': 'Ainda não temos nenhum Terminal cadastrado.',
                          'card_message': f"Precisa ser cadastrado um <b>Terminal</b>."
                                          f"<br>Para isto, utilize o menu <b>Cadastro</b>."
                          }
            log(' index - Aplicação não possui cadastro do componente Terminal. Solicitado cadastro.',
                'info')
            return render_template('index.html', dados=dict_dados, serv=True, bs=bs, temp=True, bt=bt)
        else:
            teste_ping(bd)
            log(' index - Renderizando "principal.html".', 'info')
            return render_template('principal.html', bd=bd, bt=bt, bs=bs)
    else:
        log(' index - Renderizando "index.html".', 'info')
        return render_template('index.html'), {"Refresh": f"60, url = dados_terminal"}


@app.route('/dados_terminal')
def dados_terminal():
    retorno = queue_leitor()
    if retorno != 'Falha':
        ord_retorno = sorted(retorno)
        log(' dados_terminal - Rederizando dados coletados.', 'info')
        return render_template('leitura_dados.html', retorno=retorno, ord_retorno=ord_retorno), {"Refresh": f"60, url = dados_terminal"}
    else:
        dados_dict = {'title': "Falha na Apresentação dos dados!",
                      'message': f'Ocorreu uma falha na busca das informações que deveriam ser apresentadas.',
                      'link': 'index',
                      'btn_text': 'Página principal'
                      }
        log(' dados_terminal - Falha na coleta de dados.', 'error')
        return render_template("falha.html", dados=dados_dict)


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    form = FormEquipamento()
    form.temporizador.choices = lista_temporizador()
    form.servidor.choices = lista_servidor()
    form2 = FormBusca()
    # Validação da Inexistencia do Cadastro de um Temporizador
    bt = Temporizador.query.order_by('temp_nome').all()
    if len(bt) == 0:
        dados_dict = {'title': "Falha ao cadastrar o Terminal!",
                      'message': f'Não é possível cadastrar um Terminal sem um <b>Temporizador</b> e um <b>Servidor</b>.',
                      'link': 'temporizador',
                      'btn_text': 'Cadastrar Temporizador'
                      }
        log(' cadastro - Falha na tentativa de cadastro.\nMotivo: não cadastrado Temporarizado e/ou Servidor.', 'error')
        return render_template("falha.html", dados=dados_dict)

    if form.validate_on_submit():
        try:
            instance_equip = Equipamento(equipamento=form.descricao.data, endereco_ip=form.end_ip.data,
                                         servidor=form.servidor.data, temporizador=form.temporizador.data,
                                         modo_operacao=form.modo.data, tipo_equipamento=form.tipo_equipamento.data,
                                         atividade=0)
            db.session.add(instance_equip)
            db.session.commit()
            db.session.close()

            # Adicionando registro à tabela configuracoes
            id_equip = Equipamento.query.with_entities(Equipamento.id).filter_by(equipamento=form.descricao.data).one()
            instance_config = Configuracao(equipamento=id_equip[0], data_envio=None)
            db.session.add(instance_config)
            db.session.commit()
            db.session.close()

            dados_dict = {'title': "Cadastro do Terminal realizado com sucesso!",
                          'message': f'O cadastro do <b>{form.descricao.data}</b> foi adicionado com sucesso.',
                          'link_voltar': 'cadastro',
                          'btn_voltar': 'Cadastrar Outro Terminal',
                          'link_env': 'index',
                          'btn_env': 'Pagina Principal'
                          }
            log('cadastro - Cadastro do Terminal realizado com sucesso', 'info')
            return render_template("sucessodbt.html", dados=dados_dict)
        except IntegrityError:
            db.session.rollback()
            db.session.close()
            dados_dict = {'title': "Falha ao editar o cadastro do Terminal",
                          'message': f"Falha ao editar o cadastro do <b>{form.descricao.data}</b>. "
                                     f"<p> Motivo: Cadastro já existente.",
                          'link': 'index',
                          'btn_text': 'Voltar'
                          }
            log(' cadastro - Falha ao editar cadastro.\nMotivo: Existe outro cadastro com as mesmas configurações.', 'error')
            return render_template("falha.html", dados=dados_dict)
        except Exception as ex:
            db.session.rollback()
            db.session.close()
            dados_dict = {'title': "Falha ao cadastrar o Terminal",
                          'message': f"Falha ao cadastrar o <b>{form.descricao.data}</b>.<p> Motivo: {ex}.",
                          'link': 'cadastro',
                          'btn_text': 'Voltar'
                          }
            log(f' cadastro - Falha catastrófica ao tentar cadastrar um terminal.\nMotivo: {ex}', 'error')
            return render_template("falha.html", dados=dados_dict)

    log(' cadastro - Renderizando template cadastro.html', 'info')
    return render_template('cadastro.html', form=form, form2=form2)


@app.route("/busca", methods=["GET", "POST"])
def busca():
    form = FormBusca()
    if form.validate_on_submit():
        if form.operacao.data == "1":
            result = Equipamento.query.filter_by(equipamento=form.busca.data).first()
            form2 = FormEquipamento(temporizador=result.temporizador)
            log(' busca - Validação de operação ser 1', 'info')
            return render_template("busca.html", form=form, form2=form2, dados=result)
        else:
            result = Equipamento.query.filter_by(endereco_ip=form.busca.data).first()
            form2 = FormEquipamento(temporizador=result.temporizador)
            log(' busca - Validação de operação diferente de 1', 'info')
            return render_template("busca.html", form=form, form2=form2, dados=result)


@app.route("/busca/<edit>", methods=["GET", "POST"])
def busca_edit(edit):
    form = FormBusca()
    result = Equipamento.query.filter_by(equipamento=edit).first()
    form2 = FormEquipamento(temporizador=result.temporizador, servidor=result.servidor)
    form2.temporizador.choices = lista_temporizador()
    form2.servidor.choices = lista_servidor()
    log(" busca_edit - Renderização para edição dos dados cadastrais do terminal.", 'info')
    return render_template("busca.html", form=form, form2=form2, dados=result)


@app.route('/editarcadastro', methods=["POST"])
def editar_cadastro():
    retorno = request.form.to_dict()
    equipamento = retorno.get('descricao')
    temporizador = retorno.get('temporizador')
    servidor = retorno.get('servidor')
    endereco_ip = retorno.get('end_ip')
    modo_operacao = retorno.get('modo')
    tipo_equipamento = retorno.get('tipo_equipamento')
    try:
        Equipamento.query.filter_by(equipamento=equipamento)\
            .update(dict(equipamento=equipamento, endereco_ip=endereco_ip, modo_operacao=modo_operacao,
                         servidor=servidor, temporizador=temporizador, tipo_equipamento=tipo_equipamento))
        db.session.commit()
        db.session.close()
        dados_dict = {'title': "Cadastro do Terminal alterado com sucesso!",
                      'message': f"O cadastro do <b>{equipamento}</b> foi alterado com sucesso. ",
                      'link': 'index'
                      }
        log(f' editar_cadastro - Cadastro alterado com sucesso', 'info')
        return render_template("sucesso.html", dados=dados_dict)

    except IntegrityError:
        db.session.rollback()
        db.session.close()
        dados_dict = {'title': "Falha ao editar o Cadastro do Terminal!",
                      'message': f'Tentativa de cadastro do <b>{equipamento}</b> falhou. Cadastro já existente!!',
                      'link': 'cadastro'
                      }
        log(f' editar_cadastro - Falha na tentativa de edição do cadastro.'
            f'\n Motivo: Dados cadastrados em outro terminal.', 'error')
        return render_template("falha.html", dados=dados_dict)

    except Exception as exc:
        db.session.rollback()
        db.session.close()
        dados_dict = {'title': "Falha ao editar o Cadastro do Terminal!",
                      'message': f'Tentativa de cadastro do <b>{equipamento}</b> falhou. <p> Motivo: {exc}.',
                      'link': 'cadastro',
                      'btn_text': 'Voltar'
                      }
        log(f' editar_cadastro - Falha catastrófica na tentativa de edição do cadastro.'
            f'\n Motivo: {exc}', 'error')
        return render_template("falha.html", dados=dados_dict)


@app.route('/deletar_equipamento/<edit>', methods=["GET", "POST"])
def deletar_equipamento(edit):
    try:
        Equipamento.query.filter_by(equipamento=edit).delete()
        db.session.commit()
        db.session.close()
        dados_dict = {'title': "Cadastro do Terminal deletado com sucesso!",
                      'message': f"O cadastro do <b>'{edit}'</b> foi deletado com sucesso. ",
                      'link': 'index'
                      }
        log(f' deletar_equipamento - Cadastro deletado com sucesso', 'info')
        return render_template("sucesso.html", dados=dados_dict)
    except Exception as exc:
        db.session.rollback()
        db.session.close()
        dados_dict = {'title': "Falha ao deletar o Terminal",
                      'message': f'Falha no processo de deletar o registro <b>{edit}</b>. <p> Motivo: {exc}',
                      'link': 'index',
                      'btn_text': 'Voltar'
                      }
        log(f' deletar_equipamento - Falha catastrófica ao excluir o cadastro.\n Motivo: {exc}', 'error')
        return render_template("falha.html", dados=dados_dict)


@app.route("/temporizador", methods=["GET", "POST"])
def temporizador():
    form = FormTemporizador()
    if request.method == "POST":
        instancia = Temporizador(temp_nome=form.temp_nome.data,
                                 pdt_ne=form.pdt_ne.data,
                                 pdt_falha=form.pdt_falha.data,
                                 pdt_sp=form.pdt_sp.data,
                                 pdt_ep=form.pdt_ep.data,
                                 pdt_uf=form.pdt_uf.data,
                                 pdt_df=form.pdt_df.data,
                                 scr_sav=int(form.scr_sav.data * 1000)
                                 )
        try:
            existe = db.session.query(Temporizador.id).filter_by(temp_nome=form.temp_nome.data).first()
            if existe is None:
                db.session.add(instancia)
                db.session.commit()
                db.session.close()
                dados_dict = {'title': "Cadastro do Temporizador realizado com sucesso!",
                              'message': f'O cadastro do <b>{form.temp_nome.data}</b> foi adicionado com sucesso.',
                              'link_voltar': 'temporizador',
                              'btn_voltar': 'Cadastrar Outro Temporizador',
                              'link_env': 'index',
                              'btn_env': 'Página Principal'
                              }
                log(' temporizador - Cadastro do temporizador realizado com sucesso', 'info')
                return render_template("sucessodbt.html", dados=dados_dict)
            else:
                dados_dict = {'title': "Falha ao cadastrar o temporizador!",
                              'message': f'Tentativa de cadastro do <b>{form.temp_nome.data}</b> falhou! '
                                         f'<p>Motivo: O cadastro do <b>{form.temp_nome.data}</b> já existe!',
                              'link': 'temporizador',
                              'btn_text': 'Voltar'
                              }
                log(' temporizador - Falha ao cadastrar o temporizador.'
                    '\n Motivo: Dados cadastrados em outro temporizador.', 'info')
                return render_template("falha.html", dados=dados_dict)
        except Exception as exc:
            db.session.rollback()
            db.session.close()
            dados_dict = {'title': "Falha ao cadastrar o temporizador!",
                          'message': f'Tentativa de cadastro do <b>{form.temp_nome.data}</b> falhou! <p>Motivo: {exc}',
                          'link': 'temporizador',
                          'btn_text': 'Voltar'
                          }
            log(f' temporizador - Falha catastrófica ao cadastrar o temporizador.\n Motivo: {exc}', 'error')
            return render_template("falha.html", dados=dados_dict)

    log(' temporizador - Renderizando o template temporizador.html', 'info')
    return render_template("temporizador.html", form=form)


@app.route("/temporizador/<edit>", methods=["GET", "POST"])
def busca_temporizador(edit):
    form = FormTemporizador()
    result = Temporizador.query.filter_by(temp_nome=edit).first()
    tempo_scrsave = int(result.scr_sav/1000)
    log(" busca_temporizador - Renderização para edição dos dados cadastrais do temporizador.", 'info')
    return render_template("editartemporizador.html", form=form, dados=result, tempo_scrsave=tempo_scrsave)


@app.route('/editartemporizador', methods=["POST"])
def editar_temporizador():
    retorno = request.form.to_dict()
    temp_nome = retorno.get('temp_nome')
    pdt_ne = retorno.get('pdt_ne')
    pdt_falha = retorno.get('pdt_falha')
    pdt_sp = retorno.get('pdt_sp')
    pdt_ep = retorno.get('pdt_ep')
    pdt_uf = retorno.get('pdt_uf')
    pdt_df = retorno.get('pdt_df')
    scr_sav = int(retorno.get('scr_sav')) * 1000
    try:
        Temporizador.query.filter_by(temp_nome=temp_nome)\
            .update(dict(temp_nome=temp_nome,
                         pdt_ne=pdt_ne,
                         pdt_falha=pdt_falha,
                         pdt_sp=pdt_sp,
                         pdt_ep=pdt_ep,
                         pdt_uf=pdt_uf,
                         pdt_df=pdt_df,
                         scr_sav=scr_sav
                         ))
        db.session.commit()
        db.session.close()
        dados_dict = {'title': "Cadastro do Temporizador editado com sucesso!",
                      'message': f'O cadastro do <b>{temp_nome}</b> foi alterado com sucesso. '
                                 f'Iremos redirecionar para a página principal.',
                      'link': 'index'
                      }
        log(' editar_temporizador - Cadastro do Temporizador editado com sucesso', 'info')
        return render_template("sucesso.html", dados=dados_dict)
    except IntegrityError:
        db.session.rollback()
        db.session.close()
        dados_dict = {'title': "Falha ao editar o cadastro do Temporizador",
                      'message': f"Falha ao editar o cadastro do <b>{temp_nome}</b>. "
                                 f"<p> Motivo: Cadastro já existente.",
                      'link': 'index',
                      'btn_text': 'Voltar'
                      }
        log(' editar_temporizador - Falha ao editar o cadastro do Temporizador.'
            '\n Motivo: Dados cadastrados em outro temporizador', 'error')
        return render_template("falha.html", dados=dados_dict)
    except Exception as exc:
        db.session.rollback()
        db.session.close()
        dados_dict = {'title': "Falha ao editar o cadastro do Temporizador",
                      'message': f"Falha ao editar o cadastro do <b>{temp_nome}</b>. <p> Motivo: {exc}.",
                      'link': 'index',
                      'btn_text': 'Voltar'
                      }
        log(f' editar_temporizador - Falha catastrófica ao cadastrar o temporizador.\n Motivo: {exc}', 'error')
        return render_template("falha.html", dados=dados_dict)


@app.route('/deletar_temporizador/<edit>', methods=["GET", "POST"])
def deletar_temporizador(edit):
    try:
        Temporizador.query.filter_by(temp_nome=edit).delete()
        db.session.commit()
        db.session.close()
        dados_dict = {'title': "Cadastro do Temporizador deletado com sucesso!",
                      'message': f"O cadastro do <b>{edit}</b> foi deletado com sucesso. ",
                      'link': 'index'
                      }
        log(' deletar_temporizador - Cadastro do Temporizador deletado com sucesso', 'info')
        return render_template("sucesso.html", dados=dados_dict)
    except Exception as exc:
        db.session.rollback()
        db.session.close()
        dados_dict = {'title': "Falha ao deletar o Temporizador",
                      'message': f'Falha no processo de deletar o cadastro do <b>{edit}</b>. <p> Motivo: {exc}',
                      'link': 'index',
                      'btn_text': 'Voltar'
                      }
        log(f' deletar_temporizador - Falha catastrófica ao deletar o Temporizador.\n Motivo: {exc}', 'error')
        return render_template("falha.html", dados=dados_dict)


@app.route('/server', methods=["GET", "POST"])
def server():
    """
    Rota para inserir informações do tipo de conexão. Neste momento a conexão será somente PostgreSQL do Concentrador ML
    :return:
    """
    form = FormServer()
    dados = {'tipo': "PostgreSQL",
             }
    if request.method == "POST":
        if not endereco_ip(form.end_ip.data):
            dados_dict = {'title': "Falha ao cadastrar o Servidor!",
                          'message': f'Tentativa de cadastro do <b>{form.descricao.data}</b> falhou! '
                                     f'<p>Motivo: Endereço IP informado <b>{form.end_ip.data}</b> é inválido.',
                          'link': 'server',
                          'btn_text': 'Voltar'
                          }
            log(f' server - Falha ao cadastrar o Servidor.'
                f'\n Motivo: Endereço IP informado "{form.end_ip.data}" é inválido', 'error')
            return render_template("falha.html", dados=dados_dict)
        else:
            instancia = Server(tipo="PostgreSQL",
                               descricao=form.descricao.data,
                               endereco_ip=form.end_ip.data,
                               password='null')
            try:
                existe = db.session.query(Server.id).filter_by(endereco_ip=form.end_ip.data).first()
                if existe is None:
                    db.session.add(instancia)
                    db.session.commit()
                    db.session.close()
                    dados_dict = {'title': "Cadastro do Servidor realizado com sucesso!",
                                  'message': f'O cadastro do <b>{form.descricao.data}</b> foi adicionado com sucesso.',
                                  'link_voltar': 'server',
                                  'btn_voltar': 'Cadastrar Outro Servidor',
                                  'link_env': 'index',
                                  'btn_env': 'Página Principal'
                                  }
                    log(' server - Cadastro do servidor realizado com sucesso', 'info')
                    return render_template("sucessodbt.html", dados=dados_dict)
                else:
                    dados_dict = {'title': "Falha ao cadastrar o Servidor!",
                                  'message': f'Tentativa de cadastro do <b>{form.descricao.data}</b> falhou! '
                                             f'<p>Motivo: O cadastro do <b>{form.descricao.data}</b> já existe!',
                                  'link': 'server',
                                  'btn_text': 'Voltar'
                                  }
                    log(" servidor - Falha ai cadastrar o servidor."
                        "\n Motivo: Dados cadastrados em outro servidor", 'error')
                    return render_template("falha.html", dados=dados_dict)
            except IntegrityError as exc:
                db.session.rollback()
                db.session.close()
                dados_dict = {'title': "Falha ao cadastrar o Servidor!",
                              'message': f'Tentativa de cadastro do <b>{form.descricao.data}</b> '
                                         f'falhou! <p>Motivo: Cadastro já existente.',
                              'link': 'server',
                              'btn_text': 'Voltar'
                              }
                log(f" servidor - Falha ai cadastrar o servidor."
                    f"\n Motivo: Dados cadastrados em outro servidor.\n {exc}", 'error')
                return render_template("falha.html", dados=dados_dict)

            except Exception as exc:
                db.session.rollback()
                db.session.close()
                dados_dict = {'title': "Falha ao cadastrar o Servidor!",
                              'message': f'Tentativa de cadastro do <b>{form.descricao.data}</b> falhou! <p>Motivo: {exc}',
                              'link': 'server',
                              'btn_text': 'Voltar'
                              }
                log(f' servidor - Falha catastrófica ao cadastrar o Servidor.\n Motivo: {exc}', 'error')
                return render_template("falha.html", dados=dados_dict)

    log(' servidor - Rendenrizando template server.html', 'info')
    return render_template('server.html', form=form, dados=dados)


@app.route("/server/<edit>", methods=["GET", "POST"])
def busca_servidor(edit):
    form = FormServer()
    result = Server.query.filter_by(descricao=edit).first()
    log(' busca_servidor - Renderizando template editarservidor.html', 'info')
    return render_template("editarservidor.html", form=form, dados=result)


@app.route('/editarservidor', methods=["POST"])
def editar_servidor():
    retorno = request.form.to_dict()
    tipo = retorno.get('tipo')
    descricao = retorno.get('descricao')
    end_ip = retorno.get('end_ip')
    passwd = retorno.get('passwd')
    print(tipo, descricao, end_ip, passwd)
    try:
        Server.query.filter_by(descricao=descricao)\
            .update(dict(descricao=descricao,
                         tipo=tipo,
                         endereco_ip=end_ip,
                         password='null',
                         ))
        db.session.commit()
        db.session.close()
        dados_dict = {'title': "Cadastro do Servidor editado com sucesso!",
                      'message': f'O cadastro do <b>{descricao}</b> foi alterado com sucesso. '
                                 f'Iremos redirecionar para a página principal.',
                      'link': 'index'
                      }
        log(' editar_servidor - Cadastro do Servidor editado com sucesso', 'info')
        return render_template("sucesso.html", dados=dados_dict)
    except IntegrityError:
        db.session.rollback()
        db.session.close()
        dados_dict = {'title': "Falha ao editar o cadastro do Servidor",
                      'message': f"Falha ao editar o cadastro do <b>{descricao}</b>. "
                                 f"<p> Motivo: Cadastro já existente.",
                      'link': 'index',
                      'btn_text': 'Voltar'
                      }
        log(' editar_servidor - Falha ao editar o cadastro do Servidor.\n Motivo: Dados cadastrados em outro servidor',
            'error')
        return render_template("falha.html", dados=dados_dict)
    except Exception as exc:
        db.session.rollback()
        db.session.close()
        dados_dict = {'title': "Falha ao editar o cadastro do Servidor",
                      'message': f"Falha ao editar o cadastro do <b>{descricao}</b>. <p> Motivo: {exc}.",
                      'link': 'index',
                      'btn_text': 'Voltar'
                      }
        log(f' editar_servidor - Falha catastrófica ao editar o cadastro do servidor.\n Motivo: {exc}', 'error')
        return render_template("falha.html", dados=dados_dict)


@app.route('/deletar_servidor/<edit>', methods=["GET", "POST"])
def deletar_servidor(edit):
    try:
        Server.query.filter_by(descricao=edit).delete()
        db.session.commit()
        db.session.close()
        dados_dict = {'title': "Cadastro do Servidor deletado com sucesso!",
                      'message': f"O cadastro do <b>{edit}</b> foi deletado com sucesso. ",
                      'link': 'index'
                      }
        log(' deletar_servidor - Cadastro do Servidor deletado com sucesso', 'info')
        return render_template("sucesso.html", dados=dados_dict)
    except Exception as exc:
        db.session.rollback()
        db.session.close()
        dados_dict = {'title': "Falha ao deletar o Servidor",
                      'message': f'Falha no processo de deletar o cadastro do <b>{edit}</b>. <p> Motivo: {exc}',
                      'link': 'index',
                      'btn_text': 'Voltar'
                      }
        log(f' deletar_servidor - Falha catastrófica ao deletar o Servidor.\n Motivo: {exc}', 'error')
        return render_template("falha.html", dados=dados_dict)


@app.route("/selecionar_imagens")
def select_images():
    lfs = lista_fullscreen()
    lct = lista_central()
    llg = lista_logo()
    log(f' select_images - Renderizando listas de imagens.\n Fullscreen = {lfs}\n Central = {lct}\n Logo = {llg}',
        'info')
    return render_template("selectimages.html", lfs=lfs, lct=lct, llg=llg)


@app.route("/alerta/<id>")
def alerta(id):
    dados_dict = {'title': "Alerta de Exclusão!",
                  'message': f'O sistema irá excluir definitivamente as imagens anteriormente adicionadas!!!<p>Deseja realmente excluir?',
                  'link_voltar': 'select_images',
                  'btn_voltar': 'Não',
                  'link_env': 'excluir_imagens',
                  'btn_env': 'Sim'
                 }
    log(' alerta - Renderização template alerta.html', 'info')
    return render_template('alerta.html', dados=dados_dict, id=id)


@app.route("/excluir_imagens/<id>", methods=["GET", "POST"])
def excluir_imagens(id):
    if id == 'fs':
        try:
            retorno = excluir_fullscreen()
            if retorno:
                dados_dict = {'title': "Arquivos excluídos com sucesso!",
                              'message': f'Os arquivos da pasta FullScreen foram excluídos com sucesso.',
                              'link': 'select_images'
                              }
                log(' excluir_imagens - Imagens FullScreen excluídas com sucesso.', 'info')
                return render_template("sucesso.html", dados=dados_dict)
            else:
                dados_dict = {'title': "Falha ao excluir arquivos!",
                              'message': f"Falha ao excluir os dados da pasta FullScreen.",
                              'link': 'select_images',
                              'btn_text': 'Voltar'
                              }
                log(' excluir_imagens - Falha ao excluir imagens FullScreen.', 'error')
                return render_template("falha.html", dados=dados_dict)
        except Exception as exc:
            dados_dict = {'title': "Falha ao excluir arquivos!",
                          'message': f"Falha ao excluir os dados da pasta FullScreen. <p> Motivo: {exc}",
                          'link': 'select_images',
                          'btn_text': 'Voltar'
                          }
            log(f' excluir_imagens - Falha catastrófica ao excluir imagens FullScreen.\n Motivo: {exc}', 'error')
            return render_template("falha.html", dados=dados_dict)
    elif id == 'ct':
        try:
            retorno = excluir_central()
            if retorno:
                dados_dict = {'title': "Arquivos excluídos com sucesso!",
                              'message': f'Os arquivos da pasta Central foram excluídos com sucesso.',
                              'link': 'select_images'
                              }
                log(' excluir_imagens - Imagens Central excluídas com sucesso.', 'info')
                return render_template("sucesso.html", dados=dados_dict)
            else:
                dados_dict = {'title': "Falha ao excluir arquivos!",
                              'message': f"Falha ao excluir os dados da pasta Central.",
                              'link': 'select_images',
                              'btn_text': 'Voltar'
                              }
                log(' excluir_imagens - Falha ao excluir imagens Central.', 'error')
                return render_template("falha.html", dados=dados_dict)
        except Exception as exc:
            dados_dict = {'title': "Falha ao excluir arquivos!",
                          'message': f"Falha ao excluir os dados da pasta Central. <p> Motivo: {exc}",
                          'link': 'select_images',
                          'btn_text': 'Voltar'
                          }
            log(f' excluir_imagens - Falha catastrófica ao excluir imagens FullScreen.\n Central: {exc}', 'error')
            return render_template("falha.html", dados=dados_dict)
    elif id == 'lg':
        try:
            retorno = excluir_logo()
            if retorno:
                dados_dict = {'title': "Arquivos excluídos com sucesso!",
                              'message': f'O arquivo da pasta Logo foi excluído com sucesso.',
                              'link': 'select_images'
                              }
                og(' excluir_imagens - Imagem Logo excluída com sucesso.', 'info')
                return render_template("sucesso.html", dados=dados_dict)
            else:
                dados_dict = {'title': "Falha ao excluir arquivos!",
                              'message': f"Falha ao excluir o dado da pasta Logo.",
                              'link': 'select_images',
                              'btn_text': 'Voltar'
                              }
                log(' excluir_imagens - Falha ao excluir imagem Logo.', 'error')
                return render_template("falha.html", dados=dados_dict)
        except Exception as exc:
            dados_dict = {'title': "Falha ao excluir arquivos!",
                          'message': f"Falha ao excluir o dado da pasta Logo. <p> Motivo: {exc}",
                          'link': 'select_images',
                          'btn_text': 'Voltar'
                          }
            log(f' excluir_imagens - Falha catastrófica ao excluir imagem Logo.\n Motivo: {exc}', 'error')
            return render_template("falha.html", dados=dados_dict)


@app.route("/gravar_scr", methods=["GET", "POST"])
def gravar_scr():
    # FullScreen
    if request.method == "POST":
        try:
            file_scr = request.files.getlist("img-scr[]")
            if file_scr[0].filename != '':
                for i in file_scr:
                    image = secure_filename(i.filename)
                    i.save(os.path.join(app.config['UPLOAD_FOLDER'], 'fullscreen', image))

                dados_dict = {'title': "Imagens salvas com sucesso!",
                              'message': f"As imagens foram salvas com sucesso. <p> "
                                         f"Clique em <b>Voltar</b> para adicionar mais imagens ou em "
                                         f"<b>Enviar</b> para fazer o envio",
                              'btn_voltar': 'Voltar',
                              'link_voltar': 'select_images',
                              'btn_env': 'Enviar Carga',
                              'link_env': 'enviar_config'
                              }
                log(' gravar_scr - Imagens Central salvas com sucesso', 'info')
                return render_template("gravar_scr.html", dados=dados_dict)
            else:
                dados_dict = {'title': "Falha ao salvar imagens",
                              'message': f"Não foi enviada nenhuma imagem!",
                              'link': 'select_images',
                              'btn_text': 'Voltar'
                              }
                log(' gravar_scr - Nenhuma imagem foi enviada para FullScreen', 'error')
                return render_template("falha.html", dados=dados_dict)
        except TypeError as exc:
            dados_dict = {'title': "Falha ao salvar imagens",
                          'message': f"Não foi enviada nenhuma imagem!<p>Motivo:{exc}",
                          'link': 'select_images',
                          'btn_text': 'Voltar'
                          }
            log(f' gravar_scr - Falha catastrófica ao salvar imagens FullScreen.\n Motivo: {exc}', 'error')
            return render_template("falha.html", dados=dados_dict)
        except Exception as exc:
            dados_dict = {'title': "Falha ao salvar imagens",
                          'message': f"Falha ao salvar imagens. <p> Motivo: {exc}",
                          'link': 'select_images',
                          'btn_text': 'Voltar'
                          }
            log(f' gravar_scr - Falha catastrófica ao salvar imagens FullScreen.\n Motivo: {exc}', 'error')
            return render_template("falha.html", dados=dados_dict)


@app.route("/gravar_central", methods=["GET", "POST"])
def gravar_central():
    # Central
    if request.method == "POST":
        try:
            file_central = request.files.getlist("img-central[]")
            if file_central[0].filename != '':
                for i in file_central:
                    image = secure_filename(i.filename)
                    i.save(os.path.join(app.config['UPLOAD_FOLDER'], 'central', image))

                dados_dict = {'title': "Imagens salvas com sucesso!",
                              'message': f"As imagens foram salvas com sucesso. <p> "
                                         f"Clique em <b>Voltar</b> para adicionar mais imagens ou em "
                                         f"<b>Enviar</b> para fazer o envio",
                              'btn_voltar': 'Voltar',
                              'link_voltar': 'select_images',
                              'btn_env': 'Enviar Carga',
                              'link_env': 'enviar_config'
                              }
                log(' gravar_central - Imagens Central salvas com sucesso', 'info')
                return render_template("gravar_scr.html", dados=dados_dict)
            else:
                dados_dict = {'title': "Falha ao salvar imagens",
                              'message': f"Não foi enviada nenhuma imagem!",
                              'link': 'select_images',
                              'btn_text': 'Voltar'
                              }
                log(' gravar_central - Nenhuma imagem foi enviada para Central', 'error')
                return render_template("falha.html", dados=dados_dict)
        except TypeError as exc:
            dados_dict = {'title': "Falha ao salvar imagens",
                          'message': f"Não foi enviada nenhuma imagem!<p>Motivo:{exc}",
                          'link': 'select_images',
                          'btn_text': 'Voltar'
                          }
            log(f' gravar_central - Falha catastrófica ao salvar imagens Central.\n Motivo: {exc}', 'error')
            return render_template("falha.html", dados=dados_dict)
        except Exception as exc:
            dados_dict = {'title': "Falha ao salvar imagens",
                          'message': f"Falha ao salvar imagens. <p> Motivo: {exc}",
                          'link': 'select_images',
                          'btn_text': 'Voltar'
                          }
            log(f' gravar_central - Falha catastrófica ao salvar imagens Central.\n Motivo: {exc}', 'error')
            return render_template("falha.html", dados=dados_dict)


@app.route("/gravar_logo", methods=["GET", "POST"])
def gravar_logo():
    if request.method == "POST":
        try:
            file_lg = request.files.get("img-lg")
            if file_lg.filename != '':
                image = secure_filename(file_lg.filename)
                file_lg.save(os.path.join(app.config['UPLOAD_FOLDER'], 'logo', image))
                dados_dict = {'title': "Imagens salvas com sucesso!",
                              'message': f"As imagens foram salvas com sucesso. <p> "
                                         f"Clique em <b>Voltar</b> para adicionar mais imagens ou em "
                                         f"<b>Enviar</b> para fazer o envio",
                              'btn_voltar': 'Voltar',
                              'link_voltar': 'select_images',
                              'btn_env': 'Enviar Carga',
                              'link_env': 'enviar_config'
                              }
                log(' gravar_logo - Imagem Logo salva com sucesso', 'info')
                return render_template("gravar_scr.html", dados=dados_dict)
            else:
                dados_dict = {'title': "Falha ao salvar imagens",
                              'message': f"Não foi enviada nenhuma imagem!",
                              'link': 'select_images',
                              'btn_text': 'Voltar'
                              }
                log(' gravar_logo - Nenhuma imagem foi enviada para Logo', 'error')
                return render_template("falha.html", dados=dados_dict)
        except TypeError as exc:
            dados_dict = {'title': "Falha ao salvar imagens",
                          'message': f"Não foi enviada nenhuma imagem!<p>Motivo: {exc}",
                          'link': 'select_images',
                          'btn_text': 'Voltar'
                          }
            log(f' gravar_logo - Falha catastrófica ao salvar imagem Logo.\n Motivo: {exc}', 'error')
            return render_template("falha.html", dados=dados_dict)
        except Exception as exc:
            dados_dict = {'title': "Falha ao salvar imagens",
                          'message': f"Falha ao salvar imagens. <p> Motivo: {exc}",
                          'link': 'select_images',
                          'btn_text': 'Voltar'
                          }
            log(f' gravar_logo - Falha catastrófica ao salvar imagem Logo.\n Motivo: {exc}', 'error')
            return render_template("falha.html", dados=dados_dict)


@app.route("/enviar_config", methods=["GET", "POST"])
def enviar_config():
    lista_equip = lista_equipamento_carga()
    if request.method == "POST":
        retorno = request.form.getlist("enviacheck")
        if retorno:
            enviar_terminal(retorno)
            lista_equip = lista_equipamento_carga()
            log(f' enviar_config - Renderizando template envioconfiguracao.html (POST).'
                f'\nID dos equipamentos selecionados: {retorno}', 'info')
            return render_template("envioconfiguracao.html", equipamento=lista_equip)
        else:
            dados_dict = {'title': "Falha ao enviar configuração",
                          'message': f"Falha ao enviar configuração. <p> Motivo: Nenhum terminal foi selecionado.",
                          'link': 'enviar_config',
                          'btn_text': 'Voltar'
                          }
            log(' enviar_config - Falha ao enviar configuração.\n Motivo: Nenhum terminal foi selecionado.', 'error')
            return render_template("falha.html", dados=dados_dict)

    log(' enviar_config - Renderizando template envioconfiguracao.htm (GET)', 'info')
    return render_template("envioconfiguracao.html", equipamento=lista_equip)


@app.route('/view_log/<end_ip>/<terminal>')
def view_log(end_ip, terminal):
    log_terminal = conecta_terminal(end_ip)
    if "Falha na comunicação de rede" in log_terminal:
        dados_dict = {'title': "Falha ao buscar log de operação do terminal",
                      'message': f"{log_terminal}",
                      'link': 'index',
                      'btn_text': 'Voltar'
                      }
        log(' view_log - Falha na comunicaçao com o terminal.\n Motivo: Problemas na conexão de rede.', 'error')
        return render_template("falha.html", dados=dados_dict)
    elif "Falha na busca do log de operação do terminal" in log_terminal:
        dados_dict = {'title': "Falha ao buscar log de operação do terminal",
                      'message': f"{log_terminal}",
                      'link': 'index',
                      'btn_text': 'Voltar'
                      }
        log(' view_log - Falha na visualização do log do terminal.\n Motivo: Arquivo inacessível.', 'error')
        return render_template("falha.html", dados=dados_dict)
    else:
        log(' view_log - Rederizando template visualiza_log.html com o log do terminal', 'info')
        return render_template("visualiza_log.html", texto=log_terminal, terminal=terminal)
