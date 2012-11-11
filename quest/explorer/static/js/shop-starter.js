var TMInterval = 20;
var TMlast = 30;
$(function() {
	$('#slideshow').cycle({ 
	    fx:    'fade', 
	    speed:  2500 
 	});
	jsonobj = {"limits":"0-10","sorter":"stock_amount"};
	//jsonstr = JSON.stringify(jsonobj);
	//getProductList('/get_ssp/'+jsonstr, '#top-inspirations');
		TMLoadMore(jsonobj,0, 15,'#top-inspirations');
		setTimeout(function(){TMLoadMore(jsonobj,15, 30,'#top-inspirations');}, 1000);
		$(document).scroll(function(){
			console.log('scroll');
			if($(window).scrollTop()+$(window).height()>=$(document).height()-200) {
				TMLoadMore(jsonobj,TMlast, TMlast+TMInterval, '#top-inspirations');
				TMlast = TMlast+TMInterval;
				console.log('load!!!');
			}
			
		});
	//jsonobj = {"limits":"0-10","sorter":"creation_date"};
	//jsonstr = JSON.stringify(jsonobj);
	//getProductList('/get_ssp/'+jsonstr, '#recent-products');

});
