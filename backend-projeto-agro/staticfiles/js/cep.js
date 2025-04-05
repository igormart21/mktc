function buscarCEP(cep) {
    // Remove caracteres não numéricos
    cep = cep.replace(/\D/g, '');
    
    // Verifica se o CEP tem 8 dígitos
    if (cep.length !== 8) {
        return;
    }

    // Faz a requisição para a API do ViaCEP
    fetch(`https://viacep.com.br/ws/${cep}/json/`)
        .then(response => response.json())
        .then(data => {
            if (!data.erro) {
                // Preenche os campos do formulário
                document.getElementById('id_rua').value = data.logradouro;
                document.getElementById('id_numero').value = '';
                document.getElementById('id_complemento').value = data.bairro;
            } else {
                alert('CEP não encontrado');
            }
        })
        .catch(error => {
            console.error('Erro ao buscar CEP:', error);
            alert('Erro ao buscar CEP');
        });
}

// Adiciona o evento de input no campo CEP
document.addEventListener('DOMContentLoaded', function() {
    const cepInput = document.getElementById('id_cep');
    if (cepInput) {
        cepInput.addEventListener('input', function(e) {
            let cep = e.target.value;
            // Formata o CEP com hífen
            cep = cep.replace(/(\d{5})(\d{3})/, '$1-$2');
            e.target.value = cep;
            
            // Busca o CEP quando tiver 8 dígitos
            if (cep.replace(/\D/g, '').length === 8) {
                buscarCEP(cep);
            }
        });
    }
}); 