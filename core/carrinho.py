from decimal import Decimal
from django.conf import settings
from produtos.models import Produto

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
        self.session.modified = True

    def limpar(self):
        del self.session[settings.CARRINHO_SESSION_ID]
        self.salvar()

    def __iter__(self):
        produto_ids = self.carrinho.keys()
        print("IDs dos produtos no carrinho:", list(produto_ids))
        
        produtos = Produto.objects.filter(id__in=produto_ids, ativo=True)
        print("Produtos encontrados:", list(produtos))
        
        carrinho = self.carrinho.copy()
        for produto in produtos:
            if str(produto.id) in carrinho:
                carrinho[str(produto.id)]['produto'] = produto
                carrinho[str(produto.id)]['preco'] = Decimal(carrinho[str(produto.id)]['preco'])
                carrinho[str(produto.id)]['preco_total'] = carrinho[str(produto.id)]['preco'] * carrinho[str(produto.id)]['quantidade']
                yield carrinho[str(produto.id)]

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