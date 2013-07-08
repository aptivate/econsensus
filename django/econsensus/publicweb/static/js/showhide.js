/*
Show/hide the showable class amongst multiple,
with activation via a show button
Objects are automatically hidden if the 
user clicks outside the area
*/
  $(document).ready(function() {
    $("body").live("click", function() {
      $(".showable").hide();
    });
    
    $(".show").live("click", function(e) {
    var this_showable_thing  = $(this).parent().siblings().find(".showable");
      $(".showable").hide();
      this_showable_thing.show();
      e.stopPropagation();
      e.preventDefault();
    });
    
    $(".showable").live("click", function(e) {
      e.stopPropagation();
    });
  });
