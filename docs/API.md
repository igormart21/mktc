# Documentação da API AgroMarketplace

## Autenticação

### Login

- **URL**: `/api/token/`
- **Método**: `POST`
- **Permissão**: Pública
- **Body**:

```json
{
  "email": "seu_email@email.com",
  "password": "sua_senha"
}
```

- **Resposta**:

```json
{
  "access": "seu_token_de_acesso",
  "refresh": "seu_token_de_refresh"
}
```

### Refresh Token

- **URL**: `/api/token/refresh/`
- **Método**: `POST`
- **Permissão**: Pública
- **Body**:

```json
{
  "refresh": "seu_token_de_refresh"
}
```

- **Resposta**:

```json
{
  "access": "novo_token_de_acesso"
}
```

### Logout

- **URL**: `/api/usuarios/logout/`
- **Método**: `POST`
- **Permissão**: `IsAuthenticated`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`
- **Resposta**:

```json
{
  "mensagem": "Logout realizado com sucesso."
}
```

## Usuários

### Perfil do Usuário

- **URL**: `/api/usuarios/perfil/`
- **Método**: `GET`
- **Permissão**: `IsAuthenticated`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`
- **Resposta**:

```json
{
  "id": 1,
  "nome": "Nome do Usuário",
  "email": "email@email.com",
  "tipo_usuario": "superadmin",
  "status_aprovacao": null
}
```

### Lista de Usuários

- **URL**: `/api/usuarios/lista/`
- **Método**: `GET`
- **Permissão**: `IsSuperAdmin`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`
- **Resposta**:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "email": "email@email.com",
      "nome": "Nome do Usuário",
      "cpf": "12345678900",
      "telefone": "31999999999",
      "cep": "33146020",
      "rua": "Rua Exemplo",
      "numero": "123",
      "complemento": "Apto 45",
      "hectares_atendidos": "50.00",
      "tipo_documento": "RG",
      "numero_documento": "123456789",
      "documento": "url_do_documento",
      "uf_documento": "MG",
      "orgao_emissor": "SSP",
      "is_active": true,
      "is_staff": true,
      "is_superuser": true,
      "aprovado": true,
      "date_joined": "2024-01-01T00:00:00Z"
    }
  ]
}
```

## Vendedores

### Lista de Vendedores

- **URL**: `/api/vendedores/`
- **Método**: `GET`
- **Permissão**: `IsAuthenticated`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`
- **Resposta**:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "usuario": {
        "id": 2,
        "email": "vendedor@email.com",
        "nome": "Nome do Vendedor"
      },
      "cnpj": "12345678901234",
      "razao_social": "Empresa Exemplo LTDA",
      "nome_fantasia": "Empresa Exemplo",
      "inscricao_estadual": "123456789",
      "inscricao_municipal": "987654321",
      "status_aprovacao": "aprovado",
      "observacoes": "Observações sobre a empresa"
    }
  ]
}
```

### Detalhes do Vendedor

- **URL**: `/api/vendedores/<id>/`
- **Método**: `GET`
- **Permissão**: `IsAuthenticated`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`

### Criar Vendedor

- **URL**: `/api/vendedores/`
- **Método**: `POST`
- **Permissão**: `IsAuthenticated`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`
- **Body** (form-data):
  - `usuario[email]`: vendedor@email.com
  - `usuario[nome]`: Nome do Vendedor
  - `usuario[cpf]`: 12345678900
  - `usuario[telefone]`: 31999999999
  - `usuario[cep]`: 33146020
  - `usuario[rua]`: Rua Exemplo
  - `usuario[numero]`: 123
  - `usuario[complemento]`: Apto 45
  - `usuario[hectares_atendidos]`: 50.00
  - `usuario[tipo_documento]`: RG
  - `usuario[numero_documento]`: 123456789
  - `usuario[uf_documento]`: MG
  - `usuario[orgao_emissor]`: SSP
  - `usuario[password]`: Senha@123456
  - `usuario[password2]`: Senha@123456
  - `usuario[documento]`: [arquivo]
  - `cnpj`: 12345678901234
  - `razao_social`: Empresa Teste LTDA
  - `nome_fantasia`: Empresa Teste
  - `inscricao_estadual`: 123456789
  - `inscricao_municipal`: 987654321
  - `observacoes`: Observações sobre a empresa

### Atualizar Status do Vendedor

- **URL**: `/api/vendedores/<id>/atualizar-status/`
- **Método**: `POST`
- **Permissão**: `IsSuperAdmin`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`
- **Body**:

```json
{
  "status_aprovacao": "aprovado"
}
```

- **Resposta**:

```json
{
  "mensagem": "Status do vendedor atualizado com sucesso.",
  "vendedor": {
    "id": 1,
    "usuario": {
      "id": 2,
      "email": "vendedor@email.com",
      "nome": "Nome do Vendedor"
    },
    "cnpj": "12345678901234",
    "razao_social": "Empresa Exemplo LTDA",
    "nome_fantasia": "Empresa Exemplo",
    "inscricao_estadual": "123456789",
    "inscricao_municipal": "987654321",
    "status_aprovacao": "aprovado",
    "observacoes": "Observações sobre a empresa"
  }
}
```

### Lista de Vendedores Pendentes

- **URL**: `/api/vendedores/pendentes/`
- **Método**: `GET`
- **Permissão**: `IsSuperAdmin`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`
- **Resposta**:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "usuario": {
        "id": 2,
        "email": "vendedor@email.com",
        "nome": "Nome do Vendedor"
      },
      "cnpj": "12345678901234",
      "razao_social": "Empresa Exemplo LTDA",
      "nome_fantasia": "Empresa Exemplo",
      "inscricao_estadual": "123456789",
      "inscricao_municipal": "987654321",
      "status_aprovacao": "pendente",
      "observacoes": "Observações sobre a empresa"
    }
  ]
}
```

## Produtos

### Lista de Produtos

- **URL**: `/api/produtos/`
- **Método**: `GET`
- **Permissão**: `IsAuthenticated`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`
- **Resposta**:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "nome": "Produto Exemplo",
      "descricao": "Descrição do produto",
      "preco": "100.00",
      "quantidade": 10,
      "categoria": "SEMENTES",
      "vendedor": {
        "id": 1,
        "nome": "Nome do Vendedor"
      }
    }
  ]
}
```

### Detalhes do Produto

- **URL**: `/api/produtos/<id>/`
- **Método**: `GET`
- **Permissão**: `IsAuthenticated`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`

### Criar Produto

- **URL**: `/api/produtos/`
- **Método**: `POST`
- **Permissão**: `IsVendedorAprovado`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`
- **Body**:

```json
{
  "nome": "Produto Exemplo",
  "descricao": "Descrição do produto",
  "preco": "100.00",
  "quantidade": 10,
  "categoria": "SEMENTES",
  "vendedor": 1
}
```

### Lista de Produtos por Vendedor

- **URL**: `/api/produtos/vendedor/<id>/`
- **Método**: `GET`
- **Permissão**: `IsAuthenticated`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`
- **Resposta**:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "nome": "Produto Exemplo",
      "descricao": "Descrição do produto",
      "preco": "100.00",
      "quantidade": 10,
      "categoria": "SEMENTES",
      "vendedor": {
        "id": 1,
        "nome": "Nome do Vendedor"
      }
    }
  ]
}
```

### Atualizar Produto

- **URL**: `/api/produtos/<id>/`
- **Método**: `PUT`
- **Permissão**: `IsVendedorAprovado`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`
- **Body**:

```json
{
  "nome": "Produto Atualizado",
  "descricao": "Nova descrição do produto",
  "preco": "150.00",
  "quantidade": 15,
  "categoria": "SEMENTES",
  "vendedor": 1
}
```

### Deletar Produto

- **URL**: `/api/produtos/<id>/`
- **Método**: `DELETE`
- **Permissão**: `IsVendedorAprovado`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`
- **Resposta**:

```json
{
  "mensagem": "Produto deletado com sucesso."
}
```

## Vendas

### Lista de Vendas

- **URL**: `/api/vendas/`
- **Método**: `GET`
- **Permissão**: `IsAuthenticated`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`
- **Resposta**:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "produto": {
        "id": 1,
        "nome": "Produto Exemplo"
      },
      "quantidade": 2,
      "valor_total": "200.00",
      "status": "PENDENTE",
      "comprador": {
        "id": 1,
        "nome": "Nome do Comprador"
      },
      "vendedor": {
        "id": 1,
        "nome": "Nome do Vendedor"
      }
    }
  ]
}
```

### Detalhes da Venda

- **URL**: `/api/vendas/<id>/`
- **Método**: `GET`
- **Permissão**: `IsAuthenticated`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`

### Criar Venda

- **URL**: `/api/vendas/`
- **Método**: `POST`
- **Permissão**: `IsAuthenticated`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`
- **Body**:

```json
{
  "produto": 1,
  "quantidade": 2,
  "valor_total": "200.00",
  "status": "PENDENTE",
  "comprador": 1,
  "vendedor": 1
}
```

### Atualizar Status da Venda

- **URL**: `/api/vendas/<id>/atualizar-status/`
- **Método**: `POST`
- **Permissão**: `IsAuthenticated`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`
- **Body**:

```json
{
  "status": "CONCLUIDA"
}
```

- **Resposta**:

```json
{
  "mensagem": "Status da venda atualizado com sucesso.",
  "venda": {
    "id": 1,
    "produto": {
      "id": 1,
      "nome": "Produto Exemplo"
    },
    "quantidade": 2,
    "valor_total": "200.00",
    "status": "CONCLUIDA",
    "comprador": {
      "id": 1,
      "nome": "Nome do Comprador"
    },
    "vendedor": {
      "id": 1,
      "nome": "Nome do Vendedor"
    }
  }
}
```

### Lista de Vendas por Vendedor

- **URL**: `/api/vendas/vendedor/<id>/`
- **Método**: `GET`
- **Permissão**: `IsAuthenticated`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`
- **Resposta**:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "produto": {
        "id": 1,
        "nome": "Produto Exemplo"
      },
      "quantidade": 2,
      "valor_total": "200.00",
      "status": "PENDENTE",
      "comprador": {
        "id": 1,
        "nome": "Nome do Comprador"
      },
      "vendedor": {
        "id": 1,
        "nome": "Nome do Vendedor"
      }
    }
  ]
}
```

### Lista de Vendas por Comprador

- **URL**: `/api/vendas/comprador/<id>/`
- **Método**: `GET`
- **Permissão**: `IsAuthenticated`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`
- **Resposta**:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "produto": {
        "id": 1,
        "nome": "Produto Exemplo"
      },
      "quantidade": 2,
      "valor_total": "200.00",
      "status": "PENDENTE",
      "comprador": {
        "id": 1,
        "nome": "Nome do Comprador"
      },
      "vendedor": {
        "id": 1,
        "nome": "Nome do Vendedor"
      }
    }
  ]
}
```

## Painel Administrativo

### Dashboard

- **URL**: `/api/painel/dashboard/`
- **Método**: `GET`
- **Permissão**: `IsAdminUser`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`
- **Resposta**:

```json
{
  "total_usuarios": 124,
  "total_vendedores_aprovados": 35,
  "total_produtos": 150,
  "total_vendas": 92,
  "lucro_estimado": 10452.5
}
```

## Áreas de Acesso

### Área Administrativa

- **URL**: `/api/admin/`
- **Método**: `GET`
- **Permissão**: `IsSuperAdmin`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`
- **Resposta**:

```json
{
  "mensagem": "Bem-vindo à área administrativa!",
  "usuario": "email@email.com"
}
```

### Área do Vendedor

- **URL**: `/api/vendedor/`
- **Método**: `GET`
- **Permissão**: `IsVendedorAprovado`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`
- **Resposta**:

```json
{
  "mensagem": "Bem-vindo à área do vendedor!",
  "usuario": "email@email.com"
}
```

### Área do Usuário

- **URL**: `/api/usuario/`
- **Método**: `GET`
- **Permissão**: `IsAuthenticatedUser`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`
- **Resposta**:

```json
{
  "mensagem": "Bem-vindo à sua área!",
  "usuario": "email@email.com"
}
```

## Teste de Autenticação

- **URL**: `/api/teste/`
- **Método**: `GET`
- **Permissão**: `IsAuthenticated`
- **Headers**:
  - `Authorization`: `Bearer seu_token_de_acesso`
- **Resposta**:

```json
{
  "mensagem": "Você está autenticado!",
  "usuario": "email@email.com"
}
```
