import paramiko
from paramiko import SSHClient
from app.controllers.log_app import log_app as log


class SSH:
    def __init__(self, host, user):
        passwd = "pr0t31m4ML"
        self.ssh = SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=host, username=user, password=passwd)

    def exec_cmd(self, cmd):
        result = []
        stdin, stdout, stderr = self.ssh.exec_command(cmd, get_pty=True)
        if stderr.channel.recv_exit_status() != 0:
            print(stderr.read())
        else:
            for std in stdout.readlines():
                if std is bytes:
                    result.append(std.decode('latin-1'))
                else:
                    result.append(std)
            return result
        self.ssh.close()


def exec_reboot_pdv(host, user):
    """
    Função usa SSH para enviar o camando de reboot ao terminal com o IP enviado
    :return:
        True = processo concluído
    :exception
        False = falha no processo e causa
    """
    try:
        ssh = SSH(host, user)
        ssh.exec_cmd("echo pr0t31m4ML | sudo -S reboot")
        log(' exec_reboot_pdv - Comando ssh para reboot enviado com sucesso.', 'info')
        return True
    except Exception:
        log(' exec_reboot_pdv - Comando ssh para reboot não foi executado.\n Motivo: ', 'exc')
        return False


def permissao_imagens(host, equipamento, user):
    """
    Função irá executar chmod na pasta compartilhada no Terminal, afim de dar direitos totais sobre a pasta
    :param host: endereço IP do terminal
    :return:
    """
    try:
        ssh = SSH(host, user)
        ssh.exec_cmd(f'echo pr0t31m4ML | sudo -S chmod 777 -R /home/{user}/tira-teima/app/static/image/')
        log(f' permissao_imagens_pc - Comando ssh para permissão total da pasta image do terminal {equipamento}', 'info')
        return True
    except Exception:
        log(f' permissao_imagens_pc - Falha catastrófica na execução do comando ssh para permissão total da pasta '
            f'image do terminal {equipamento}. \nMotivo: ', 'exc')
        return False
