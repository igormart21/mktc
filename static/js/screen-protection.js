// Prevenir captura de tela em dispositivos móveis
document.addEventListener('DOMContentLoaded', function() {
    // Prevenir captura de tela em dispositivos móveis
    if (navigator.userAgent.match(/Android|iPhone|iPad|iPod/i)) {
        // Desabilitar eventos de toque que podem ser usados para captura
        document.addEventListener('touchstart', function(e) {
            if (e.touches.length > 1) {
                e.preventDefault();
            }
        }, { passive: false });

        // Desabilitar eventos de teclado que podem ser usados para captura
        document.addEventListener('keydown', function(e) {
            if (e.key === 'PrintScreen' || 
                (e.ctrlKey && e.key === 'p') || 
                (e.ctrlKey && e.key === 's')) {
                e.preventDefault();
            }
        });
    }

    // Prevenir captura de tela em desktop
    document.addEventListener('keydown', function(e) {
        if (e.key === 'PrintScreen' || 
            (e.ctrlKey && e.key === 'p') || 
            (e.ctrlKey && e.key === 's')) {
            e.preventDefault();
        }
    });

    // Desabilitar o menu de contexto (botão direito)
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
    });

    // Adicionar CSS para desabilitar seleção de texto
    const style = document.createElement('style');
    style.textContent = `
        * {
            -webkit-user-select: none !important;
            -moz-user-select: none !important;
            -ms-user-select: none !important;
            user-select: none !important;
        }
    `;
    document.head.appendChild(style);

    // Detectar tentativas de captura de tela
    window.addEventListener('beforeprint', function(e) {
        e.preventDefault();
        alert('Captura de tela não é permitida neste site.');
    });

    // Desabilitar DevTools
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'i' || e.key === 'J' || e.key === 'j')) {
            e.preventDefault();
        }
    });
}); 