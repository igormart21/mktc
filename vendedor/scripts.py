from vendedor.models import Vendedor

def atualizar_status_aprovacao():
    aprovados = Vendedor.objects.filter(data_aprovacao__isnull=False)
    for v in aprovados:
        v.status_aprovacao = 'APROVADO'
        v.save()
    print(f"{aprovados.count()} vendedores atualizados para APROVADO.")

if __name__ == "__main__":
    atualizar_status_aprovacao() 