
$(function() {
	$('#slideshow').cycle({ 
	    fx:    'fade', 
	    speed:  2500 
 	});
	jsonobj = {"limits":"0-10","sorter":"stock_amount"};
	jsonstr = JSON.stringify(jsonobj);
	getProductList('/get_ssp/'+jsonstr, '#top-inspirations');

	jsonobj = {"limits":"0-10","sorter":"creation_date"};
	jsonstr = JSON.stringify(jsonobj);
	getProductList('/get_ssp/'+jsonstr, '#recent-products');

//	getProductList('/explorer/get_recent_products', '#recent-products');
	//setInterval("slideSwitch()", 4000);
	//setInterval("textSwitch()", 4000);
	//$('#slideshow').on('click', function() {
	//	window.location = '/create'
	//});
});
