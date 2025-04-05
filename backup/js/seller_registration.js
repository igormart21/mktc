document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('sellerRegistrationForm');
    const cepInput = document.getElementById('zip_code');
    const addressInput = document.getElementById('address');
    const cityInput = document.getElementById('city');
    const stateInput = document.getElementById('state');
    const password1 = document.getElementById('password1');
    const password2 = document.getElementById('password2');
    const documentFile = document.getElementById('document_file');

    // Máscara para o CEP
    cepInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length > 8) value = value.slice(0, 8);
        value = value.replace(/(\d{5})(\d)/, '$1-$2');
        e.target.value = value;
    });

    // Buscar endereço pelo CEP
    cepInput.addEventListener('blur', function(e) {
        const cep = e.target.value.replace(/\D/g, '');
        if (cep.length !== 8) return;

        fetch(`https://viacep.com.br/ws/${cep}/json/`)
            .then(response => response.json())
            .then(data => {
                if (data.erro) {
                    showError(cepInput, 'CEP não encontrado');
                    return;
                }
                addressInput.value = data.logradouro;
                cityInput.value = data.localidade;
                stateInput.value = data.uf;
                clearError(cepInput);
            })
            .catch(error => {
                showError(cepInput, 'Erro ao buscar CEP');
                console.error('Erro:', error);
            });
    });

    // Função para mostrar erro em um campo
    function showError(input, message) {
        const formGroup = input.closest('.input-group');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback d-block';
        errorDiv.textContent = message;
        formGroup.appendChild(errorDiv);
        input.classList.add('is-invalid');
    }

    // Função para limpar erro de um campo
    function clearError(input) {
        input.classList.remove('is-invalid');
        const formGroup = input.closest('.input-group');
        const errorDiv = formGroup.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    // Validar senhas
    function validatePasswords() {
        if (password1.value !== password2.value) {
            password2.setCustomValidity('As senhas não coincidem');
        } else {
            password2.setCustomValidity('');
        }
    }

    // Validar arquivo
    function validateFile() {
        const file = documentFile.files[0];
        if (file) {
            const validTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
            const maxSize = 5 * 1024 * 1024; // 5MB
            
            if (!validTypes.includes(file.type)) {
                documentFile.setCustomValidity('Por favor, envie um arquivo PDF, JPG ou PNG');
            } else if (file.size > maxSize) {
                documentFile.setCustomValidity('O arquivo deve ter no máximo 5MB');
            } else {
                documentFile.setCustomValidity('');
            }
        }
    }

    // Validar CEP
    async function validateCEP() {
        const cep = cepInput.value.replace(/\D/g, '');
        if (cep.length === 8) {
            try {
                const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
                const data = await response.json();
                
                if (!data.erro) {
                    addressInput.value = data.logradouro;
                    cityInput.value = data.localidade;
                    stateInput.value = data.uf;
                }
            } catch (error) {
                console.error('Erro ao buscar CEP:', error);
            }
        }
    }

    // Event listeners
    password2.addEventListener('input', validatePasswords);
    documentFile.addEventListener('change', validateFile);
    cepInput.addEventListener('blur', validateCEP);

    // Validar formulário antes de enviar
    form.addEventListener('submit', function(event) {
        validatePasswords();
        validateFile();
        
        if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
        }
        
        form.classList.add('was-validated');
    });

    // Formatação do CPF
    const cpfInput = document.getElementById('cpf');
    if (cpfInput) {
        cpfInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 11) {
                value = value.slice(0, 11);
            }
            e.target.value = value;
        });
    }

    // Validação do formulário
    if (form) {
        form.addEventListener('submit', function(e) {
            const cpf = document.getElementById('cpf').value;
            if (!validateCPF(cpf)) {
                e.preventDefault();
                alert('CPF inválido. Por favor, verifique o número informado.');
            }
        });
    }
});

function validateCPF(cpf) {
    // Remove caracteres não numéricos
    cpf = cpf.replace(/\D/g, '');
    
    // Verifica se tem 11 dígitos
    if (cpf.length !== 11) {
        return false;
    }
    
    // Verifica se todos os dígitos são iguais
    if (/^(\d)\1+$/.test(cpf)) {
        return false;
    }
    
    // Validação do primeiro dígito verificador
    let sum = 0;
    for (let i = 0; i < 9; i++) {
        sum += parseInt(cpf.charAt(i)) * (10 - i);
    }
    let digit = 11 - (sum % 11);
    if (digit > 9) {
        digit = 0;
    }
    if (digit !== parseInt(cpf.charAt(9))) {
        return false;
    }
    
    // Validação do segundo dígito verificador
    sum = 0;
    for (let i = 0; i < 10; i++) {
        sum += parseInt(cpf.charAt(i)) * (11 - i);
    }
    digit = 11 - (sum % 11);
    if (digit > 9) {
        digit = 0;
    }
    if (digit !== parseInt(cpf.charAt(10))) {
        return false;
    }
    
    return true;
} 