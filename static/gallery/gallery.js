

function requestPage(number) {
    /**
     * This function queries the backend for a page of image objects
     * args:
     *  number: A *one* based index of what page you want
     * returns:
     *  a dictionary with the following values:
     *   photos:
     *    link: link to the picture
     *    alt: the caption for the image
     *   hasNext: whether or not there is a next page
     */

    return new Promise((resolve) => {

        $.post("/gallery-page/", {'page': number}, (data) => {

            resolve(data);

        });

    });

}

$(document).ready(() => {



});