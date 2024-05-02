let inModal = false;
let userName = null;

let konamiCode = '';
const secretCode = 'ArrowUpArrowUpArrowDownArrowDownArrowLeftArrowRightArrowLeftArrowRightba'; // Code Konami en ASCII

function open_modal(id, page) {
    inModal = true;
    $(id).modal('show');
    if (page !== null) {
        // gotoPage(page, true, false);
        const newLocation = document.getElementById("newLocation");
        newLocation.innerHTML = page;
    }
}

function close_modal(id) {
    inModal = false;
    $(id).modal('hide');
    const newLocation = document.getElementById("newLocation").innerHTML;
    if (newLocation !== "undefined") {
        gotoPage(newLocation, true, false);
    }
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
            konamiCode = ""; // Réinitialiser le code Konami
        } else {
            konamiCode = ""
        }

    }
});

function checkLoggedIn(page= null, openModal = true) {
    const userName = getUserName();
    console.log(userName)
    if (!userName) {
        // Si l'utilisateur n'est pas connecté, afficher la popup de connexion
        if (openModal) {
            open_modal('#loginModal', page)
        }
        return false;
    }
    return true;
}

function logout() {
    localStorage.removeItem('user'); // Remove user data from localStorage
    // Remove token from localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('access-token');
    updateNavBar(null); // Update navigation bar to show login and signup buttons
    do_logout_request();
}

function do_logout_request() {
    fetch('/logout', {
        method: 'POST',
    }).then(response => {
        if (response.ok) {
            console.log('Déconnexion réussie');
            window.location.href = "/";
        } else {
            console.error('Erreur lors de la déconnexion');
        }
    }).catch(error => {
        console.error('Erreur lors de la déconnexion', error);
    });
}

function getUserName() {
    const userStr = localStorage.getItem('user')
    console.log(userStr)
    if (!userStr) {
        return null
    }
    const user = JSON.parse(userStr)
    const now = new Date()

    if (now.getTime() > user.expiry) {
        localStorage.removeItem('user')
        $('#loginModal').modal('show');
        return null
    }
    return user.name
}

async function makeRequest(mode) {
    const formData = new FormData(document.getElementById(mode + 'Form'));

    try {
        const response = await fetch('/' + mode, {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            const jsonResponse = await response.json();
            const now = new Date()
            const user = {
                name: jsonResponse.username,
                expiry: now.getTime() + 120 * 60 * 1000
            }
            localStorage.setItem("user", JSON.stringify(user));
            // On supprime l' username du storage une fois que le token a expiré
            updateNavBar(jsonResponse.username)
            // Fermer la modale
            close_modal('#' + mode + 'Modal')
        } else {
            const errorMessage = await response.json();
            if (mode === 'signup') {
                // Display error message in the modal
                const errorDiv = document.createElement('div');
                errorDiv.className = 'alert alert-danger';
                errorDiv.textContent = errorMessage.detail;
                const modalBody = document.querySelector('#modal-body');
                modalBody.prepend(errorDiv);

                // Change username input to class 'danger'
                usernameInput.classList.add('is-invalid');
            }
        }
    } catch (error) {
        console.error('Erreur lors de l\'envoi de la requête AJAX', error);
    }
}

function updateNavBar(username) {
    const userMenu = document.getElementById('userMenu');
    if (username) {
        userMenu.innerHTML = `<span class="navbar-text" style="margin-right: 1em">Bienvenue, ${username}!</span>
                                  <button type="button" class="btn btn-link" onclick="logout()">Déconnexion</button>`;
    } else {
        userMenu.innerHTML = `<button type="button" class="btn btn-link" onclick="open_modal('#loginModal')">Connexion</button>
                                  <button type="button" class="btn btn-link" onclick="open_modal('#signupModal')">Inscription</button>`;
    }
}


async function gotoPage(page, checkLogin = true, openModal = true) {
    if (checkLogin && !checkLoggedIn(page, openModal)) {
        return;
    }
    window.location = page;
}


function showToast(id) {
    const toastContainer = document.getElementById('toastContainer');

    // Créez le contenu du toast
    // Ajoutez le toast au conteneur
    toastContainer.innerHTML = `
            <div class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-delay="10000">
                <div class="toast-header">
                    <strong class="mr-auto">Félicitations</strong>
                    <button type="button" class="ml-2 mb-1 close" data-dismiss="toast" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="toast-body">
                    Badge secret débloqué !
                    <br>
                    <img src="/badges/${id}.gif" class="img-thumbnail" alt="Badge Image">
                </div>
            </div>
        `;

    // Affichez le toast
    $('.toast').toast('show');
}

function onLoaded() {
    userName = getUserName();
    updateNavBar(userName);
}

document.addEventListener('DOMContentLoaded', onLoaded);
