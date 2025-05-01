from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('vendedor', '0002_vendedor_cnh_verso_vendedor_rg_verso'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vendedor',
            old_name='created_at',
            new_name='data_criacao',
        ),
        migrations.AlterModelOptions(
            name='vendedor',
            options={'ordering': ['-data_criacao'], 'verbose_name': 'Vendedor', 'verbose_name_plural': 'Vendedores'},
        ),
    ] 