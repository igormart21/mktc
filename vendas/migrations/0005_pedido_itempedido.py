# Generated by Django 5.1.7 on 2025-04-06 15:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0003_produto_imagem'),
        ('vendas', '0004_venda_data_venda_venda_preco_total_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('PENDENTE', 'Pendente'), ('ACEITO', 'Aceito'), ('REJEITADO', 'Rejeitado'), ('CANCELADO', 'Cancelado')], default='PENDENTE', max_length=20)),
                ('data_pedido', models.DateTimeField(auto_now_add=True)),
                ('data_atualizacao', models.DateTimeField(auto_now=True)),
                ('observacoes', models.TextField(blank=True, null=True)),
                ('vendedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pedidos', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ItemPedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.IntegerField(default=1)),
                ('preco_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('preco_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='produtos.produto')),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens', to='vendas.pedido')),
            ],
        ),
    ]
