# Rede Social de Futebol Society ⚽

MVP de rede social para conectar jogadores de futebol society.

## Como Executar

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute a aplicação:
```bash
streamlit run app.py
```

## Funcionalidades

- **Login/Cadastro**: Acesso com senha de 4 dígitos
- **Perfil**: Gerenciar dados pessoais e foto
- **Organizador**: Criar jogos e gerenciar inscrições
- **Jogador**: Buscar e se inscrever em jogos
- **Notificações**: Sistema de alertas para interações

## Estrutura do Projeto

```
R_social/
├── app.py              # Aplicação principal Streamlit
├── utils.py            # Funções utilitárias
├── requirements.txt    # Dependências
└── data/
    ├── campos.json     # Campos cadastrados
    ├── usuarios.json   # Usuários
    ├── jogos.json      # Jogos criados
    ├── inscricoes.json # Inscrições
    ├── notificacoes.json # Notificações
    └── fotos/          # Fotos de perfil
```
