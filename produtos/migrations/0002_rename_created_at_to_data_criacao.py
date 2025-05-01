from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='produto',
            old_name='created_at',
            new_name='data_criacao',
        ),
    ] 