/*
Show/hide the feedback_comment class amongst multiple,
with activation via a show button
Objects are automatically hidden if the 
user clicks outside the area
*/
  $(document).ready(function() {
    $("body").click(function() {
      $(".form_comment").hide();
    });
    
    $(".show").click(function(e) {
    var this_comment_form  = $(this).parent().siblings().find(".form_comment");
      $(".form_comment").hide();
      this_comment_form.show();
      e.stopPropagation();
      e.preventDefault();
    });
    
    $(".form_comment").click(function(e) {
      e.stopPropagation();
    });
  });
