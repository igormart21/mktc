from produtos.models import Produto

# Criar um produto de teste
produto = Produto.objects.create(
    nome="Produto Teste",
    categoria="SEMENTE",
    descricao="Produto de teste para verificação",
    preco=100.00,
    volume_disponivel=1000,
    unidade_medida="kg",
    tipo="soja",
    embalagem="Saco",
    fabricante="Teste",
    lote="TESTE001",
    quantidade_minima=10
)

print(f"Produto criado com ID: {produto.id}") 