from app import db


class Temporizador(db.Model):
    __tablename__ = "temporizadores"
    id = db.Column(db.Integer, primary_key=True)
    temp_nome = db.Column(db.String)
    pdt_ne = db.Column(db.Integer)
    pdt_falha = db.Column(db.Integer)
    pdt_sp = db.Column(db.Integer)
    pdt_ep = db.Column(db.Integer)
    pdt_uf = db.Column(db.Integer)
    pdt_df = db.Column(db.Integer)
    scr_sav = db.Column(db.Integer)

    def __init__(self, temp_nome, pdt_ne, pdt_falha, pdt_sp, pdt_ep, pdt_uf, pdt_df, scr_sav):
        self.temp_nome = temp_nome
        self.pdt_ne = pdt_ne
        self.pdt_falha = pdt_falha
        self.pdt_sp = pdt_sp
        self.pdt_ep = pdt_ep
        self.pdt_uf = pdt_uf
        self.pdt_df = pdt_df
        self.scr_sav = scr_sav

    def __repr__(self):
        return "<Temporizador %r>" % self.temp_nome


class Server(db.Model):
    __tablename__ = "servidores"
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String)
    descricao = db.Column(db.String, unique=True)
    endereco_ip = db.Column(db.String, unique=True)
    password = db.Column(db.String)

    def __init__(self, tipo, descricao, endereco_ip, password):
        self.tipo = tipo
        self.descricao = descricao
        self.endereco_ip = endereco_ip
        self.password = password

    def __repr__(self):
        return "<Server %r>" % self.descricao


class Configuracao(db.Model):
    __tablename__ = 'configuracoes'
    id = db.Column(db.Integer, primary_key=True)
    equipamento = db.Column(db.Integer, db.ForeignKey('equipamentos.id'))
    data_envio = db.Column(db.String)

    relacao = db.relationship("Equipamento", foreign_keys=equipamento)

    def __init__(self, equipamento, data_envio):
        self.equipamento = equipamento
        self.data_envio = data_envio

    def __repr__(self):
        return "<Configuracao %r>" % self.equipamento


class Equipamento(db.Model):
    __tablename__ = "equipamentos"
    id = db.Column(db.Integer, primary_key=True)
    equipamento = db.Column(db.String, unique=True)
    endereco_ip = db.Column(db.String, unique=True)
    servidor = db.Column(db.Integer, db.ForeignKey('servidores.id'))
    temporizador = db.Column(db.Integer, db.ForeignKey('temporizadores.id'))
    modo_operacao = db.Column(db.Integer)
    tipo_equipamento = db.Column(db.Integer)
    atividade = db.Column(db.Integer, default=0)

    relacao = db.relationship("Temporizador", foreign_keys=temporizador)
    relacao_serv = db.relationship("Server", foreign_keys=servidor)

    def __init__(self, equipamento, endereco_ip, servidor, temporizador, modo_operacao, tipo_equipamento, atividade):
        self.equipamento = equipamento
        self.endereco_ip = endereco_ip
        self.servidor = servidor
        self.temporizador = temporizador
        self.modo_operacao = modo_operacao
        self.tipo_equipamento = tipo_equipamento
        self.atividade = atividade

    def __repr__(self):
        return "<Equipamento %r>" % self.equipamento


def init_db():
    db.create_all()
