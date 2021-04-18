function requestPage(number) {
    return new Promise((resolve) => {
        $.post("/gallery-page/", {'page': number}, (data) => {
            resolve(data);
        });
    });
}

$(document).ready(function () {
    let current = 1;
    let load_images_button = $("#load-images-button");
    load_images_button.click(function () {
        current++;
        requestPage(current).then(results => {
            let photos = results["photos"];
            for (let i = 0; i < photos.length; i++) {
                let photo = photos[i];
                let photoPreview = `
                    <a class="grid-item" href="${photo.link}" aria-label="${photo.alt}" style="background-image: url('${photo.src}')">
                        <div class="image-clicker">
                            <p class="h3">Click To View</p>
                        </div>
                    </a>`;
                $(".grid").append(photoPreview);
            }
            if (results["hasNext"] === false) {
                load_images_button.prop("disabled", true);
                load_images_button.text("There Are No More Images");
            }
        });
    });
    if ($(".grid-item").length === 0) {
        load_images_button.prop("disabled", true);
        load_images_button.text("There Are No Images");
    }
});