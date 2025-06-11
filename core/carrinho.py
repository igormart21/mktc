from decimal import Decimal
from django.conf import settings
from produtos.models import Produto

# Função recursiva para converter Decimals em string
def converter_decimals(obj):
    if isinstance(obj, dict):
        return {k: converter_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [converter_decimals(i) for i in obj]
    elif isinstance(obj, Decimal):
        return str(obj)
    else:
        return obj

class Carrinho:
    def __init__(self, request):
        self.session = request.session
        carrinho = self.session.get(settings.CARRINHO_SESSION_ID)
        if not carrinho:
            carrinho = self.session[settings.CARRINHO_SESSION_ID] = {}
        self.carrinho = carrinho

    def adicionar(self, produto, quantidade=1, atualizar_quantidade=False):
        produto_id = str(produto.id)
        if produto_id not in self.carrinho:
            self.carrinho[produto_id] = {
                'quantidade': 0,
                'preco': str(produto.preco)
            }
        if atualizar_quantidade:
            self.carrinho[produto_id]['quantidade'] = quantidade
        else:
            self.carrinho[produto_id]['quantidade'] += quantidade
        self.salvar()

    def remover(self, produto):
        produto_id = str(produto.id)
        if produto_id in self.carrinho:
            del self.carrinho[produto_id]
            self.salvar()

    def salvar(self):
        # Salva apenas o dicionário puro, convertido
        self.session[settings.CARRINHO_SESSION_ID] = converter_decimals(self.carrinho)
        self.session.modified = True

    def limpar(self):
        if settings.CARRINHO_SESSION_ID in self.session:
            del self.session[settings.CARRINHO_SESSION_ID]
        self.session.modified = True

    def __iter__(self):
        for produto_id, item in self.carrinho.items():
            produto = Produto.objects.get(id=produto_id)
            preco = float(item['preco'])  # Garante que é float
            quantidade = int(item['quantidade'])
            preco_total = float(preco * quantidade)
            yield {
                'produto': produto,
                'quantidade': quantidade,
                'preco': preco,
                'preco_total': preco_total,
            }

    def __len__(self):
        return sum(item['quantidade'] for item in self.carrinho.values())

    def get_preco_total(self):
        return sum(Decimal(item['preco']) * item['quantidade'] for item in self.carrinho.values())

    def __bool__(self):
        return bool(self.carrinho)

    def diminuir_quantidade(self, produto):
        produto_id = str(produto.id)
        if produto_id in self.carrinho:
            if self.carrinho[produto_id]['quantidade'] > 1:
                self.carrinho[produto_id]['quantidade'] -= 1
            else:
                del self.carrinho[produto_id]
            self.salvar() 