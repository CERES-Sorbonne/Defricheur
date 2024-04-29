let inModal = false;


function open_modal(id) {
    inModal = true;
    $(id).modal('show');
}

function close_modal(id) {
    inModal = false;
    $(id).modal('hide');
}

window.addEventListener('keydown', async function (e) {
    if (inModal) {
        const modal = document.querySelector('.modal.show');
        if (e.key === 'Escape') {
            close_modal(modal);
        }
        if (e.key === 'Enter') {
            const button = modal.querySelector('.button-modal');
            button.click();
        }
        return;
    }
    konamiCode += e.key;
    if (secretCode.slice(0, konamiCode.length) !== konamiCode) {
        konamiCode = ""
    }
    if (konamiCode.length === secretCode.length) {
        if (konamiCode === secretCode) {
            // Appeler la route /secret?q=k0nam1
            const response = await fetch('/secret?q=k0nam1')
            if (response.ok) {
                const data = await response.json()
                console.log('Secret révélé !');
                showToast(data.id)
            } else {
                console.error('Impossible de révéler le secret.');
            }
            konamiCode = ''; // Réinitialiser le code Konami
        } else {
            konamiCode = ""
        }

    }
});
