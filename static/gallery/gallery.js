function requestNextImageSet(number) {
    return new Promise((resolve) => {
        $.post("/gallery-page/", {'page': number}, (data) => {
            resolve(data);
        });
    });
}

$(document).ready(function() {
    let current = 1;
    let grid = $(".image-grid");
    let cell = $("#load-images-cell")
    let button = $("#load-images-button");
    button.click(function() {
        current++;
        button.addClass("is-loading");
        requestNextImageSet(current).then(function(results) {
            let photos = results["photos"];
            for (let photo of photos) {
                let appendString = `
                <div class="image-grid-cell">
                    <a href="${photo["link"]}" class="image-grid-item-wrapper">
                        <img class="image-grid-item" src="${photo["src"]}" alt="${photo["alt"]}" />
                    </a>
                </div>`;
                cell.detach()
                $(appendString).appendTo(grid);
            }
            if (results["hasNext"]) {
                grid.append(cell);
                button.removeClass("is-loading");
            }
        });
    });
});