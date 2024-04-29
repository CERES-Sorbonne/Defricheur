    function checkLoggedIn() {
        const userName = getUserName();
        console.log(userName)
        if (!userName) {
            // Si l'utilisateur n'est pas connecté, afficher la popup de connexion
            $('#loginModal').modal('show');
            return false;
        }
        return true;
    }
    function logout() {
        localStorage.removeItem('user'); // Remove user data from localStorage
        // Remove token from localStorage
        localStorage.removeItem('token');
        updateNavBar(null); // Update navigation bar to show login and signup buttons
        window.location.href="/";
    }
    function getUserName(){
        const userStr = localStorage.getItem('user')
        if (!userStr){
            return null
        }
        const user = JSON.parse(userStr)
        const now = new Date()

        if (now.getTime() > user.expiry){
            localStorage.removeItem('user')
            $('#loginModal').modal('show');
            return null
        }
        return user.name
    }
    const userName = getUserName()
    if(userName){
        updateNavBar(userName)
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
                // On supprime le username du storage une fois que le token a expiré
                updateNavBar(jsonResponse.username)
                // Fermer la modale
                $('#' + mode + 'Modal').modal('hide');
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
    document.querySelectorAll('.nav-link').forEach((link, index) => {
        link.addEventListener('click', function(event) {
            // Vérifier si l'utilisateur est connecté avant de suivre le lien,
            // sauf pour le premier lien
            if (index !== 0 && !checkLoggedIn()) {
                event.preventDefault(); // Empêcher le lien de s'exécuter normalement
            }
        });
    });

    let konamiCode = '';
    const secretCode = 'ArrowUpArrowUpArrowDownArrowDownArrowLeftArrowRightArrowLeftArrowRightba'; // Code Konami en ASCII


    function showToast(id){
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