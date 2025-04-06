import os
from django.core.exceptions import ValidationError
from django.conf import settings

def validate_file_upload(file, max_size_mb=5, allowed_types=None):
    """
    Valida um arquivo enviado pelo usuário.
    
    Args:
        file: O arquivo a ser validado
        max_size_mb: Tamanho máximo permitido em MB
        allowed_types: Lista de tipos MIME permitidos
    
    Raises:
        ValidationError: Se o arquivo não atender aos requisitos
    """
    if not file:
        raise ValidationError('Nenhum arquivo foi enviado.')
    
    # Verifica o tamanho do arquivo
    max_size = max_size_mb * 1024 * 1024  # Converte MB para bytes
    if file.size > max_size:
        raise ValidationError(f'O arquivo é muito grande. Tamanho máximo permitido: {max_size_mb}MB')
    
    # Verifica o tipo do arquivo
    if allowed_types:
        content_type = file.content_type
        if content_type not in allowed_types:
            raise ValidationError(f'Tipo de arquivo não permitido. Tipos permitidos: {", ".join(allowed_types)}')
    
    # Verifica se o arquivo está corrompido
    try:
        # Tenta ler os primeiros bytes do arquivo
        file.seek(0)
        file.read(1)
        file.seek(0)  # Retorna o ponteiro para o início
    except Exception:
        raise ValidationError('O arquivo parece estar corrompido ou é inválido.')
    
    return True 

def validate_cpf(cpf):
    """
    Valida um CPF brasileiro.
    Retorna True se o CPF for válido, False caso contrário.
    """
    # Remove caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, cpf))
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Validação do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = 11 - (soma % 11)
    if digito1 > 9:
        digito1 = 0
    
    # Validação do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = 11 - (soma % 11)
    if digito2 > 9:
        digito2 = 0
    
    # Verifica se os dígitos calculados correspondem aos dígitos informados
    return int(cpf[9]) == digito1 and int(cpf[10]) == digito2 

def is_superadmin(user):
    """Verifica se o usuário é um superadmin"""
    return user.is_superuser

def is_vendedor(user):
    """Verifica se o usuário é um vendedor"""
    return hasattr(user, 'vendedor') 