# JogoFácil - Rede Social para Futebol Society

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41-red)
![License](https://img.shields.io/badge/License-MIT-green)

**JogoFácil** é uma rede social completa desenvolvida em Python com Streamlit, criada especificamente para jogadores de futebol society organizarem jogos, conectarem-se com outros jogadores e compartilharem momentos.

---

## Índice

- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Guia de Uso](#guia-de-uso)
- [Customização](#customização)

---

## Funcionalidades

### Autenticação
- Sistema de login e cadastro com validação
- Senha de 4 dígitos
- Telefone como identificador único
- Recuperação de senha via suporte

### Perfil do Usuário
- Foto de perfil personalizada
- Nome completo e apelido de jogador
- Edição de informações pessoais
- Telefone para contato

### Organizador de Jogos
- **Criar Jogos**: Agende partidas com detalhes completos
  - Seleção de campo cadastrado
  - Data e horário (intervalos de 30 minutos)
  - Valor por pessoa
  - Número de vagas
  - Validação de conflito de horários
- **Gerenciar Inscrições**:
  - Aprovar/reprovar jogadores
  - Remover jogadores confirmados
  - Visualizar lista completa (confirmados + pendentes)
- **Excluir Jogos**: Com notificação automática para todos os inscritos

### Jogador
- **Buscar Jogos**: 
  - Filtro por data
  - Visualização de campos disponíveis
  - Informações detalhadas (organizador, telefone, confirmados, pendentes)
- **Inscrever-se**: Sistema de aprovação pelo organizador
- **Minhas Inscrições**:
  - Acompanhar status (pendente/aprovada)
  - Cancelar inscrições
  - Visualizar jogos confirmados

### Feed Social
- **Criar Posts**:
  - Texto de até 140 caracteres
  - Upload de foto (JPG, PNG)
  - Preview de caracteres restantes
- **Interações**:
  - Curtir/descurtir posts
  - Comentar (até 100 caracteres)
  - Excluir comentários (autor ou dono do post)
- **Editar/Excluir**: Próprios posts
- **Abas**:
  - Feed Principal (posts de quem você segue)
  - Minhas Postagens
  - Amigos (buscar, seguindo, seguidores)

### Sistema de Amizade
- Seguir/deixar de seguir usuários
- Busca por nome ou apelido
- Contador de seguindo/seguidores
- Visualizar listas completas

### Notificações
- **Jogos**:
  - Nova inscrição (organizador)
  - Inscrição aprovada/reprovada (jogador)
  - Inscrição cancelada (organizador)
  - Jogo cancelado (todos os inscritos)
  - Jogador removido
- **Feed Social**:
  - Novo seguidor
  - Curtida em post
  - Comentário em post
- Marcar como lida (individual ou todas)
- Indicador visual de não lidas
- Dividers entre notificações para melhor organização

---

## Tecnologias

### Backend
- **Python 3.12**: Linguagem principal
- **Streamlit 1.41**: Framework web
- **JSON**: Persistência de dados

### Bibliotecas
- **Pillow (PIL)**: Processamento de imagens
- **datetime**: Manipulação de datas

### Frontend
- **CSS customizado**: Tema verde campo de futebol
- **Streamlit Components**: Interface reativa

---

## Instalação

### Pré-requisitos
- Python 3.12+
- pip ou uv (gerenciador de pacotes)

### Passo a Passo

1. **Clone o repositório**
```bash
git clone https://github.com/Daniel-JMachado/jogofacil.git
cd jogofacil
```

2. **Crie um ambiente virtual** (opcional, mas recomendado)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Instale as dependências**

Com pip:
```bash
pip install streamlit pillow
```

Com uv:
```bash
uv pip install streamlit pillow
```

4. **Execute a aplicação**
```bash
streamlit run app.py
```

ou com uv:
```bash
uv run streamlit run app.py
```

5. **Acesse no navegador**
```
http://localhost:8501
```

---

## Como Usar

### Primeiro Acesso

1. **Cadastro**:
   - Clique na aba "Cadastro"
   - Preencha: Nome/Apelido, Telefone, Senha (4 dígitos)
   - Clique em "Cadastrar"

2. **Login**:
   - Digite seu nome/apelido e senha
   - Clique em "Entrar"

### Navegação

Use o **menu lateral** para acessar:
- 👤 **Perfil**: Editar informações e foto
- 📱 **Feed**: Rede social
- 📋 **Organizador**: Criar e gerenciar jogos
- ⚽ **Jogador**: Buscar e se inscrever em jogos
- 🔔 **Notificações**: Ver avisos

---

## Estrutura do Projeto

```
jogofacil/
├── app.py                 # Aplicação principal
├── utils.py              # Funções de jogos, usuários, notificações
├── utils_feed.py         # Funções do feed social
├── style.css             # Estilos customizados
├── data/                 # Dados persistidos (JSON)
│   ├── usuarios.json
│   ├── jogos.json
│   ├── campos.json
│   ├── inscricoes.json
│   ├── notificacoes.json
│   ├── posts.json
│   ├── seguindo.json
│   ├── curtidas.json
│   ├── comentarios.json
│   ├── fotos/            # Fotos de perfil
│   └── posts_fotos/      # Fotos de posts
└── README.md             # Este arquivo
```

### Arquivos Principais

#### `app.py`
- Interface principal Streamlit
- Páginas: Login, Perfil, Feed, Organizador, Jogador, Notificações
- Funções de UI e roteamento

#### `utils.py`
- Gerenciamento de usuários
- CRUD de jogos e campos
- Sistema de inscrições
- Notificações
- Validações (conflito de horário, telefone único)

#### `utils_feed.py`
- Posts (criar, editar, excluir)
- Curtidas (curtir, descurtir)
- Comentários (adicionar, excluir)
- Sistema de seguir (seguir, deixar de seguir)
- Feed personalizado

#### `style.css`
- Tema escuro com gradiente verde
- Design inspirado em campo de futebol
- Componentes customizados
- Responsivo

---

## Guia de Uso

### Como Organizador

1. **Criar Jogo**:
   - Acesse "📋 Organizador"
   - Aba "Criar Jogo"
   - Selecione campo, data, horário, valor e vagas
   - Clique "Criar Jogo"

2. **Gerenciar Inscrições**:
   - Aba "Meus Jogos"
   - Expanda um jogo
   - Veja inscrições pendentes e aprovadas
   - Aprove/reprove jogadores

3. **Excluir Jogo**:
   - Clique em "Excluir Jogo"
   - Todos os inscritos serão notificados

### Como Jogador

1. **Buscar Jogos**:
   - Acesse "⚽ Jogador"
   - Filtre por data
   - Clique "Ver Detalhes"

2. **Inscrever-se**:
   - Veja informações do jogo
   - Clique "🎯 Quero Jogar!"
   - Aguarde aprovação do organizador

3. **Acompanhar**:
   - Aba "Meus Jogos"
   - Veja status: pendente ou confirmada
   - Cancele se necessário

### Rede Social

1. **Criar Post**:
   - Acesse "📱 Feed"
   - Escreva texto (até 140 caracteres)
   - Adicione foto (opcional)
   - Clique "📤 Postar"

2. **Interagir**:
   - Curta posts (coração)
   - Comente (balão de fala)
   - Expanda para ver comentários

3. **Seguir Pessoas**:
   - Aba "Amigos"
   - Sub-aba "🔍 Buscar"
   - Digite nome/apelido
   - Clique "Seguir"

---

## Customização

### Tema Visual

O CSS está em `style.css`. Principais variáveis de cor:

```css
:root {
    --verde-campo: #1a4d2e;
    --verde-grama: #2d7a4f;
    --verde-claro: #4a9d6f;
    --verde-neon: #00ff88;
}
```

### Adicionar Campos

Edite `data/campos.json`:

```json
{
  "id": 1,
  "nome": "Arena Park Coberto",
  "endereco": "Av. Principal, 123",
  "formato": "6x6",
  "tipo": "coberto",
  "dimensoes": "45x25m",
  "jogadores_por_time": 6
}
```

---

## Funcionalidades Técnicas

### Validações

- **Telefone único**: Não permite duplicatas
- **Conflito de horário**: Mesmo campo não pode ter jogos sobrepostos
- **Vagas**: Impede inscrições em jogos lotados
- **Duplicatas**: Previne múltiplas inscrições no mesmo jogo

### Notificações Automáticas

Gatilhos:
- Nova inscrição → Organizador
- Aprovação/reprovação → Jogador
- Cancelamento de inscrição → Organizador
- Exclusão de jogo → Todos os inscritos
- Novo seguidor → Usuário seguido
- Curtida em post → Dono do post (se diferente)
- Comentário em post → Dono do post (se diferente)

### Persistência de Dados

Todos os dados são salvos em arquivos JSON em `data/`:
- Leitura e escrita atômica
- Encoding UTF-8 para caracteres especiais
- Geração automática de IDs únicos

---

## Contato

**Desenvolvedor**: Daniel Machado  
**GitHub**: [@Daniel-JMachado](https://github.com/Daniel-JMachado)  
**Repositório**: [jogofacil](https://github.com/Daniel-JMachado/jogofacil)

---

**Bora jogar bola!**
