"""
Rede Social de Futebol Society
MVP - Aplicação Streamlit
"""
import streamlit as st
import os
from datetime import datetime, date, timedelta
from PIL import Image
import io
import base64

# Importa funções utilitárias
from utils import (
    # Usuários
    buscar_usuario_por_login, criar_usuario, buscar_usuario_por_id,
    buscar_usuario_por_telefone, atualizar_usuario, gerar_nova_senha,
    # Campos
    carregar_campos, buscar_campo_por_id,
    # Jogos
    carregar_jogos, criar_jogo, buscar_jogo_por_id, listar_jogos_por_organizador,
    listar_jogos_futuros, verificar_conflito_horario, excluir_jogo,
    # Inscrições
    criar_inscricao, listar_inscricoes_por_jogo, listar_inscricoes_por_jogador,
    atualizar_status_inscricao, remover_jogador_inscricao,
    # Notificações
    listar_notificacoes_usuario, contar_notificacoes_nao_lidas,
    marcar_notificacao_lida, marcar_todas_lidas,
    # Paths
    FOTOS_DIR
)

# Importa funções do feed
from utils_feed import (
    # Posts
    criar_post, editar_post, excluir_post, listar_posts_usuario,
    listar_feed, buscar_post_por_id, carregar_foto_post,
    # Seguir
    seguir_usuario, deixar_seguir, esta_seguindo, listar_ids_seguindo,
    listar_ids_seguidores, contar_seguindo, contar_seguidores,
    # Curtidas
    curtir_post, descurtir_post, usuario_curtiu, contar_curtidas,
    # Comentários
    adicionar_comentario, excluir_comentario, listar_comentarios_post,
    contar_comentarios
)


# ============= CONFIGURAÇÕES DA PÁGINA =============

st.set_page_config(
    page_title="Futebol Society",
    page_icon="⚽",
    layout="wide"
)

# ============= CARREGA CSS CUSTOMIZADO =============

def carregar_css():
    """Carrega arquivo CSS customizado"""
    try:
        with open('style.css', 'r', encoding='utf-8') as f:
            css = f.read()
        st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # Se não encontrar o arquivo, continua sem CSS

carregar_css()


# ============= INICIALIZAÇÃO DO SESSION STATE =============

if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = None

if 'pagina_atual' not in st.session_state:
    st.session_state.pagina_atual = 'login'


# ============= FUNÇÕES AUXILIARES =============

def salvar_foto_perfil(usuario_id: int, imagem_upload) -> str:
    """Salva foto de perfil e retorna o caminho"""
    if imagem_upload is not None:
        # Cria nome único para a foto
        extensao = imagem_upload.name.split('.')[-1]
        nome_arquivo = f"user_{usuario_id}.{extensao}"
        caminho_completo = os.path.join(FOTOS_DIR, nome_arquivo)
        
        # Salva a imagem
        try:
            img = Image.open(imagem_upload)
            img.save(caminho_completo)
            return nome_arquivo
        except:
            return ''
    return ''


def carregar_foto_perfil(foto_nome: str):
    """Carrega e exibe foto de perfil"""
    if foto_nome:
        caminho = os.path.join(FOTOS_DIR, foto_nome)
        if os.path.exists(caminho):
            return Image.open(caminho)
    return None


def formatar_data_br(data_str: str) -> str:
    """Converte data YYYY-MM-DD para DD/MM/YYYY"""
    try:
        data_obj = datetime.strptime(data_str, "%Y-%m-%d")
        return data_obj.strftime("%d/%m/%Y")
    except:
        return data_str


def logout():
    """Realiza logout do usuário"""
    st.session_state.usuario_logado = None
    st.session_state.pagina_atual = 'login'
    st.rerun()


def gerar_horarios_30min():
    """Gera lista de horários de 30 em 30 minutos"""
    horarios = []
    for hora in range(24):
        horarios.append(f"{hora:02d}:00")
        horarios.append(f"{hora:02d}:30")
    return horarios


# ============= TELA DE LOGIN E CADASTRO =============

def tela_login():
    """Tela de login e cadastro"""
    
    st.title("⚽ Futebol Society")
    st.subheader("Conecte-se e jogue!")
    
    # Tabs para Login e Cadastro
    tab_login, tab_cadastro, tab_recuperar = st.tabs(["Login", "Cadastro", "Recuperar Senha"])
    
    # === TAB LOGIN ===
    with tab_login:
        st.write("### Faça login")
        
        with st.form("form_login"):
            login = st.text_input("Nome ou Apelido")
            senha = st.text_input("Senha (4 dígitos)", type="password", max_chars=4)
            
            submit = st.form_submit_button("Entrar", use_container_width=True)
            
            if submit:
                if not login or not senha:
                    st.error("Preencha todos os campos!")
                elif len(senha) != 4 or not senha.isdigit():
                    st.error("A senha deve ter exatamente 4 dígitos!")
                else:
                    usuario = buscar_usuario_por_login(login)
                    
                    if usuario and usuario.get('senha') == senha:
                        st.session_state.usuario_logado = usuario
                        st.session_state.pagina_atual = 'perfil'
                        st.success("Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Login ou senha incorretos!")
    
    # === TAB CADASTRO ===
    with tab_cadastro:
        st.write("### Criar nova conta")
        
        with st.form("form_cadastro"):
            novo_login = st.text_input("Nome ou Apelido")
            novo_telefone = st.text_input("Telefone", placeholder="Ex: 11 98765-4321")
            nova_senha = st.text_input("Senha (4 dígitos)", type="password", max_chars=4)
            confirma_senha = st.text_input("Confirme a senha", type="password", max_chars=4)
            
            submit_cadastro = st.form_submit_button("Cadastrar", use_container_width=True)
            
            if submit_cadastro:
                if not novo_login or not novo_telefone or not nova_senha:
                    st.error("Preencha todos os campos!")
                elif len(nova_senha) != 4 or not nova_senha.isdigit():
                    st.error("A senha deve ter exatamente 4 dígitos numéricos!")
                elif nova_senha != confirma_senha:
                    st.error("As senhas não coincidem!")
                else:
                    # Verifica se telefone já existe
                    if buscar_usuario_por_telefone(novo_telefone):
                        st.error("Este telefone já está cadastrado!")
                    # Verifica se login já existe
                    elif buscar_usuario_por_login(novo_login):
                        st.error("Este nome/apelido já está em uso!")
                    else:
                        # Cria usuário
                        usuario = criar_usuario(novo_login, nova_senha, novo_telefone)
                        st.success("Cadastro realizado com sucesso! volte a tela de login e Faça seu login.")
    
    # === TAB RECUPERAR SENHA ===
    with tab_recuperar:
        st.write("### Esqueceu sua senha?")
        st.info("📞 Entre em contato com o suporte: **1234-5678**")


# ============= SIDEBAR COM MENU =============

def mostrar_sidebar():
    """Mostra sidebar com menu de navegação"""
    
    usuario = st.session_state.usuario_logado
    
    with st.sidebar:
                
        # Foto e nome do usuário (centralizado)
        foto = carregar_foto_perfil(usuario.get('foto', ''))
        if foto:
            st.image(foto, use_container_width=True)
        
        # Nome centralizado
        st.markdown(f"<h4 style='text-align: center;'>{usuario.get('apelido_jogador') or usuario.get('login')}</h4>", unsafe_allow_html=True)
        
        # Notificações
        num_notificacoes = contar_notificacoes_nao_lidas(usuario['id'])
        if num_notificacoes > 0:
            st.warning(f"{num_notificacoes} Você tem notificação nova!")
        
        st.divider()
        
        # Menu
        if st.button("Perfil", use_container_width=True):
            st.session_state.pagina_atual = 'perfil'
            st.rerun()
        
        if st.button("Feed", use_container_width=True):
            st.session_state.pagina_atual = 'feed'
            st.rerun()
        
        if st.button("Organizador", use_container_width=True):
            st.session_state.pagina_atual = 'organizador'
            st.rerun()
        
        if st.button("Jogador", use_container_width=True):
            st.session_state.pagina_atual = 'jogador'
            st.rerun()
        
        if st.button("Notificações", use_container_width=True):
            st.session_state.pagina_atual = 'notificacoes'
            st.rerun()
        
        st.divider()
        
        if st.button("Sair", use_container_width=True):
            logout()


# ============= PÁGINA DE PERFIL =============

def pagina_perfil():
    """Página de perfil do usuário"""
    
    usuario = st.session_state.usuario_logado
    
    st.title("Meu Perfil")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        
        foto = carregar_foto_perfil(usuario.get('foto', ''))
        if foto:
            st.image(foto, width=200)
        else:
            st.info("Sem foto")
        
        upload_foto = st.file_uploader("Enviar nova foto", type=['jpg', 'jpeg', 'png'])
        
        if upload_foto:
            if st.button("Salvar Foto"):
                nome_foto = salvar_foto_perfil(usuario['id'], upload_foto)
                if nome_foto:
                    atualizar_usuario(usuario['id'], {'foto': nome_foto})
                    st.success("Foto atualizada!")
                    st.session_state.usuario_logado = buscar_usuario_por_id(usuario['id'])
                    st.rerun()
    
    with col2:
        st.subheader("Informações Pessoais")
        
        with st.form("form_perfil"):
            nome = st.text_input("Nome Completo", value=usuario.get('nome', ''))
            apelido = st.text_input("Apelido de Jogador", value=usuario.get('apelido_jogador', ''))
            telefone = st.text_input("Telefone", value=usuario.get('telefone', ''))
            
            st.info(f"**Login:** {usuario.get('login')}")
            
            submit = st.form_submit_button("Salvar Alterações", use_container_width=True)
            
            if submit:
                # Verifica se telefone mudou e se já está em uso
                if telefone != usuario.get('telefone', ''):
                    usuario_existente = buscar_usuario_por_telefone(telefone)
                    if usuario_existente and usuario_existente['id'] != usuario['id']:
                        st.error("Este telefone já está cadastrado por outro usuário!")
                        return
                
                dados_atualizados = {
                    'nome': nome,
                    'apelido_jogador': apelido,
                    'telefone': telefone
                }
                
                if atualizar_usuario(usuario['id'], dados_atualizados):
                    st.success("Perfil atualizado com sucesso!")
                    st.session_state.usuario_logado = buscar_usuario_por_id(usuario['id'])
                    st.rerun()
                else:
                    st.error("Erro ao atualizar perfil!")


# ============= PÁGINA ORGANIZADOR =============

def pagina_organizador():
    """Página do organizador"""
    
    usuario = st.session_state.usuario_logado
    
    st.title("📋 Organizador de Jogos")
    
    # Tabs
    tab_criar, tab_meus_jogos = st.tabs(["Criar Jogo", "Meus Jogos"])
    
    # === TAB CRIAR JOGO ===
    with tab_criar:
        st.subheader("Organizar Novo Jogo")
        
        campos = carregar_campos()
        
        # Select box de campos FORA do form para atualizar dinamicamente
        opcoes_campos = {f"{c['nome']} - {c['formato']} ({c['tipo']})": c['id'] for c in campos}
        campo_selecionado = st.selectbox("Campo", options=list(opcoes_campos.keys()))
        campo_id = opcoes_campos[campo_selecionado]
        
        # Mostra info do campo selecionado
        campo_info = buscar_campo_por_id(campo_id)
        st.info(f"📍 {campo_info['endereco']} | {campo_info['dimensoes']} | {campo_info['jogadores_por_time']} jogadores por time")
        
        with st.form("form_criar_jogo"):
            
            col1, col2 = st.columns(2)
            
            with col1:
                data_jogo = st.date_input("Data do Jogo", min_value=date.today())
                horarios = gerar_horarios_30min()
                hora_inicio = st.selectbox("Horário de Início", horarios, index=20)  # Default 10:00
            
            with col2:
                valor = st.number_input("Valor por Pessoa (R$)", min_value=0.0, step=5.0)
                hora_fim = st.selectbox("Horário de Término", horarios, index=23)  # Default 11:30
            
            vagas = st.number_input("Número de Vagas", min_value=1, max_value=campo_info['jogadores_por_time']*5, value=campo_info['jogadores_por_time']*3)
            
            submit = st.form_submit_button("Criar Jogo", use_container_width=True)
            
            if submit:
                data_str = data_jogo.strftime("%Y-%m-%d")
                hora_inicio_str = hora_inicio
                hora_fim_str = hora_fim
                
                # Validações
                hora_inicio_time = datetime.strptime(hora_inicio, "%H:%M").time()
                hora_fim_time = datetime.strptime(hora_fim, "%H:%M").time()
                
                if hora_fim_time <= hora_inicio_time:
                    st.error("O horário de término deve ser após o horário de início!")
                elif verificar_conflito_horario(campo_id, data_str, hora_inicio_str, hora_fim_str):
                    st.error("⚠️ Este campo já está ocupado neste horário!")
                else:
                    jogo = criar_jogo(
                        organizador_id=usuario['id'],
                        campo_id=campo_id,
                        data=data_str,
                        hora_inicio=hora_inicio_str,
                        hora_fim=hora_fim_str,
                        valor=valor,
                        vagas=vagas
                    )
                    
                    if jogo:
                        st.success("✅ Jogo criado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao criar jogo!")
    
    # === TAB MEUS JOGOS ===
    with tab_meus_jogos:
        st.subheader("Jogos que Organizei")
        
        meus_jogos = listar_jogos_por_organizador(usuario['id'])
        
        if not meus_jogos:
            st.info("Você ainda não organizou nenhum jogo.")
        else:
            for jogo in meus_jogos:
                campo = buscar_campo_por_id(jogo['campo_id'])
                
                with st.expander(f"⚽ {campo['nome']} - {formatar_data_br(jogo['data'])} às {jogo['hora_inicio']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Data:** {formatar_data_br(jogo['data'])}")
                        st.write(f"**Horário:** {jogo['hora_inicio']} - {jogo['hora_fim']}")
                    
                    with col2:
                        st.write(f"**Campo:** {campo['nome']}")
                        st.write(f"**Valor:** R$ {jogo['valor']:.2f}")
                    
                    with col3:
                        vagas_disponiveis = jogo['vagas_total'] - jogo['vagas_ocupadas']
                        st.write(f"**Vagas:** {jogo['vagas_ocupadas']}/{jogo['vagas_total']}")
                        
                        if vagas_disponiveis == 0:
                            st.success("🎉 Lotado!")
                        else:
                            st.info(f"{vagas_disponiveis} vaga(s) disponível(eis)")
                    
                    st.divider()
                    
                    # Inscrições pendentes
                    inscricoes_pendentes = listar_inscricoes_por_jogo(jogo['id'], 'pendente')
                    
                    if inscricoes_pendentes:
                        st.write("**⏳ Solicitações Pendentes:**")
                        
                        for inscricao in inscricoes_pendentes:
                            jogador = buscar_usuario_por_id(inscricao['jogador_id'])
                            
                            col_a, col_b, col_c = st.columns([2, 1, 1])
                            
                            with col_a:
                                nome_jogador = jogador.get('apelido_jogador') or jogador.get('nome') or jogador.get('login')
                                st.write(f"👤 {nome_jogador}")
                                st.caption(f"Tel: {jogador.get('telefone', 'N/A')}")
                            
                            with col_b:
                                if st.button("✅ Aprovar", key=f"aprovar_{inscricao['id']}"):
                                    if jogo['vagas_ocupadas'] < jogo['vagas_total']:
                                        atualizar_status_inscricao(inscricao['id'], 'aprovada')
                                        st.success("Aprovado!")
                                        st.rerun()
                                    else:
                                        st.error("Sem vagas!")
                            
                            with col_c:
                                if st.button("❌ Recusar", key=f"recusar_{inscricao['id']}"):
                                    atualizar_status_inscricao(inscricao['id'], 'reprovada')
                                    st.success("Recusado!")
                                    st.rerun()
                    
                    # Jogadores aprovados
                    inscricoes_aprovadas = listar_inscricoes_por_jogo(jogo['id'], 'aprovada')
                    
                    if inscricoes_aprovadas:
                        st.write("**✅ Jogadores Confirmados:**")
                        
                        # Enumera de baixo para cima (inverte a lista)
                        for idx, inscricao in enumerate(reversed(inscricoes_aprovadas), 1):
                            jogador = buscar_usuario_por_id(inscricao['jogador_id'])
                            
                            col_a, col_b = st.columns([3, 1])
                            
                            with col_a:
                                nome_jogador = jogador.get('apelido_jogador') or jogador.get('nome') or jogador.get('login')
                                st.write(f"{idx}. {nome_jogador}")
                            
                            with col_b:
                                if st.button("🗑️ Remover", key=f"remover_{inscricao['id']}"):
                                    remover_jogador_inscricao(inscricao['id'])
                                    st.success("Jogador removido!")
                                    st.rerun()
                    
                    # Botão para excluir jogo
                    st.divider()
                    if st.button("🗑️ Excluir Jogo", key=f"excluir_jogo_{jogo['id']}", type="secondary"):
                        if excluir_jogo(jogo['id']):
                            st.success("✅ Jogo excluído! Todos os inscritos foram notificados.")
                            st.rerun()
                        else:
                            st.error("Erro ao excluir jogo!")


# ============= PÁGINA JOGADOR =============

def pagina_jogador():
    """Página do jogador"""
    
    usuario = st.session_state.usuario_logado
    
    st.title("⚽ Encontrar Jogos")
    
    # Tabs
    tab_buscar, tab_meus_jogos = st.tabs(["Buscar Jogos", "Meus Jogos"])
    
    # === TAB BUSCAR JOGOS ===
    with tab_buscar:
        st.subheader("Jogos Disponíveis")
        
        # Filtro de data
        col1, col2 = st.columns(2)
        with col1:
            data_inicial = st.date_input("A partir de:", value=date.today())
        with col2:
            data_final = st.date_input("Até:", value=date.today() + timedelta(days=30))
        
        data_inicial_str = data_inicial.strftime("%Y-%m-%d")
        data_final_str = data_final.strftime("%Y-%m-%d")
        
        # Lista jogos
        jogos = listar_jogos_futuros(data_inicial_str)
        jogos_filtrados = [j for j in jogos if j['data'] <= data_final_str]
        
        if not jogos_filtrados:
            st.info("Nenhum jogo disponível neste período.")
        else:
            for jogo in jogos_filtrados:
                campo = buscar_campo_por_id(jogo['campo_id'])
                organizador = buscar_usuario_por_id(jogo['organizador_id'])
                
                vagas_disponiveis = jogo['vagas_total'] - jogo['vagas_ocupadas']
                
                # Card do jogo
                with st.container():
                    st.markdown("---")
                    
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"### ⚽ {campo['nome']}")
                        st.write(f"📍 {campo['endereco']}")
                        st.write(f"📏 {campo['formato']} - {campo['tipo']}")
                    
                    with col2:
                        st.write(f"📅 **{formatar_data_br(jogo['data'])}**")
                        st.write(f"⏰ {jogo['hora_inicio']} - {jogo['hora_fim']}")
                        st.write(f"💰 R$ {jogo['valor']:.2f} por pessoa")
                    
                    with col3:
                        if vagas_disponiveis > 0:
                            st.success(f"{vagas_disponiveis} vaga(s)")
                        else:
                            st.error("Lotado")
                        
                        st.write(f"👥 {jogo['vagas_ocupadas']}/{jogo['vagas_total']}")
                    
                    # Botão para ver detalhes
                    if st.button("Ver Detalhes", key=f"detalhes_{jogo['id']}"):
                        st.session_state.jogo_detalhes_id = jogo['id']
                    
                    # Mostra detalhes se selecionado
                    if st.session_state.get('jogo_detalhes_id') == jogo['id']:
                        st.write("---")
                        
                        # Info do organizador
                        nome_org = organizador.get('nome') or organizador.get('login')
                        st.write(f"**👤 Organizador:** {nome_org}")
                        st.write(f"**📞 Telefone:** {organizador.get('telefone', 'N/A')}")
                        
                        # Jogadores confirmados
                        inscricoes_aprovadas = listar_inscricoes_por_jogo(jogo['id'], 'aprovada')
                        
                        if inscricoes_aprovadas:
                            st.write("**✅ Jogadores Confirmados:**")
                            # Lista numerada
                            nomes = []
                            for idx, insc in enumerate(reversed(inscricoes_aprovadas), 1):
                                jog = buscar_usuario_por_id(insc['jogador_id'])
                                nome = jog.get('apelido_jogador') or jog.get('nome') or jog.get('login')
                                nomes.append(f"{idx}. {nome}")
                            st.write("\n".join(nomes))
                        
                        # Jogadores pendentes
                        inscricoes_pendentes = listar_inscricoes_por_jogo(jogo['id'], 'pendente')
                        
                        if inscricoes_pendentes:
                            st.write("**⏳ Aguardando Aprovação:**")
                            nomes_pendentes = []
                            for insc in inscricoes_pendentes:
                                jog = buscar_usuario_por_id(insc['jogador_id'])
                                nome = jog.get('apelido_jogador') or jog.get('nome') or jog.get('login')
                                nomes_pendentes.append(f"• {nome}")
                            st.write("\n".join(nomes_pendentes))
                        
                        # Verifica se usuário já se inscreveu
                        minhas_inscricoes = listar_inscricoes_por_jogador(usuario['id'])
                        ja_inscrito = any(i['jogo_id'] == jogo['id'] and i['status'] in ['pendente', 'aprovada'] for i in minhas_inscricoes)
                        
                        col_btn1, col_btn2 = st.columns(2)
                        
                        with col_btn1:
                            if not ja_inscrito and vagas_disponiveis > 0:
                                if st.button("🎯 Quero Jogar!", key=f"inscrever_{jogo['id']}", use_container_width=True):
                                    inscricao = criar_inscricao(jogo['id'], usuario['id'])
                                    if inscricao:
                                        st.success("✅ Solicitação enviada! Aguarde aprovação do organizador.")
                                        st.rerun()
                                    else:
                                        st.error("Você já está inscrito neste jogo!")
                            elif ja_inscrito:
                                st.info("Você já está inscrito neste jogo")
                            else:
                                st.warning("Sem vagas disponíveis")
                        
                        with col_btn2:
                            if st.button("Fechar", key=f"fechar_{jogo['id']}", use_container_width=True):
                                st.session_state.jogo_detalhes_id = None
                                st.rerun()
    
    # === TAB MEUS JOGOS ===
    with tab_meus_jogos:
        st.subheader("Minhas Inscrições")
        
        minhas_inscricoes = listar_inscricoes_por_jogador(usuario['id'])
        
        if not minhas_inscricoes:
            st.info("Você não está inscrito em nenhum jogo.")
        else:
            # Separa por status
            pendentes = [i for i in minhas_inscricoes if i['status'] == 'pendente']
            aprovadas = [i for i in minhas_inscricoes if i['status'] == 'aprovada']
            
            if pendentes:
                st.write("### ⏳ Aguardando Aprovação")
                for inscricao in pendentes:
                    jogo = buscar_jogo_por_id(inscricao['jogo_id'])
                    campo = buscar_campo_por_id(jogo['campo_id'])
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"⚽ **{campo['nome']}** - {formatar_data_br(jogo['data'])} às {jogo['hora_inicio']}")
                    
                    with col2:
                        if st.button("❌ Cancelar", key=f"cancelar_{inscricao['id']}"):
                            atualizar_status_inscricao(inscricao['id'], 'cancelada')
                            st.success("Inscrição cancelada!")
                            st.rerun()
            
            if aprovadas:
                st.write("### ✅ Confirmadas")
                for inscricao in aprovadas:
                    jogo = buscar_jogo_por_id(inscricao['jogo_id'])
                    campo = buscar_campo_por_id(jogo['campo_id'])
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"⚽ **{campo['nome']}** - {formatar_data_br(jogo['data'])} às {jogo['hora_inicio']}")
                        st.caption(f"💰 R$ {jogo['valor']:.2f}")
                    
                    with col2:
                        if st.button("❌ Cancelar", key=f"cancelar_aprov_{inscricao['id']}"):
                            atualizar_status_inscricao(inscricao['id'], 'cancelada')
                            st.success("Inscrição cancelada!")
                            st.rerun()


# ============= PÁGINA DE NOTIFICAÇÕES =============

def pagina_notificacoes():
    """Página de notificações"""
    
    usuario = st.session_state.usuario_logado
    
    st.title("🔔 Notificações")
    
    notificacoes = listar_notificacoes_usuario(usuario['id'])
    
    if not notificacoes:
        st.info("Você não tem notificações.")
    else:
        col1, col2 = st.columns([3, 1])
        
        with col2:
            if st.button("Marcar todas como lidas"):
                marcar_todas_lidas(usuario['id'])
                st.rerun()
        
        st.divider()
        
        for notif in notificacoes:
            with st.container():
                col_msg, col_btn = st.columns([4, 1])
                
                with col_msg:
                    icone = "🔴" if not notif.get('lida') else "✅"
                    st.write(f"{icone} **{notif['mensagem']}**")
                    st.caption(notif['data_criacao'])
                
                with col_btn:
                    if not notif.get('lida'):
                        if st.button("✓", key=f"ler_{notif['id']}"):
                            marcar_notificacao_lida(notif['id'])
                            st.rerun()
                
                st.divider()


# ============= PÁGINA DE FEED =============

def pagina_feed():
    """Página do feed social"""
    
    usuario = st.session_state.usuario_logado
    
    st.title("📱 Feed Social")
    
    # Tabs
    tab_feed, tab_meus_posts, tab_amigos = st.tabs(["Feed", "Minhas Postagens", "Amigos"])
    
    # === TAB FEED PRINCIPAL ===
    with tab_feed:
        st.subheader("O que está acontecendo?")
        
        # Formulário para criar post
        with st.form("form_criar_post", clear_on_submit=True):
            texto_post = st.text_area("Escreva algo...", max_chars=140, placeholder="Compartilhe algo sobre futebol! ⚽")
            caracteres_restantes = 140 - len(texto_post)
            st.caption(f"{caracteres_restantes} caracteres restantes")
            
            foto_post = st.file_uploader("Adicionar foto (opcional)", type=['jpg', 'jpeg', 'png'], key="upload_post_feed")
            
            col_btn1, col_btn2 = st.columns([1, 4])
            with col_btn1:
                submit_post = st.form_submit_button("📤 Postar", use_container_width=True)
            
            if submit_post:
                if not texto_post and not foto_post:
                    st.error("Escreva algo ou adicione uma foto!")
                else:
                    post = criar_post(usuario['id'], texto_post, foto_post)
                    if post:
                        st.success("✅ Post criado!")
                        st.rerun()
                    else:
                        st.error("Erro ao criar post!")
        
        st.divider()
        
        # Lista posts do feed
        posts_feed = listar_feed(usuario['id'], limite=20)
        
        if not posts_feed:
            st.info("📭 Seu feed está vazio. Siga outros jogadores para ver posts!")
        else:
            for post in posts_feed:
                exibir_post(post, usuario['id'], prefixo_key="feed")
    
    # === TAB MINHAS POSTAGENS ===
    with tab_meus_posts:
        st.subheader("Minhas Postagens")
        
        meus_posts = listar_posts_usuario(usuario['id'])
        
        if not meus_posts:
            st.info("Você ainda não fez nenhuma postagem.")
        else:
            for post in meus_posts:
                exibir_post(post, usuario['id'], exibir_acoes_autor=True, prefixo_key="meus")
    
    # === TAB AMIGOS ===
    with tab_amigos:
        st.subheader("Amigos")
        
        # Estatísticas
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("👥 Seguindo", contar_seguindo(usuario['id']))
        with col_stat2:
            st.metric("❤️ Seguidores", contar_seguidores(usuario['id']))
        
        st.divider()
        
        # Sub-tabs para Buscar, Seguindo e Seguidores
        subtab_buscar, subtab_seguindo, subtab_seguidores = st.tabs(["🔍 Buscar", "👥 Seguindo", "❤️ Seguidores"])
        
        # Buscar jogadores
        with subtab_buscar:
            st.write("### Buscar Jogadores")
            
            # Campo de busca
            termo_busca = st.text_input("Digite nome ou apelido", placeholder="Ex: Daniel")
            
            if termo_busca:
                # Importa função de listar usuários
                from utils import carregar_usuarios
                todos_usuarios = carregar_usuarios()
                
                # Filtra usuários pelo termo de busca (excluindo o próprio usuário)
                resultados = [
                    u for u in todos_usuarios 
                    if u['id'] != usuario['id'] and (
                        termo_busca.lower() in u.get('login', '').lower() or
                        termo_busca.lower() in u.get('nome', '').lower() or
                        termo_busca.lower() in u.get('apelido_jogador', '').lower()
                    )
                ]
                
                if not resultados:
                    st.info("Nenhum jogador encontrado.")
                else:
                    for user in resultados[:10]:  # Mostra até 10 resultados
                        col_user, col_btn = st.columns([3, 1])
                        
                        with col_user:
                            nome = user.get('apelido_jogador') or user.get('nome') or user.get('login')
                            st.write(f"👤 **{nome}**")
                        
                        with col_btn:
                            if esta_seguindo(usuario['id'], user['id']):
                                if st.button("✓ Seguindo", key=f"seguindo_{user['id']}", type="secondary"):
                                    deixar_seguir(usuario['id'], user['id'])
                                    st.rerun()
                            else:
                                if st.button("+ Seguir", key=f"seguir_{user['id']}", type="primary"):
                                    seguir_usuario(usuario['id'], user['id'])
                                    st.success(f"Agora você segue {nome}!")
                                    st.rerun()
        
        # Seguindo
        with subtab_seguindo:
            seguindo_ids = listar_ids_seguindo(usuario['id'])
            
            if not seguindo_ids:
                st.info("Você não está seguindo ninguém ainda.")
            else:
                from utils import buscar_usuario_por_id
                
                for user_id in seguindo_ids:
                    user = buscar_usuario_por_id(user_id)
                    if user:
                        col_user, col_btn = st.columns([3, 1])
                        
                        with col_user:
                            nome = user.get('apelido_jogador') or user.get('nome') or user.get('login')
                            st.write(f"👤 **{nome}**")
                        
                        with col_btn:
                            if st.button("Deixar de seguir", key=f"deixar_{user_id}"):
                                deixar_seguir(usuario['id'], user_id)
                                st.success(f"Você deixou de seguir {nome}")
                                st.rerun()
        
        # Seguidores
        with subtab_seguidores:
            seguidores_ids = listar_ids_seguidores(usuario['id'])
            
            if not seguidores_ids:
                st.info("Você ainda não tem seguidores.")
            else:
                from utils import buscar_usuario_por_id
                
                for user_id in seguidores_ids:
                    user = buscar_usuario_por_id(user_id)
                    if user:
                        col_user, col_btn = st.columns([3, 1])
                        
                        with col_user:
                            nome = user.get('apelido_jogador') or user.get('nome') or user.get('login')
                            st.write(f"👤 **{nome}**")
                        
                        with col_btn:
                            # Verifica se você também segue essa pessoa
                            if esta_seguindo(usuario['id'], user_id):
                                st.caption("✓ Seguindo também")
                            else:
                                if st.button("+ Seguir de volta", key=f"seguir_volta_{user_id}"):
                                    seguir_usuario(usuario['id'], user_id)
                                    st.success(f"Agora você segue {nome}!")
                                    st.rerun()


def exibir_post(post, usuario_logado_id, exibir_acoes_autor=False, prefixo_key="post"):
    """Exibe um post com curtidas e comentários"""
    
    from utils import buscar_usuario_por_id
    
    autor = buscar_usuario_por_id(post['usuario_id'])
    nome_autor = autor.get('apelido_jogador') or autor.get('nome') or autor.get('login')
    
    with st.container():
        st.markdown("---")
        
        # Cabeçalho do post
        col_foto, col_info = st.columns([1, 5])
        
        with col_foto:
            foto_autor = carregar_foto_perfil(autor.get('foto', ''))
            if foto_autor:
                st.image(foto_autor, width=50)
            else:
                st.write("👤")
        
        with col_info:
            st.write(f"**{nome_autor}**")
            data_post = datetime.strptime(post['data_criacao'], "%Y-%m-%d %H:%M:%S")
            st.caption(data_post.strftime("%d/%m/%Y às %H:%M"))
        
        # Texto do post
        if post.get('texto'):
            st.write(post['texto'])
        
        # Foto do post
        if post.get('foto'):
            foto_post = carregar_foto_post(post['foto'])
            if foto_post:
                st.image(foto_post, use_container_width=True)
        
        # Ações do autor (editar/excluir)
        if exibir_acoes_autor and post['usuario_id'] == usuario_logado_id:
            col_edit, col_del, col_space = st.columns([1, 1, 4])
            
            with col_edit:
                if st.button("✏️ Editar", key=f"{prefixo_key}_editar_{post['id']}"):
                    st.session_state.editando_post_id = post['id']
                    st.session_state.texto_edicao = post.get('texto', '')
            
            with col_del:
                if st.button("🗑️ Excluir", key=f"{prefixo_key}_excluir_{post['id']}"):
                    if excluir_post(post['id']):
                        st.success("Post excluído!")
                        st.rerun()
            
            # Formulário de edição
            if st.session_state.get('editando_post_id') == post['id']:
                with st.form(f"{prefixo_key}_form_editar_{post['id']}"):
                    novo_texto = st.text_area("Editar texto", value=st.session_state.texto_edicao, max_chars=140)
                    
                    col_salvar, col_cancelar = st.columns(2)
                    with col_salvar:
                        submit_edicao = st.form_submit_button("💾 Salvar")
                    with col_cancelar:
                        cancelar_edicao = st.form_submit_button("❌ Cancelar")
                    
                    if submit_edicao:
                        if editar_post(post['id'], novo_texto):
                            st.success("Post atualizado!")
                            st.session_state.editando_post_id = None
                            st.rerun()
                    
                    if cancelar_edicao:
                        st.session_state.editando_post_id = None
                        st.rerun()
        
        # Curtidas e Comentários
        st.write("")
        col_curtir, col_comentar = st.columns([1, 5])
        
        num_curtidas = contar_curtidas(post['id'])
        curtiu = usuario_curtiu(post['id'], usuario_logado_id)
        
        with col_curtir:
            if curtiu:
                if st.button(f"❤️ {num_curtidas}", key=f"{prefixo_key}_curtir_{post['id']}"):
                    descurtir_post(post['id'], usuario_logado_id)
                    st.rerun()
            else:
                if st.button(f"🤍 {num_curtidas}", key=f"{prefixo_key}_curtir_{post['id']}"):
                    curtir_post(post['id'], usuario_logado_id)
                    st.rerun()
        
        with col_comentar:
            num_comentarios = contar_comentarios(post['id'])
            if st.button(f"💬 {num_comentarios} comentários", key=f"{prefixo_key}_ver_coment_{post['id']}"):
                if st.session_state.get('post_comentarios_id') == post['id']:
                    st.session_state.post_comentarios_id = None
                else:
                    st.session_state.post_comentarios_id = post['id']
                st.rerun()
        
        # Seção de comentários
        if st.session_state.get('post_comentarios_id') == post['id']:
            st.write("---")
            st.write("**💬 Comentários**")
            
            # Formulário para adicionar comentário
            with st.form(f"{prefixo_key}_form_comentario_{post['id']}", clear_on_submit=True):
                texto_comentario = st.text_input("Escreva um comentário...", max_chars=100)
                submit_comentario = st.form_submit_button("Comentar")
                
                if submit_comentario and texto_comentario:
                    adicionar_comentario(post['id'], usuario_logado_id, texto_comentario)
                    st.success("Comentário adicionado!")
                    st.rerun()
            
            # Lista comentários
            comentarios = listar_comentarios_post(post['id'])
            
            if comentarios:
                for comentario in comentarios:
                    autor_coment = buscar_usuario_por_id(comentario['usuario_id'])
                    nome_autor_coment = autor_coment.get('apelido_jogador') or autor_coment.get('nome') or autor_coment.get('login')
                    
                    col_coment, col_del_coment = st.columns([5, 1])
                    
                    with col_coment:
                        st.write(f"**{nome_autor_coment}:** {comentario['texto']}")
                        data_coment = datetime.strptime(comentario['data'], "%Y-%m-%d %H:%M:%S")
                        st.caption(data_coment.strftime("%d/%m/%Y %H:%M"))
                    
                    with col_del_coment:
                        # Pode excluir se for seu comentário OU se for dono do post
                        if comentario['usuario_id'] == usuario_logado_id or post['usuario_id'] == usuario_logado_id:
                            if st.button("🗑️", key=f"{prefixo_key}_del_coment_{comentario['id']}"):
                                excluir_comentario(comentario['id'])
                                st.rerun()
            else:
                st.info("Seja o primeiro a comentar!")


# ============= ROTEAMENTO DE PÁGINAS =============

def main():
    """Função principal"""
    
    # Se não estiver logado, mostra tela de login
    if not st.session_state.usuario_logado:
        tela_login()
    else:
        # Mostra sidebar
        mostrar_sidebar()
        
        # Roteamento de páginas
        if st.session_state.pagina_atual == 'perfil':
            pagina_perfil()
        elif st.session_state.pagina_atual == 'feed':
            pagina_feed()
        elif st.session_state.pagina_atual == 'organizador':
            pagina_organizador()
        elif st.session_state.pagina_atual == 'jogador':
            pagina_jogador()
        elif st.session_state.pagina_atual == 'notificacoes':
            pagina_notificacoes()


if __name__ == "__main__":
    main()
