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
    listar_jogos_futuros, verificar_conflito_horario,
    # Inscrições
    criar_inscricao, listar_inscricoes_por_jogo, listar_inscricoes_por_jogador,
    atualizar_status_inscricao, remover_jogador_inscricao,
    # Notificações
    listar_notificacoes_usuario, contar_notificacoes_nao_lidas,
    marcar_notificacao_lida, marcar_todas_lidas,
    # Paths
    FOTOS_DIR
)


# ============= CONFIGURAÇÕES DA PÁGINA =============

st.set_page_config(
    page_title="Futebol Society",
    page_icon="⚽",
    layout="wide"
)


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
            login = st.text_input("Nome/Email/Apelido")
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
            novo_login = st.text_input("Nome/Email/Apelido")
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
                    # Verifica se login já existe
                    if buscar_usuario_por_login(novo_login):
                        st.error("Este login já está em uso!")
                    else:
                        # Cria usuário
                        usuario = criar_usuario(novo_login, nova_senha, novo_telefone)
                        st.success("Cadastro realizado com sucesso! Faça login.")
    
    # === TAB RECUPERAR SENHA ===
    with tab_recuperar:
        st.write("### Esqueceu sua senha?")
        st.info("📞 Entre em contato com o suporte: **1234-5678**")


# ============= SIDEBAR COM MENU =============

def mostrar_sidebar():
    """Mostra sidebar com menu de navegação"""
    
    usuario = st.session_state.usuario_logado
    
    with st.sidebar:
        st.title("⚽ Menu")
        
        # Foto e nome do usuário
        foto = carregar_foto_perfil(usuario.get('foto', ''))
        if foto:
            st.image(foto, width=150)
        
        st.write(f"**{usuario.get('nome') or usuario.get('login')}**")
        
        # Notificações
        num_notificacoes = contar_notificacoes_nao_lidas(usuario['id'])
        if num_notificacoes > 0:
            st.warning(f"🔔 {num_notificacoes} notificação(ões) nova(s)")
        
        st.divider()
        
        # Menu
        if st.button("👤 Perfil", use_container_width=True):
            st.session_state.pagina_atual = 'perfil'
            st.rerun()
        
        if st.button("📋 Organizador", use_container_width=True):
            st.session_state.pagina_atual = 'organizador'
            st.rerun()
        
        if st.button("⚽ Jogador", use_container_width=True):
            st.session_state.pagina_atual = 'jogador'
            st.rerun()
        
        if st.button("🔔 Notificações", use_container_width=True):
            st.session_state.pagina_atual = 'notificacoes'
            st.rerun()
        
        st.divider()
        
        if st.button("🚪 Sair", use_container_width=True):
            logout()


# ============= PÁGINA DE PERFIL =============

def pagina_perfil():
    """Página de perfil do usuário"""
    
    usuario = st.session_state.usuario_logado
    
    st.title("👤 Meu Perfil")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Foto de Perfil")
        
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
        
        with st.form("form_criar_jogo"):
            # Select box de campos
            opcoes_campos = {f"{c['nome']} - {c['formato']} ({c['tipo']})": c['id'] for c in campos}
            campo_selecionado = st.selectbox("Campo", options=list(opcoes_campos.keys()))
            campo_id = opcoes_campos[campo_selecionado]
            
            # Mostra info do campo
            campo_info = buscar_campo_por_id(campo_id)
            st.info(f"📍 {campo_info['endereco']} | {campo_info['dimensoes']} | {campo_info['jogadores_por_time']} jogadores por time")
            
            col1, col2 = st.columns(2)
            
            with col1:
                data_jogo = st.date_input("Data do Jogo", min_value=date.today())
                hora_inicio = st.time_input("Horário de Início")
            
            with col2:
                hora_fim = st.time_input("Horário de Término")
                valor = st.number_input("Valor por Pessoa (R$)", min_value=0.0, step=5.0)
            
            vagas = st.number_input("Número de Vagas", min_value=1, max_value=campo_info['jogadores_por_time']*2, value=campo_info['jogadores_por_time']*2)
            
            submit = st.form_submit_button("Criar Jogo", use_container_width=True)
            
            if submit:
                data_str = data_jogo.strftime("%Y-%m-%d")
                hora_inicio_str = hora_inicio.strftime("%H:%M")
                hora_fim_str = hora_fim.strftime("%H:%M")
                
                # Validações
                if hora_fim <= hora_inicio:
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
                        
                        for inscricao in inscricoes_aprovadas:
                            jogador = buscar_usuario_por_id(inscricao['jogador_id'])
                            
                            col_a, col_b = st.columns([3, 1])
                            
                            with col_a:
                                nome_jogador = jogador.get('apelido_jogador') or jogador.get('nome') or jogador.get('login')
                                st.write(f"✅ {nome_jogador}")
                            
                            with col_b:
                                if st.button("🗑️ Remover", key=f"remover_{inscricao['id']}"):
                                    remover_jogador_inscricao(inscricao['id'])
                                    st.success("Jogador removido!")
                                    st.rerun()


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
                            nomes = []
                            for insc in inscricoes_aprovadas:
                                jog = buscar_usuario_por_id(insc['jogador_id'])
                                nome = jog.get('apelido_jogador') or jog.get('nome') or jog.get('login')
                                nomes.append(nome)
                            st.write(", ".join(nomes))
                        
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
        elif st.session_state.pagina_atual == 'organizador':
            pagina_organizador()
        elif st.session_state.pagina_atual == 'jogador':
            pagina_jogador()
        elif st.session_state.pagina_atual == 'notificacoes':
            pagina_notificacoes()


if __name__ == "__main__":
    main()
