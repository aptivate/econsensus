/*
Disables an element (e.g. submit button) of
the "once" class the first time it is clicked
*/
$(document).on("click", ".once", function(e) {
    if (this.has_been_clicked)
        e.preventDefault();
    else
        this.has_been_clicked = true;
});
