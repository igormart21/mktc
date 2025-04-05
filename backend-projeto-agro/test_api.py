import requests
import json

# URL base da API
BASE_URL = 'http://127.0.0.1:8000'

# Dados de login
login_data = {
    'email': 'westervictor94@gmail.com',
    'password': 'Agro12345@'
}

# Obter token
print('Obtendo token...')
response = requests.post(f'{BASE_URL}/api/token/', json=login_data)
if response.status_code == 200:
    token = response.json()['access']
    print('Token obtido com sucesso!')
    
    # Fazer requisição para o perfil
    headers = {
        'Authorization': f'Bearer {token}'
    }
    print('\nObtendo perfil do usuário...')
    response = requests.get(f'{BASE_URL}/api/usuarios/perfil/', headers=headers)
    
    if response.status_code == 200:
        print('\nPerfil obtido com sucesso!')
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print(f'\nErro ao obter perfil: {response.status_code}')
        print(response.text)
else:
    print(f'Erro ao obter token: {response.status_code}')
    print(response.text) 