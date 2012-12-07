//only call this once
if ($('.paginationform').length === 1) {
    $(document).ready(function () {
        $('.pagination-num-items').change(function () {
            $(this).parent('.paginationform').submit();
        });
    });
}
