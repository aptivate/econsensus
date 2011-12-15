
$(document).ready(function() {
    $("div.description textarea").addClass("collapsed");
    $("div.description textarea").addClass("feedbacktextbox");
    
    $("textarea.feedbacktextbox").each(function(){
    	$(this).mouseover(function(){
    		
    		$(this).addClass("expanded").removeClass("collapsed");
    	});
    	$(this).mouseout(function(){
    		$(this).addClass("collapsed").removeClass("expanded");
    	});
    });    
});
