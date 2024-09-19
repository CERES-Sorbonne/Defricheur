let haveYouSeenTheCorrection = false;
let dico = {}
let changing = false;
let host = window.location.href.replace("annotate", "")
while (host.endsWith("/")) {
    host = host.slice(0, -1)
}

function modifyPage(data) {
    document.querySelector('#seed_text').innerText = data.seed_text;
    document.querySelector('#tweet_text').innerText = data.tweet_text;
    document.querySelector('#shown_tweet_id').innerText = data.shown_tweet_id;
    document.querySelector('#total_block').innerText = data.total_block;
    let style = document.getElementById('expression').style;
    let percent = (data.shown_tweet_id / data.total_block) * 100
    let newStyle = `linear-gradient(90deg, #FBA69E ${percent}%, #FFF 0%)`
    style.setProperty('--background', newStyle)

    const buttons = document.querySelectorAll('.answer');
    buttons.forEach(button => {
        button.classList.remove('accent');
    })
    if (data.newBadge) {
        displayToast(data.newBadge);
    }

    const UMWE = data.UMWE_identified_answer;
    const UMWEButtons = document.querySelectorAll('.UMWE_identified');
    if (UMWE !== 4) {
        UMWEButtons.forEach(button => {
            if (button.name === UMWE) {
                button.classList.add('accent');
            }
        });
    }

    const MWE = data.MWE_recognized_answer;
    const MWEButtons = document.querySelectorAll('.MWE_recognized');
    if (MWE !== 4) {
        MWEButtons.forEach(button => {
            if (button.name === MWE) {
                button.classList.add('accent');
            }
        });
    }

}

async function getData(order = null) {
    try {
        const body = {}
        if (order) {
            body.order = order
        }
        if (dico.blockId) {
            body.block_id = dico.blockId
        }
        if (dico.tweetId) {
            body.tweet_id = dico.tweetId
        }
        const response = await fetch(host + '/data/', {
            method: 'POST',
            credentials: 'include',
            body: JSON.stringify(body)
        })
        if (response.ok) {
            const data = await response.json()
            modifyPage(data)
            return data
        }
    } catch {

    }
}

async function tuto_done() {
    try {
        const response = await fetch('/isTutoDone/', {
            method: 'GET',
            credentials: 'include',
        })
        if (response.ok) {
            const data = await response.json()
            return data
        }
    } catch {
        console.error('Erreur lors de l\'envoi de la requête AJAX')
        return true
    }

}

async function onChange(order) {
    if (changing) {
        return;
    }
    changing = true;
    // This is a hack to prevent the user from clicking too fast and skipping the training altogether
    if (dico.__type__ === "training" || dico.__type__ === "control") {
        const isTraining = await deal_with_training();
        if (isTraining) {
            changing = false;
            return;
        }
    }

    const block_id = dico.block_id;
    const tweet_id = dico.current_tweet_index;


    if (block_id === 0 && tweet_id === 19 && order === 1) {
        const tutorial_done = await tuto_done();
        if (!tutorial_done) {
            await open_modal('#cPasFini');
            changing = false;
            return;
        }
    }

    dico = await getData(order);
    await retour_vers_le_passe();
    changing = false;
}

async function retour_vers_le_passe() {
    const correction_container = document.getElementById("correction-container");
    correction_container.style.display = "none";

    const bonne_reponse = document.getElementById("bonne-reponse");
    const mauvaise_reponse = document.getElementById("mauvaise-reponse");
    bonne_reponse.style.display = "none";
    mauvaise_reponse.style.display = "none";

    haveYouSeenTheCorrection = false;

    if (dico.__type__ === "training" || dico.__type__ === "control") {
        await deal_with_training(true);
    }
}

async function answer(value, questionNumber, buttonId) {
    const form = document.getElementById(buttonId).closest('form');
    const buttons = form.querySelectorAll('button');

    try {
        const response = await fetch(host + '/annotate/', {
            method: 'POST',
            credentials: 'include',
            body: JSON.stringify({
                annotation: value,
                question: questionNumber,
                // seedId: dico.seed_id,
                tweetId: dico.tweet_id,
                tweetIndex: dico.current_tweet_index,
                blockId: dico.block_id,
                timestamp: Date.now()
            }),
            // headers: {
            //     'Authorization': 'Bearer ' + document.cookie.split(';')[0].split('=')[1]
            // }
        });

        if (response.ok) {
            buttons.forEach(button => {
                if (button.id === buttonId) {
                    button.classList.add('accent');
                } else {
                    button.classList.remove('accent');
                }
            });
        } else {
            console.error('Échec de la requête AJAX');
        }
    } catch (error) {
        console.error('Erreur lors de l\'envoi de la requête AJAX', error);
    }
}

function displayToast(badgeName) {
    // Sélectionnez le conteneur de toast dans le DOM
    const toastContainer = document.getElementById('toastContainer');

    // Créez le contenu du toast
    // Ajoutez le toast au conteneur
    toastContainer.innerHTML = `
            <div class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-delay="5000">
                <div class="toast-header">
                    <strong class="mr-auto">Félicitations</strong>
                    <button type="button" class="ml-2 mb-1 close" data-dismiss="toast" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="toast-body">
                    Vous avez débloqué un nouveau badge!
                    <br>
                    <img src="/badges/${badgeName}.png" class="img-thumbnail" alt="Badge Image">
                </div>
            </div>
        `;

    // Affichez le toast
    $('.toast').toast('show');
}

document.addEventListener("DOMContentLoaded", async function () {
        dico = await getData();

        if (dico.__type__ === "training" || dico.__type__ === "control") {
            await deal_with_training(true);
        }
        if (dico.block_id === 0) {
            await open_modal('#tutoModal');
        }
    }
);

// Fonction pour gérer les événements de touche
document.addEventListener("keydown", function (event) {
    if (inModal) {
        return;
    }
    switch (event.key) {
        case "a":
        case "A":
            document.getElementById("3").click();
            break;
        case "z":
        case "Z":
            document.getElementById("4").click();
            break;
        case "e":
        case "E":
            document.getElementById("5").click();
            break;
        case "q":
        case "Q":
            document.getElementById("0").click();
            break;
        case "s":
        case "S":
            document.getElementById("1").click();
            break;
        case "d":
        case "D":
            document.getElementById("2").click();
            break;
        case "ArrowRight":
        case "Enter":
            document.getElementById("suivant").click();
            break;
        case "ArrowLeft":
        case "Backspace":
            document.getElementById("precedent").click();
            break;
    }
});

async function deal_with_training(on_start = false) {
    if (haveYouSeenTheCorrection && !on_start) {
        return false;
    }
    const isWellAnnotated = await is_well_annotated();

    if (isWellAnnotated === null) {
        return false;
    }
    // Put the correction message in the correction message container
    const correction_message = document.getElementById("correction-message");
    correction_message.innerText = dico.correction;

    // Display the good or bad response
    const correction_container = document.getElementById("correction-container");
    const bonne_reponse = document.getElementById("bonne-reponse");
    const mauvaise_reponse = document.getElementById("mauvaise-reponse");

    correction_container.classList.remove("success");
    correction_container.classList.remove("danger");

    if (isWellAnnotated) {
        bonne_reponse.style.display = "block";
        correction_container.classList.add("success");
    } else {
        mauvaise_reponse.style.display = "block";
        correction_container.classList.add("danger");
    }

    const correction_precisions = document.getElementById("correction-precisions");
    message = await do_message();
    correction_precisions.innerText = message;

    if (dico.correction) {
        correction_message.style.display = "block";
        correction_precisions.style.display = "none";
    } else {
        correction_message.style.display = "none";
        correction_precisions.style.display = "block";
    }

    // Display the correction container once everything is set and return true
    correction_container.style.display = "block";

    haveYouSeenTheCorrection = true;
    return true;
}

async function is_well_annotated() {
    const buttons_accented = document.querySelectorAll('.accent');

    const MWE_butt = Array.from(buttons_accented).find(button => button.classList.contains('MWE_recognized'));
    const UMWE_butt = Array.from(buttons_accented).find(button => button.classList.contains('UMWE_identified'));

    if (MWE_butt === undefined || UMWE_butt === undefined) {
        return null;
    }

    const MWE_answer = MWE_butt.name;
    const UMWE_answer = UMWE_butt.name;

    return !(MWE_answer !== dico.MWE_recognized_correction || UMWE_answer !== dico.UMWE_identified_correction);

}

async function do_message() {
    const buttons_accented = document.querySelectorAll('.accent');

    const MWE_butt = Array.from(buttons_accented).find(button => button.classList.contains('MWE_recognized'));
    const UMWE_butt = Array.from(buttons_accented).find(button => button.classList.contains('UMWE_identified'));

    if (MWE_butt === undefined || UMWE_butt === undefined) {
        return null;
    }

    const MWE_answer = MWE_butt.name;
    const UMWE_answer = UMWE_butt.name;
    let message = "Nous avons quelques remarques à faire sur ce tweet :\n\n";

    if (MWE_answer === "0" && dico.MWE_recognized_correction === "0") {
        message += " - en effet, l'expression recherchée ne se trouve pas dans ce tweet.";
    }
    if (MWE_answer === "1" && dico.MWE_recognized_correction === "0") {
        message += " - vous avez identifié l'expression recherchée dans ce tweet, mais elle ne s'y trouve pas.";
    }
    if (MWE_answer === "0" && dico.MWE_recognized_correction === "1") {
        message += " - vous n'avez pas identifié l'expression recherchée dans ce tweet.";
    }
    if (MWE_answer === "1" && dico.MWE_recognized_correction === "1") {
        message += " - en effet, l'expression recherchée se trouve dans ce tweet.";
    }
    if (MWE_answer === "2") {
        if (dico.MWE_recognized_correction === "0") {
            message += " - l'expression recherchée ne se trouve pas dans ce tweet.";
        }
        if (dico.MWE_recognized_correction === "1") {
            message += " - l'expression recherchée se trouve dans ce tweet.";
        }
    }

    message += "\n";
    if (UMWE_answer === "0" && dico.UMWE_identified_correction === "0") {
        message += " - en effet, ce tweet ne contient pas de message codé.";
    }
    if (UMWE_answer === "1" && dico.UMWE_identified_correction === "0") {
        message += " - vous avez détecté un message codé dans ce tweet, mais il n'en contient aucun.";
    }
    if (UMWE_answer === "0" && dico.UMWE_identified_correction === "1") {
        message += " - vous n'avez pas détecté le message codé caché dans ce tweet.";
    }
    if (UMWE_answer === "1" && dico.UMWE_identified_correction === "1") {
        message += " - en effet, ce tweet contient un message codé.";
    }
    if (UMWE_answer === "2") {
        if (dico.UMWE_identified_correction === "0") {
            message += " - ce tweet ne contient pas de message codé.";
        }
        if (dico.UMWE_identified_correction === "1") {
            message += " - ce tweet contient un message codé";
        }
    }

    return message;
}

document.addEventListener('DOMContentLoaded', mainPageIfNotConnected);
