document.addEventListener('DOMContentLoaded', function() {
    const tipoDocumentoField = document.querySelector('select[name="tipo_documento"]');
    const ufDocumentoField = document.querySelector('.uf-documento-field');
    const orgaoEmissorField = document.querySelector('.orgao-emissor-field');

    function toggleCamposRG() {
        const isRG = tipoDocumentoField.value === 'RG';
        
        if (ufDocumentoField) {
            ufDocumentoField.closest('.form-row').style.display = isRG ? '' : 'none';
            ufDocumentoField.required = isRG;
        }
        
        if (orgaoEmissorField) {
            orgaoEmissorField.closest('.form-row').style.display = isRG ? '' : 'none';
            orgaoEmissorField.required = isRG;
        }
    }

    if (tipoDocumentoField) {
        tipoDocumentoField.addEventListener('change', toggleCamposRG);
        toggleCamposRG(); // Executa na carga inicial
    }
}); 