"""
Módulo de funções utilitárias para a Rede Social de Futebol Society
"""
import json
import os
from datetime import datetime, time
from typing import List, Dict, Optional
import random


# Caminhos dos arquivos JSON
DATA_DIR = "data"
USUARIOS_FILE = os.path.join(DATA_DIR, "usuarios.json")
JOGOS_FILE = os.path.join(DATA_DIR, "jogos.json")
CAMPOS_FILE = os.path.join(DATA_DIR, "campos.json")
INSCRICOES_FILE = os.path.join(DATA_DIR, "inscricoes.json")
NOTIFICACOES_FILE = os.path.join(DATA_DIR, "notificacoes.json")
FOTOS_DIR = os.path.join(DATA_DIR, "fotos")


# ============= FUNÇÕES DE CARREGAMENTO E SALVAMENTO =============

def carregar_json(arquivo: str) -> List[Dict]:
    """Carrega dados de um arquivo JSON"""
    if not os.path.exists(arquivo):
        return []
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []


def salvar_json(arquivo: str, dados: List[Dict]) -> bool:
    """Salva dados em um arquivo JSON"""
    try:
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


# ============= FUNÇÕES DE USUÁRIOS =============

def carregar_usuarios() -> List[Dict]:
    """Carrega lista de usuários"""
    return carregar_json(USUARIOS_FILE)


def salvar_usuarios(usuarios: List[Dict]) -> bool:
    """Salva lista de usuários"""
    return salvar_json(USUARIOS_FILE, usuarios)


def buscar_usuario_por_login(login: str) -> Optional[Dict]:
    """Busca usuário por login (nome/email/apelido)"""
    usuarios = carregar_usuarios()
    for usuario in usuarios:
        if usuario.get('login', '').lower() == login.lower():
            return usuario
    return None


def buscar_usuario_por_id(user_id: int) -> Optional[Dict]:
    """Busca usuário por ID"""
    usuarios = carregar_usuarios()
    for usuario in usuarios:
        if usuario.get('id') == user_id:
            return usuario
    return None


def buscar_usuario_por_telefone(telefone: str) -> Optional[Dict]:
    """Busca usuário por telefone"""
    usuarios = carregar_usuarios()
    for usuario in usuarios:
        if usuario.get('telefone') == telefone:
            return usuario
    return None


def criar_usuario(login: str, senha: str, telefone: str) -> Dict:
    """Cria um novo usuário"""
    usuarios = carregar_usuarios()
    
    # Gera ID único
    novo_id = max([u.get('id', 0) for u in usuarios], default=0) + 1
    
    novo_usuario = {
        'id': novo_id,
        'login': login,
        'senha': senha,
        'telefone': telefone,
        'nome': '',
        'apelido_jogador': '',
        'foto': ''
    }
    
    usuarios.append(novo_usuario)
    salvar_usuarios(usuarios)
    return novo_usuario


def atualizar_usuario(user_id: int, dados: Dict) -> bool:
    """Atualiza dados de um usuário"""
    usuarios = carregar_usuarios()
    
    for i, usuario in enumerate(usuarios):
        if usuario.get('id') == user_id:
            # Atualiza apenas os campos fornecidos
            for chave, valor in dados.items():
                if chave != 'id':  # Não permite alterar o ID
                    usuarios[i][chave] = valor
            return salvar_usuarios(usuarios)
    
    return False


def gerar_nova_senha() -> str:
    """Gera uma senha aleatória de 4 dígitos"""
    return str(random.randint(1000, 9999))


# ============= FUNÇÕES DE CAMPOS =============

def carregar_campos() -> List[Dict]:
    """Carrega lista de campos"""
    return carregar_json(CAMPOS_FILE)


def buscar_campo_por_id(campo_id: int) -> Optional[Dict]:
    """Busca campo por ID"""
    campos = carregar_campos()
    for campo in campos:
        if campo.get('id') == campo_id:
            return campo
    return None


# ============= FUNÇÕES DE JOGOS =============

def carregar_jogos() -> List[Dict]:
    """Carrega lista de jogos"""
    return carregar_json(JOGOS_FILE)


def salvar_jogos(jogos: List[Dict]) -> bool:
    """Salva lista de jogos"""
    return salvar_json(JOGOS_FILE, jogos)


def buscar_jogo_por_id(jogo_id: int) -> Optional[Dict]:
    """Busca jogo por ID"""
    jogos = carregar_jogos()
    for jogo in jogos:
        if jogo.get('id') == jogo_id:
            return jogo
    return None


def verificar_conflito_horario(campo_id: int, data: str, hora_inicio: str, hora_fim: str, jogo_id_excluir: Optional[int] = None) -> bool:
    """
    Verifica se há conflito de horário para um campo em uma data específica
    Retorna True se houver conflito, False caso contrário
    """
    jogos = carregar_jogos()
    
    # Converte strings de horário para objetos time para comparação
    inicio = datetime.strptime(hora_inicio, "%H:%M").time()
    fim = datetime.strptime(hora_fim, "%H:%M").time()
    
    for jogo in jogos:
        # Ignora o próprio jogo (útil para edição)
        if jogo_id_excluir and jogo.get('id') == jogo_id_excluir:
            continue
            
        # Verifica se é o mesmo campo e mesma data
        if jogo.get('campo_id') == campo_id and jogo.get('data') == data:
            jogo_inicio = datetime.strptime(jogo.get('hora_inicio'), "%H:%M").time()
            jogo_fim = datetime.strptime(jogo.get('hora_fim'), "%H:%M").time()
            
            # Verifica sobreposição de horários
            # Há conflito se: novo início < jogo fim E novo fim > jogo início
            if inicio < jogo_fim and fim > jogo_inicio:
                return True
    
    return False


def criar_jogo(organizador_id: int, campo_id: int, data: str, hora_inicio: str, 
               hora_fim: str, valor: float, vagas: int) -> Optional[Dict]:
    """Cria um novo jogo"""
    
    # Verifica conflito de horário
    if verificar_conflito_horario(campo_id, data, hora_inicio, hora_fim):
        return None
    
    jogos = carregar_jogos()
    
    # Gera ID único
    novo_id = max([j.get('id', 0) for j in jogos], default=0) + 1
    
    novo_jogo = {
        'id': novo_id,
        'organizador_id': organizador_id,
        'campo_id': campo_id,
        'data': data,
        'hora_inicio': hora_inicio,
        'hora_fim': hora_fim,
        'valor': valor,
        'vagas_total': vagas,
        'vagas_ocupadas': 0,
        'status': 'ativo'  # ativo, cancelado, finalizado
    }
    
    jogos.append(novo_jogo)
    salvar_jogos(jogos)
    return novo_jogo


def listar_jogos_por_organizador(organizador_id: int) -> List[Dict]:
    """Lista todos os jogos criados por um organizador"""
    jogos = carregar_jogos()
    return [j for j in jogos if j.get('organizador_id') == organizador_id]


def listar_jogos_futuros(data_inicial: Optional[str] = None) -> List[Dict]:
    """Lista jogos futuros a partir de uma data"""
    jogos = carregar_jogos()
    hoje = datetime.now().strftime("%Y-%m-%d")
    
    data_filtro = data_inicial if data_inicial else hoje
    
    jogos_futuros = [j for j in jogos if j.get('data', '') >= data_filtro and j.get('status') == 'ativo']
    
    # Ordena por data e hora
    jogos_futuros.sort(key=lambda x: (x.get('data', ''), x.get('hora_inicio', '')))
    
    return jogos_futuros


# ============= FUNÇÕES DE INSCRIÇÕES =============

def carregar_inscricoes() -> List[Dict]:
    """Carrega lista de inscrições"""
    return carregar_json(INSCRICOES_FILE)


def salvar_inscricoes(inscricoes: List[Dict]) -> bool:
    """Salva lista de inscrições"""
    return salvar_json(INSCRICOES_FILE, inscricoes)


def criar_inscricao(jogo_id: int, jogador_id: int) -> Optional[Dict]:
    """Cria uma nova inscrição"""
    inscricoes = carregar_inscricoes()
    
    # Verifica se já existe inscrição
    for insc in inscricoes:
        if insc.get('jogo_id') == jogo_id and insc.get('jogador_id') == jogador_id:
            return None
    
    # Gera ID único
    novo_id = max([i.get('id', 0) for i in inscricoes], default=0) + 1
    
    nova_inscricao = {
        'id': novo_id,
        'jogo_id': jogo_id,
        'jogador_id': jogador_id,
        'status': 'pendente',  # pendente, aprovada, reprovada, cancelada
        'data_inscricao': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    inscricoes.append(nova_inscricao)
    salvar_inscricoes(inscricoes)
    
    # Cria notificação para o organizador
    jogo = buscar_jogo_por_id(jogo_id)
    if jogo:
        criar_notificacao(
            usuario_id=jogo['organizador_id'],
            tipo='nova_inscricao',
            mensagem=f'Novo jogador quer participar do seu jogo!',
            dados={'jogo_id': jogo_id, 'inscricao_id': novo_id}
        )
    
    return nova_inscricao


def listar_inscricoes_por_jogo(jogo_id: int, status: Optional[str] = None) -> List[Dict]:
    """Lista inscrições de um jogo, opcionalmente filtrando por status"""
    inscricoes = carregar_inscricoes()
    resultado = [i for i in inscricoes if i.get('jogo_id') == jogo_id]
    
    if status:
        resultado = [i for i in resultado if i.get('status') == status]
    
    return resultado


def listar_inscricoes_por_jogador(jogador_id: int) -> List[Dict]:
    """Lista todas as inscrições de um jogador"""
    inscricoes = carregar_inscricoes()
    return [i for i in inscricoes if i.get('jogador_id') == jogador_id]


def atualizar_status_inscricao(inscricao_id: int, novo_status: str) -> bool:
    """Atualiza o status de uma inscrição"""
    inscricoes = carregar_inscricoes()
    
    for i, insc in enumerate(inscricoes):
        if insc.get('id') == inscricao_id:
            inscricoes[i]['status'] = novo_status
            
            # Atualiza vagas ocupadas se aprovado
            if novo_status == 'aprovada':
                atualizar_vagas_jogo(insc['jogo_id'], 1)
                
                # Notifica jogador
                criar_notificacao(
                    usuario_id=insc['jogador_id'],
                    tipo='inscricao_aprovada',
                    mensagem=f'Sua inscrição foi aprovada!',
                    dados={'jogo_id': insc['jogo_id']}
                )
            elif novo_status == 'reprovada':
                # Notifica jogador
                criar_notificacao(
                    usuario_id=insc['jogador_id'],
                    tipo='inscricao_reprovada',
                    mensagem=f'Sua inscrição foi recusada.',
                    dados={'jogo_id': insc['jogo_id']}
                )
            elif novo_status == 'cancelada':
                # Se estava aprovada, libera vaga
                if insc.get('status') == 'aprovada':
                    atualizar_vagas_jogo(insc['jogo_id'], -1)
                
                # Notifica organizador
                jogo = buscar_jogo_por_id(insc['jogo_id'])
                if jogo:
                    criar_notificacao(
                        usuario_id=jogo['organizador_id'],
                        tipo='inscricao_cancelada',
                        mensagem=f'Um jogador cancelou a inscrição.',
                        dados={'jogo_id': insc['jogo_id']}
                    )
            
            return salvar_inscricoes(inscricoes)
    
    return False


def remover_jogador_inscricao(inscricao_id: int) -> bool:
    """Remove um jogador (organizador removendo)"""
    inscricoes = carregar_inscricoes()
    
    for i, insc in enumerate(inscricoes):
        if insc.get('id') == inscricao_id:
            # Libera vaga
            atualizar_vagas_jogo(insc['jogo_id'], -1)
            
            # Notifica jogador removido
            criar_notificacao(
                usuario_id=insc['jogador_id'],
                tipo='removido_jogo',
                mensagem=f'Você foi removido de um jogo pelo organizador.',
                dados={'jogo_id': insc['jogo_id']}
            )
            
            # Remove a inscrição
            inscricoes.pop(i)
            return salvar_inscricoes(inscricoes)
    
    return False


def atualizar_vagas_jogo(jogo_id: int, incremento: int) -> bool:
    """Atualiza o número de vagas ocupadas de um jogo"""
    jogos = carregar_jogos()
    
    for i, jogo in enumerate(jogos):
        if jogo.get('id') == jogo_id:
            jogos[i]['vagas_ocupadas'] = jogos[i].get('vagas_ocupadas', 0) + incremento
            # Garante que não fique negativo
            if jogos[i]['vagas_ocupadas'] < 0:
                jogos[i]['vagas_ocupadas'] = 0
            return salvar_jogos(jogos)
    
    return False


# ============= FUNÇÕES DE NOTIFICAÇÕES =============

def carregar_notificacoes() -> List[Dict]:
    """Carrega lista de notificações"""
    return carregar_json(NOTIFICACOES_FILE)


def salvar_notificacoes(notificacoes: List[Dict]) -> bool:
    """Salva lista de notificações"""
    return salvar_json(NOTIFICACOES_FILE, notificacoes)


def criar_notificacao(usuario_id: int, tipo: str, mensagem: str, dados: Optional[Dict] = None) -> Dict:
    """Cria uma nova notificação"""
    notificacoes = carregar_notificacoes()
    
    # Gera ID único
    novo_id = max([n.get('id', 0) for n in notificacoes], default=0) + 1
    
    nova_notificacao = {
        'id': novo_id,
        'usuario_id': usuario_id,
        'tipo': tipo,
        'mensagem': mensagem,
        'dados': dados or {},
        'lida': False,
        'data_criacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    notificacoes.append(nova_notificacao)
    salvar_notificacoes(notificacoes)
    return nova_notificacao


def listar_notificacoes_usuario(usuario_id: int, apenas_nao_lidas: bool = False) -> List[Dict]:
    """Lista notificações de um usuário"""
    notificacoes = carregar_notificacoes()
    resultado = [n for n in notificacoes if n.get('usuario_id') == usuario_id]
    
    if apenas_nao_lidas:
        resultado = [n for n in resultado if not n.get('lida', False)]
    
    # Ordena por data (mais recente primeiro)
    resultado.sort(key=lambda x: x.get('data_criacao', ''), reverse=True)
    
    return resultado


def contar_notificacoes_nao_lidas(usuario_id: int) -> int:
    """Conta notificações não lidas de um usuário"""
    notificacoes = listar_notificacoes_usuario(usuario_id, apenas_nao_lidas=True)
    return len(notificacoes)


def marcar_notificacao_lida(notificacao_id: int) -> bool:
    """Marca uma notificação como lida"""
    notificacoes = carregar_notificacoes()
    
    for i, notif in enumerate(notificacoes):
        if notif.get('id') == notificacao_id:
            notificacoes[i]['lida'] = True
            return salvar_notificacoes(notificacoes)
    
    return False


def marcar_todas_lidas(usuario_id: int) -> bool:
    """Marca todas as notificações de um usuário como lidas"""
    notificacoes = carregar_notificacoes()
    
    alterado = False
    for i, notif in enumerate(notificacoes):
        if notif.get('usuario_id') == usuario_id and not notif.get('lida', False):
            notificacoes[i]['lida'] = True
            alterado = True
    
    if alterado:
        return salvar_notificacoes(notificacoes)
    
    return False
