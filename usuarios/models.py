from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
import re

def validar_cpf(cpf):
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Validação do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10) % 11
    if digito1 == 10:
        digito1 = 0
    
    # Validação do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10) % 11
    if digito2 == 10:
        digito2 = 0
    
    return int(cpf[9]) == digito1 and int(cpf[10]) == digito2

def validar_telefone(telefone):
    # Remove caracteres não numéricos
    telefone = re.sub(r'[^0-9]', '', telefone)
    
    # Verifica se tem 10 ou 11 dígitos (com ou sem DDD)
    return len(telefone) in [10, 11]

def validate_cep(cep):
    if not re.match(r'^\d{5}-\d{3}$', cep):
        raise ValueError('CEP deve estar no formato 99999-999')

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('aprovado', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário precisa ter acesso ao painel.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário precisa ter permissões de superusuário.')

        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    TIPO_DOCUMENTO_CHOICES = [
        ('RG', 'RG'),
        ('CNH', 'CNH'),
    ]

    UF_CHOICES = [
        ('AC', 'Acre'),
        ('AL', 'Alagoas'),
        ('AP', 'Amapá'),
        ('AM', 'Amazonas'),
        ('BA', 'Bahia'),
        ('CE', 'Ceará'),
        ('DF', 'Distrito Federal'),
        ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'),
        ('MA', 'Maranhão'),
        ('MT', 'Mato Grosso'),
        ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'),
        ('PA', 'Pará'),
        ('PB', 'Paraíba'),
        ('PR', 'Paraná'),
        ('PE', 'Pernambuco'),
        ('PI', 'Piauí'),
        ('RJ', 'Rio de Janeiro'),
        ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'),
        ('RO', 'Rondônia'),
        ('RR', 'Roraima'),
        ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'),
        ('SE', 'Sergipe'),
        ('TO', 'Tocantins'),
    ]

    email = models.EmailField(unique=True, verbose_name='Email')
    nome = models.CharField(max_length=255, verbose_name='Nome')
    cpf = models.CharField(max_length=14, unique=True, verbose_name='CPF')
    telefone = models.CharField(max_length=15, verbose_name='Telefone')
    cep = models.CharField(max_length=9, verbose_name='CEP')
    rua = models.CharField(max_length=255, verbose_name='Rua')
    numero = models.CharField(max_length=20, verbose_name='Número')
    complemento = models.CharField(max_length=255, blank=True, null=True, verbose_name='Complemento')
    hectares_atendidos = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Hectares Atendidos')
    
    # Campos de documento
    tipo_documento = models.CharField(max_length=3, choices=TIPO_DOCUMENTO_CHOICES, verbose_name='Tipo de Documento', null=True, blank=True)
    numero_documento = models.CharField(max_length=20, verbose_name='Número do Documento', null=True, blank=True)
    documento = models.ImageField(upload_to='documentos/', verbose_name='Documento', null=True, blank=True)
    uf_documento = models.CharField(max_length=2, choices=UF_CHOICES, blank=True, null=True, verbose_name='UF do Documento')
    orgao_emissor = models.CharField(max_length=10, blank=True, null=True, verbose_name='Órgão Emissor')

    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    is_staff = models.BooleanField(default=False, verbose_name='Acesso ao Painel')
    is_superuser = models.BooleanField(default=False, verbose_name='Superusuário')
    aprovado = models.BooleanField(default=False, verbose_name='Aprovado')
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='Data de Cadastro')

    # Sobrescrevendo os campos ManyToMany do PermissionsMixin
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='usuario_set',
        related_query_name='usuario'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='usuario_set',
        related_query_name='usuario'
    )

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'cpf', 'telefone', 'cep', 'rua', 'numero', 'hectares_atendidos']

    def __str__(self):
        return self.nome

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def clean(self):
        if not validar_cpf(self.cpf):
            raise ValidationError('CPF inválido')
        if not validar_telefone(self.telefone):
            raise ValidationError('Telefone inválido')
        
        # Validações de documento
        if self.tipo_documento == 'RG':
            if not self.uf_documento:
                raise ValidationError('UF do documento é obrigatória para RG')
            if not self.orgao_emissor:
                raise ValidationError('Órgão emissor é obrigatório para RG')
            if not self.documento:
                raise ValidationError('Documento é obrigatório')
            if not self.numero_documento:
                raise ValidationError('Número do documento é obrigatório')
        elif self.tipo_documento == 'CNH':
            if self.uf_documento:
                raise ValidationError('UF do documento não deve ser preenchida para CNH')
            if self.orgao_emissor:
                raise ValidationError('Órgão emissor não deve ser preenchido para CNH')
            if not self.documento:
                raise ValidationError('Documento é obrigatório')
            if not self.numero_documento:
                raise ValidationError('Número do documento é obrigatório')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        db_table = 'usuario'
