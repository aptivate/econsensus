
$(document).ready(function() {
    $("div.description textarea").addClass("collapsed");
    $("div.description textarea").addClass("feedbacktextbox");

    $("textarea.feedbacktextbox").each(function(){
    	$(this).click(function(){
    		if ($(this).is(".collapsed"))
    		{
        		$(this).addClass("expanded").removeClass("collapsed");
    		}
    		else if ($(this).is(".expanded"))
    		{
    			$(this).addClass("collapsed").removeClass("expanded");    	
    		}
    	});
    });
});
