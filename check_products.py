from produtos.models import Produto

# Listar todos os produtos
print("Produtos existentes:")
for produto in Produto.objects.all():
    print(f"ID: {produto.id}, Nome: {produto.nome}") 