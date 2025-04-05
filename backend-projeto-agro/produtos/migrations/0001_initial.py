from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Produto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255, verbose_name='Nome')),
                ('descricao', models.TextField(verbose_name='Descrição')),
                ('preco', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Preço')),
                ('estoque', models.IntegerField(verbose_name='Estoque')),
                ('criado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='produtos_criados', to='usuarios.usuario', verbose_name='Criado por')),
            ],
            options={
                'verbose_name': 'Produto',
                'verbose_name_plural': 'Produtos',
                'db_table': 'produto',
            },
        ),
    ] 