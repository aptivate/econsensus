/*
Show/hide the feedback_comment class amongst multiple,
with activation via a show button
*/
  $(document).ready(function() {
    $(".controls .form_cancel").on("click", function(e) {
      $(".form_comment").hide();
      e.stopPropagation();
      e.preventDefault();
    });
    
    $(".controls .form_submit").on("click", function(e) {
    	var this_comment_form  = $(this).parent().parent();
    	if(!this_comment_form.parsley('validate'))
    	{
    		e.stopPropogation();
    		e.preventDefault();
    	}
      });
    
    $(".show").on("click", function(e) {
      var this_comment_form  = $(this).parent().siblings().find(".form_comment");
      $(".form_comment").hide();
      this_comment_form.parsley()
      this_comment_form.show();
      // Ensure "Post" button is on screen
      this_comment_form.find(".button").focus();
      // Move focus to where user will type
      this_comment_form.find("textarea").focus();
      e.stopPropagation();
      e.preventDefault();
    });
    
    $(".form_comment").on("click", function(e) {
      e.stopPropagation();
    });
  });
