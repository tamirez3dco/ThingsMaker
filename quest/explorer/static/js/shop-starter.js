var TMInterval = 20;
var TMlast = 30;
var TMCanLoad=true;
$(function() {
	$('#slideshow').cycle({ 
	    fx:    'fade', 
	    timeout:  1000,  
	    speed: 3000,
	    continous: 1
 	});
	jsonobj = {"limits":"0-10","sorter":"stock_amount"};
	//jsonstr = JSON.stringify(jsonobj);
	//getProductList('/get_ssp/'+jsonstr, '#top-inspirations');
		TMLoadMore(jsonobj,0, 15,'#top-inspirations');
		setTimeout(function(){TMLoadMore(jsonobj,15, 30,'#top-inspirations');}, 1000);
		$(document).scroll(function(){
			//console.log('scroll');
			if (TMlast>500) return;
			if($(window).scrollTop()+$(window).height()>=$(document).height()-350) {
				if(TMCanLoad==false) return;
				TMCanLoad=false;
				TMLoadMore(jsonobj,TMlast, TMlast+TMInterval, '#top-inspirations');
				TMlast = TMlast+TMInterval;
				//console.log('load!!!');
			}
			
		});
	//jsonobj = {"limits":"0-10","sorter":"creation_date"};
	//jsonstr = JSON.stringify(jsonobj);
	//getProductList('/get_ssp/'+jsonstr, '#recent-products');

});
