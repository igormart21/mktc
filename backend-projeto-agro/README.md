# Agromarketplace

Sistema de marketplace para produtos agrícolas desenvolvido com Django e Django REST Framework.

## Funcionalidades

- Sistema de autenticação com JWT
- Gerenciamento de usuários
- Gerenciamento de vendedores
- Gerenciamento de produtos
- Sistema de permissões personalizado
- API RESTful

## Requisitos

- Python 3.8+
- Django 4.2+
- MySQL
- Outras dependências listadas em `requirements.txt`

## Instalação

1. Clone o repositório:

```bash
git clone https://github.com/seu-usuario/agromarketplace.git
cd agromarketplace
```

2. Crie um ambiente virtual e ative-o:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:

- Crie um arquivo `.env` na raiz do projeto
- Adicione as seguintes variáveis:

```
DEBUG=True
SECRET_KEY=sua-chave-secreta
DATABASE_URL=mysql://usuario:senha@localhost:3306/nome_do_banco
```

5. Execute as migrações:

```bash
python manage.py migrate
```

6. Crie um superusuário:

```bash
python manage.py createsuperuser
```

7. Inicie o servidor:

```bash
python manage.py runserver
```

## Endpoints da API

- `/api/token/` - Obter token JWT
- `/api/token/refresh/` - Renovar token JWT
- `/api/admin/` - Área administrativa
- `/api/vendedor/` - Área do vendedor
- `/api/usuario/` - Área do usuário
- `/api/perfil/` - Dados do usuário autenticado

## Permissões

- `IsSuperAdmin`: Acesso apenas para superadmins
- `IsVendedorAprovado`: Acesso apenas para vendedores aprovados
- `IsAuthenticatedUser`: Acesso para usuários autenticados

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request
