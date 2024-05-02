let imgs_hover = {};
let url = "/static/imgs_hover.json";

let promise = fetch(url)
    .then(response => response.json())
    .then(data => {
        imgs_hover = data;
    }
    );

async function isJsonLoaded() {
    return promise.then(() => {
        return true;
    });
}


async function generateHover(img) {
    if (await isJsonLoaded()) {
        const parentDiv = img.parentElement;
        const accompanyingP = parentDiv.querySelector('p');
        const id = parentDiv.id;
        const text = imgs_hover[id];
        accompanyingP.innerHTML = text;
    }
    else {
        console.log("Json not loaded , WTF !");
    }
}

