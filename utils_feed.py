"""
Módulo de funções para Feed Social
Gerencia posts, curtidas, comentários e sistema de seguir
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from PIL import Image

# Importa função de notificação
from utils import criar_notificacao, buscar_usuario_por_id


# Caminhos dos arquivos
DATA_DIR = "data"
POSTS_FILE = os.path.join(DATA_DIR, "posts.json")
SEGUINDO_FILE = os.path.join(DATA_DIR, "seguindo.json")
CURTIDAS_FILE = os.path.join(DATA_DIR, "curtidas.json")
COMENTARIOS_FILE = os.path.join(DATA_DIR, "comentarios.json")
POSTS_FOTOS_DIR = os.path.join(DATA_DIR, "posts_fotos")


# ============= FUNÇÕES AUXILIARES =============

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


# ============= FUNÇÕES DE POSTS =============

def carregar_posts() -> List[Dict]:
    """Carrega lista de posts"""
    return carregar_json(POSTS_FILE)


def salvar_posts(posts: List[Dict]) -> bool:
    """Salva lista de posts"""
    return salvar_json(POSTS_FILE, posts)


def criar_post(usuario_id: int, texto: str, foto_upload=None) -> Optional[Dict]:
    """Cria um novo post"""
    posts = carregar_posts()
    
    # Gera ID único
    novo_id = max([p.get('id', 0) for p in posts], default=0) + 1
    
    # Salva foto se houver
    foto_nome = ''
    if foto_upload is not None:
        try:
            extensao = foto_upload.name.split('.')[-1]
            foto_nome = f"post_{novo_id}.{extensao}"
            caminho_completo = os.path.join(POSTS_FOTOS_DIR, foto_nome)
            
            img = Image.open(foto_upload)
            img.save(caminho_completo)
        except:
            foto_nome = ''
    
    novo_post = {
        'id': novo_id,
        'usuario_id': usuario_id,
        'texto': texto,
        'foto': foto_nome,
        'data_criacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    posts.append(novo_post)
    salvar_posts(posts)
    return novo_post


def buscar_post_por_id(post_id: int) -> Optional[Dict]:
    """Busca post por ID"""
    posts = carregar_posts()
    for post in posts:
        if post.get('id') == post_id:
            return post
    return None


def buscar_post_por_id(post_id: int) -> Optional[Dict]:
    """Busca um post pelo ID"""
    posts = carregar_posts()
    for post in posts:
        if post.get('id') == post_id:
            return post
    return None


def editar_post(post_id: int, novo_texto: str) -> bool:
    """Edita o texto de um post"""
    posts = carregar_posts()
    
    for i, post in enumerate(posts):
        if post.get('id') == post_id:
            posts[i]['texto'] = novo_texto
            posts[i]['data_edicao'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return salvar_posts(posts)
    
    return False


def excluir_post(post_id: int) -> bool:
    """Exclui um post e seus curtidas/comentários"""
    posts = carregar_posts()
    
    # Remove o post
    for i, post in enumerate(posts):
        if post.get('id') == post_id:
            # Remove foto se existir
            if post.get('foto'):
                caminho_foto = os.path.join(POSTS_FOTOS_DIR, post['foto'])
                if os.path.exists(caminho_foto):
                    try:
                        os.remove(caminho_foto)
                    except:
                        pass
            
            posts.pop(i)
            salvar_posts(posts)
            
            # Remove curtidas do post
            curtidas = carregar_curtidas()
            curtidas_filtradas = [c for c in curtidas if c.get('post_id') != post_id]
            salvar_curtidas(curtidas_filtradas)
            
            # Remove comentários do post
            comentarios = carregar_comentarios()
            comentarios_filtrados = [c for c in comentarios if c.get('post_id') != post_id]
            salvar_comentarios(comentarios_filtrados)
            
            return True
    
    return False


def listar_posts_usuario(usuario_id: int) -> List[Dict]:
    """Lista todos os posts de um usuário"""
    posts = carregar_posts()
    posts_usuario = [p for p in posts if p.get('usuario_id') == usuario_id]
    # Ordena por data (mais recente primeiro)
    posts_usuario.sort(key=lambda x: x.get('data_criacao', ''), reverse=True)
    return posts_usuario


def listar_feed(usuario_id: int, limite: int = 20) -> List[Dict]:
    """Lista posts do feed (quem o usuário segue + próprios posts)"""
    posts = carregar_posts()
    seguindo_ids = listar_ids_seguindo(usuario_id)
    
    # Inclui posts de quem segue + próprios posts
    seguindo_ids.add(usuario_id)
    
    posts_feed = [p for p in posts if p.get('usuario_id') in seguindo_ids]
    
    # Ordena por data (mais recente primeiro)
    posts_feed.sort(key=lambda x: x.get('data_criacao', ''), reverse=True)
    
    # Retorna apenas os N mais recentes
    return posts_feed[:limite]


def carregar_foto_post(foto_nome: str):
    """Carrega foto de um post"""
    if foto_nome:
        caminho = os.path.join(POSTS_FOTOS_DIR, foto_nome)
        if os.path.exists(caminho):
            return Image.open(caminho)
    return None


# ============= FUNÇÕES DE SEGUIR =============

def carregar_seguindo() -> List[Dict]:
    """Carrega lista de relacionamentos de seguir"""
    return carregar_json(SEGUINDO_FILE)


def salvar_seguindo(seguindo: List[Dict]) -> bool:
    """Salva lista de relacionamentos"""
    return salvar_json(SEGUINDO_FILE, seguindo)


def seguir_usuario(seguidor_id: int, seguido_id: int) -> bool:
    """Um usuário segue outro"""
    if seguidor_id == seguido_id:
        return False  # Não pode seguir a si mesmo
    
    seguindo = carregar_seguindo()
    
    # Verifica se já segue
    for rel in seguindo:
        if rel.get('seguidor_id') == seguidor_id and rel.get('seguido_id') == seguido_id:
            return False  # Já está seguindo
    
    # Gera ID único
    novo_id = max([s.get('id', 0) for s in seguindo], default=0) + 1
    
    novo_relacionamento = {
        'id': novo_id,
        'seguidor_id': seguidor_id,
        'seguido_id': seguido_id,
        'data_inicio': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    seguindo.append(novo_relacionamento)
    salvar_seguindo(seguindo)
    
    # Cria notificação para quem foi seguido
    seguidor = buscar_usuario_por_id(seguidor_id)
    nome_seguidor = seguidor.get('apelido_jogador') or seguidor.get('nome') or seguidor.get('login')
    
    criar_notificacao(
        usuario_id=seguido_id,
        tipo='novo_seguidor',
        mensagem=f'{nome_seguidor} começou a seguir você!',
        dados={'seguidor_id': seguidor_id}
    )
    
    return True


def deixar_seguir(seguidor_id: int, seguido_id: int) -> bool:
    """Um usuário deixa de seguir outro"""
    seguindo = carregar_seguindo()
    
    for i, rel in enumerate(seguindo):
        if rel.get('seguidor_id') == seguidor_id and rel.get('seguido_id') == seguido_id:
            seguindo.pop(i)
            return salvar_seguindo(seguindo)
    
    return False


def esta_seguindo(seguidor_id: int, seguido_id: int) -> bool:
    """Verifica se um usuário está seguindo outro"""
    seguindo = carregar_seguindo()
    
    for rel in seguindo:
        if rel.get('seguidor_id') == seguidor_id and rel.get('seguido_id') == seguido_id:
            return True
    
    return False


def listar_ids_seguindo(usuario_id: int) -> set:
    """Retorna IDs de usuários que o usuário segue"""
    seguindo = carregar_seguindo()
    return {rel.get('seguido_id') for rel in seguindo if rel.get('seguidor_id') == usuario_id}


def listar_ids_seguidores(usuario_id: int) -> set:
    """Retorna IDs de usuários que seguem o usuário"""
    seguindo = carregar_seguindo()
    return {rel.get('seguidor_id') for rel in seguindo if rel.get('seguido_id') == usuario_id}


def contar_seguindo(usuario_id: int) -> int:
    """Conta quantos usuários o usuário segue"""
    return len(listar_ids_seguindo(usuario_id))


def contar_seguidores(usuario_id: int) -> int:
    """Conta quantos seguidores o usuário tem"""
    return len(listar_ids_seguidores(usuario_id))


# ============= FUNÇÕES DE CURTIDAS =============

def carregar_curtidas() -> List[Dict]:
    """Carrega lista de curtidas"""
    return carregar_json(CURTIDAS_FILE)


def salvar_curtidas(curtidas: List[Dict]) -> bool:
    """Salva lista de curtidas"""
    return salvar_json(CURTIDAS_FILE, curtidas)


def curtir_post(post_id: int, usuario_id: int) -> bool:
    """Usuário curte um post"""
    curtidas = carregar_curtidas()
    
    # Verifica se já curtiu
    for curtida in curtidas:
        if curtida.get('post_id') == post_id and curtida.get('usuario_id') == usuario_id:
            return False  # Já curtiu
    
    # Gera ID único
    novo_id = max([c.get('id', 0) for c in curtidas], default=0) + 1
    
    nova_curtida = {
        'id': novo_id,
        'post_id': post_id,
        'usuario_id': usuario_id,
        'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    curtidas.append(nova_curtida)
    salvar_curtidas(curtidas)
    
    # Cria notificação para o dono do post (se não for ele mesmo curtindo)
    post = buscar_post_por_id(post_id)
    if post and post['usuario_id'] != usuario_id:
        usuario = buscar_usuario_por_id(usuario_id)
        nome_usuario = usuario.get('apelido_jogador') or usuario.get('nome') or usuario.get('login')
        
        # Pega preview do post
        data_post = datetime.strptime(post['data_criacao'], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
        texto_preview = post.get('texto', '')[:10] + '...' if post.get('texto') and len(post.get('texto', '')) > 10 else post.get('texto', '[foto]')
        
        criar_notificacao(
            usuario_id=post['usuario_id'],
            tipo='curtida_post',
            mensagem=f'{nome_usuario} curtiu sua postagem de {data_post}: "{texto_preview}"',
            dados={'post_id': post_id, 'usuario_id': usuario_id}
        )
    
    return True


def descurtir_post(post_id: int, usuario_id: int) -> bool:
    """Usuário remove curtida de um post"""
    curtidas = carregar_curtidas()
    
    for i, curtida in enumerate(curtidas):
        if curtida.get('post_id') == post_id and curtida.get('usuario_id') == usuario_id:
            curtidas.pop(i)
            return salvar_curtidas(curtidas)
    
    return False


def usuario_curtiu(post_id: int, usuario_id: int) -> bool:
    """Verifica se usuário curtiu um post"""
    curtidas = carregar_curtidas()
    
    for curtida in curtidas:
        if curtida.get('post_id') == post_id and curtida.get('usuario_id') == usuario_id:
            return True
    
    return False


def contar_curtidas(post_id: int) -> int:
    """Conta quantas curtidas um post tem"""
    curtidas = carregar_curtidas()
    return sum(1 for c in curtidas if c.get('post_id') == post_id)


# ============= FUNÇÕES DE COMENTÁRIOS =============

def carregar_comentarios() -> List[Dict]:
    """Carrega lista de comentários"""
    return carregar_json(COMENTARIOS_FILE)


def salvar_comentarios(comentarios: List[Dict]) -> bool:
    """Salva lista de comentários"""
    return salvar_json(COMENTARIOS_FILE, comentarios)


def adicionar_comentario(post_id: int, usuario_id: int, texto: str) -> Optional[Dict]:
    """Adiciona um comentário em um post"""
    comentarios = carregar_comentarios()
    
    # Gera ID único
    novo_id = max([c.get('id', 0) for c in comentarios], default=0) + 1
    
    novo_comentario = {
        'id': novo_id,
        'post_id': post_id,
        'usuario_id': usuario_id,
        'texto': texto,
        'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    comentarios.append(novo_comentario)
    salvar_comentarios(comentarios)
    
    # Cria notificação para o dono do post (se não for ele mesmo comentando)
    post = buscar_post_por_id(post_id)
    if post and post['usuario_id'] != usuario_id:
        usuario = buscar_usuario_por_id(usuario_id)
        nome_usuario = usuario.get('apelido_jogador') or usuario.get('nome') or usuario.get('login')
        
        # Pega preview do post
        data_post = datetime.strptime(post['data_criacao'], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
        texto_preview = post.get('texto', '')[:20] + '...' if post.get('texto') and len(post.get('texto', '')) > 20 else post.get('texto', '[foto]')
        
        criar_notificacao(
            usuario_id=post['usuario_id'],
            tipo='comentario_post',
            mensagem=f'{nome_usuario} comentou sua postagem de {data_post}: "{texto_preview}"',
            dados={'post_id': post_id, 'comentario_id': novo_id}
        )
    
    return novo_comentario


def excluir_comentario(comentario_id: int) -> bool:
    """Exclui um comentário"""
    comentarios = carregar_comentarios()
    
    for i, comentario in enumerate(comentarios):
        if comentario.get('id') == comentario_id:
            comentarios.pop(i)
            return salvar_comentarios(comentarios)
    
    return False


def listar_comentarios_post(post_id: int) -> List[Dict]:
    """Lista comentários de um post"""
    comentarios = carregar_comentarios()
    comentarios_post = [c for c in comentarios if c.get('post_id') == post_id]
    # Ordena por data (mais antigo primeiro)
    comentarios_post.sort(key=lambda x: x.get('data', ''))
    return comentarios_post


def contar_comentarios(post_id: int) -> int:
    """Conta quantos comentários um post tem"""
    comentarios = carregar_comentarios()
    return sum(1 for c in comentarios if c.get('post_id') == post_id)
