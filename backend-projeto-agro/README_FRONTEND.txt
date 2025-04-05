INSTRUÇÕES PARA O TIME DE FRONTEND - AGROMARKETPLACE
=================================================

INFORMAÇÕES DO BACKEND
---------------------
- Projeto: AgroMarketplace Backend
- Framework: Django com Django REST Framework
- Versão do Python: 3.13.2
- Autenticação: JWT (JSON Web Tokens)

COMO INICIAR O PROJETO
---------------------
1. Descompacte o arquivo projeto_agro.zip
2. Configure o ambiente virtual Python (se necessário)
3. Instale as dependências: `pip install -r requirements.txt`
4. Execute as migrações: `python manage.py migrate`
5. Crie um superusuário: `python manage.py createsuperuser`
6. Inicie o servidor: `python manage.py runserver`

URLS IMPORTANTES
--------------
- API Base URL: http://localhost:8000/api/
- Admin Django: http://localhost:8000/admin/
- Documentação API: Consulte o arquivo `/docs/API.md`

AUTENTICAÇÃO
-----------
- Endpoint: `/api/token/`
- Method: POST
- Body: `{"username": "seu_usuario", "password": "sua_senha"}`
- Response: `{"access": "token", "refresh": "token"}`
- Como usar: Adicione o header `Authorization: Bearer {token}` em todas as requisições autenticadas

ENDPOINTS PRINCIPAIS
------------------
1. Produtos
   - GET `/api/produtos/` - Listar produtos
   - POST `/api/produtos/` - Criar produto
   - GET `/api/produtos/{id}/` - Detalhes do produto
   - PUT `/api/produtos/{id}/` - Atualizar produto
   - DELETE `/api/produtos/{id}/` - Deletar produto

2. Vendas
   - GET `/api/vendas/` - Listar vendas
   - POST `/api/vendas/` - Criar venda
   - GET `/api/vendas/{id}/` - Detalhes da venda
   - PUT `/api/vendas/{id}/` - Atualizar venda
   - GET `/api/vendas/vendas_recebidas/` - Vendas recebidas (vendedor)
   - GET `/api/vendas/minhas_vendas/` - Minhas vendas (comprador)

3. Vendedores
   - GET `/api/vendedores/` - Listar vendedores
   - POST `/api/vendedores/` - Criar vendedor
   - GET `/api/vendedores/{id}/` - Detalhes do vendedor

4. Usuários
   - GET `/api/usuarios/` - Listar usuários (admin)
   - GET `/api/area-admin/` - Área admin
   - GET `/api/area-vendedor/` - Área vendedor
   - GET `/api/area-usuario/` - Área usuário

CORS E REQUISIÇÕES
----------------
- O backend já está configurado com CORS habilitado
- Todos os métodos HTTP estão permitidos (GET, POST, PUT, DELETE)
- Origins permitidos: Configuráveis em `core/settings.py`

ESTRUTURA DE DADOS
----------------
1. Produto:
   ```json
   {
     "id": 1,
     "nome": "Nome do Produto",
     "descricao": "Descrição detalhada",
     "preco": "100.00",
     "quantidade": 10,
     "categoria": "SEMENTES",
     "vendedor": 1
   }
   ```

2. Venda:
   ```json
   {
     "id": 1,
     "produto": 1,
     "quantidade": 2,
     "valor_total": "200.00",
     "status": "PENDENTE",
     "comprador": 1
   }
   ```

3. Usuário:
   ```json
   {
     "id": 1,
     "username": "usuario",
     "email": "email@exemplo.com",
     "nome": "Nome Completo"
   }
   ```

4. Vendedor:
   ```json
   {
     "id": 1,
     "usuario": 1,
     "documento": "12345678901",
     "telefone": "11999999999",
     "endereco": "Endereço completo",
     "status_aprovacao": "APROVADO"
   }
   ```

CONTATO PARA SUPORTE
------------------
Em caso de dúvidas ou problemas com a API, entre em contato com o time de backend.

Para detalhes completos, consulte também os arquivos:
1. funcionalidades_vendedor.txt - Detalhes das funcionalidades para vendedores
2. funcionalidades_admin.txt - Detalhes das funcionalidades para administradores
3. guia_desenvolvimento_frontend.txt - Guia passo a passo para desenvolvimento do frontend 