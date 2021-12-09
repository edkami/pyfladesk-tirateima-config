from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField, SelectField, IntegerField, PasswordField
from wtforms.validators import DataRequired, IPAddress
from app.controllers.query_bd import lista_temporizador, lista_servidor


class FormTemporizador(FlaskForm):
    temp_nome = StringField('nome', validators=[DataRequired()])
    pdt_ne = IntegerField('nenhuma_desc', validators=[DataRequired()])
    pdt_falha = IntegerField('falha', validators=[DataRequired()])
    pdt_sp = IntegerField('sem_promo', validators=[DataRequired()])
    pdt_ep = IntegerField('em_promo', validators=[DataRequired()])
    pdt_uf = IntegerField('uma_faixa', validators=[DataRequired()])
    pdt_df = IntegerField('duas_faixa', validators=[DataRequired()])
    scr_sav = IntegerField('screen_saver', validators=[DataRequired()])
    submit = SubmitField("Cadastrar")


class FormEquipamento(FlaskForm):
    descricao = StringField("descricao", validators=[DataRequired()])
    end_ip = StringField("end_ip", validators=[IPAddress(message="Endereço IP inválido"), DataRequired()])
    servidor = SelectField('servidor')
    temporizador = SelectField('temporizador')
    campos = [(1, "Busca-Preço"), (2, "Propaganda"), (3, "Ambos")]
    modo = RadioField('modo_operacao', choices=campos, validators=[DataRequired()])
    equip_mode = [(1, "Computador"), (2, "Raspberry")]
    tipo_equipamento = RadioField('tipo_equipamento', choices=equip_mode, validators=[DataRequired()])
    submit = SubmitField("Cadastrar")


class FormEquipamentoBusca(FlaskForm):
    descricao = StringField("descricao", validators=[DataRequired()])
    end_ip = StringField("end_ip", validators=[IPAddress(message="Endereço IP inválido"), DataRequired()])
    servidor = SelectField('servidor')
    temporizador = SelectField('temporizador')
    campos = [(1, "Busca-Preço"), (2, "Propaganda"), (3, "Ambos")]
    modo = RadioField('modo_operacao', choices=campos, validators=[DataRequired()])
    submit = SubmitField("Cadastrar")


class FormBusca(FlaskForm):
    busca = StringField("descricao", validators=[DataRequired()])
    campos = [(1, "Descrição"), (2, "Endereço IP")]
    operacao = SelectField("modo_operacao", choices=campos, default=1,
                           validators=[DataRequired()])
    submit = SubmitField("Buscar")


class FormServer(FlaskForm):
    tipo = StringField('tipo', validators=[DataRequired()])
    descricao = StringField('descricao', validators=[DataRequired()])
    end_ip = StringField("end_ip", validators=[IPAddress(message="Endereço IP inválido"), DataRequired()])
    passwd = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("Cadastrar")



