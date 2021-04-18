function requestPage(number) {
    return new Promise((resolve) => {
        $.post("/gallery-page/", {'page': number}, (data) => {
            resolve(data);
        });
    });
}
$(document).ready(function() {
    let current = 0;
    $("#load-images-button").click(function() {
        current++;
        requestPage(current).then(results => {
            let photos = results["photos"];
            for (let i = 0; i < photos.length;i++) {
                let photoPreview = `
 <a class="grid-item" href="${VIEW PHOTO LINK}" aria-label="${PHOTO CAPTION}" style="background-image: url('${PHOTO SOURCE}')">
     <div class="image-clicker">
         <p class="h3">Click To View</p>
     </div>
 </a>`;
                $(".grid").append(photoPreview);
            }
        });
    });
});