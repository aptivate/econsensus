//The pagination section may appear multiple times on a page, but we only want to call this function once, and only once the document is ready. It will then apply the "on change" function to all instances of the pagination-num-items select box.
if ($('.paginationform').length === 1) {
    $(document).ready(function () {
        //When the user changes the number of items they want to display in the select box with class "pagination-num-items" we automatically submit the form for them (there is a no-javascript fallback in the main template).
        $('.pagination-num-items').change(function () {
            $(this).parent('.paginationform').submit();
        });
    });
}
