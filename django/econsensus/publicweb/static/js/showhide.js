/*
Show/hide the showable class amongst multiple,
with activation via a show button
*/
  $(document).ready(function() {
    $(".controls .form_cancel").on("click", function(e) {
      $(".showable").hide();
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
    
    $(".feedback_list").on("click", "li > .feedback_wrapper > .description > .show", function(e) {
      var this_showable_thing  = $(this).parent().siblings().find(".showable");
      $(".showable").hide();
      this_showable_thing.parsley()
      this_showable_thing.show();
      // Ensure "Post" button is on screen
      this_showable_thing.find(".button").focus();
      // Move focus to where user will type
      this_showable_thing.find("textarea").focus();
      e.stopPropagation();
      e.preventDefault();
    });
    
    $(".showable").on("click", function(e) {
      e.stopPropagation();
    });
  });
