function requestPage(number) {
    return new Promise((resolve) => {
        $.post("/gallery-page/", {'page': number}, (data) => {
            resolve(data);
        });
    });
}

$(document).ready(function() {
    let current = 1;
    let grid = $(".image-grid");
    let button = $("#load-images-button");
    button.click(function() {
        current++;
        $("#load-images-button").addClass("is-loading");
        requestPage(current).then(function(results) {
            let photos = results["photos"];
            for (let photo of photos) {
                let appendString = `
                <div class="image-grid-item-outer-wrapper">
                    <a href="${photo["link"]}" class="image-grid-item-inner-wrapper">
                        <img src="${photo["src"]}" alt="${photo["alt"]}" />
                    </a>
                </div>`;
                button.detach()
                $(appendString).appendTo(grid);
                grid.append(button)
            }
            $("#load-images-button").removeClass("is-loading");
            if (!results["hasNext"]) {
                button.detach();
            }
        });
    });
});