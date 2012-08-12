function slideSwitch() {
	var $active = $('#slideshow IMG.active-img');

	if($active.length == 0)
		$active = $('#slideshow IMG:last');

	var $next = $active.next('IMG').length ? $active.next('IMG') : $('#slideshow IMG:first');

	$active.addClass('last-active-img');

	$next.css({
		opacity : 0.0
	}).addClass('active-img').animate({
		opacity : 1.0
	}, 1000, function() {
		$active.removeClass('active-img last-active-img');
	});
}

function textSwitch() {
	//console.log('hi');
	var $active1 = $('#slideshow DIV.active-txt');
	//console.log($active1);
	if($active1.length == 0)
		$active1 = $('#slideshow DIV:last');

	var $next1 = $active1.next('DIV').length ? $active1.next('DIV') : $('#slideshow DIV:first');

	$active1.addClass('last-active-txt');

	$next1.css({
		opacity : 0.0
	}).addClass('active-txt').animate({
		opacity : 1.0
	}, 1000, function() {
		$active1.removeClass('active-txt last-active-txt');
	});
}

function hart_clicked(element)
{
	myslug = element.getAttribute("slug");
	//products = Product.objects.get(slug=myslug);
	console.log("hart_clicked on slug=" + myslug);
	return false;
}


function getProductList(url, element) {
	$.getJSON(url, function(data) {
		var items = [];
		for(var i = 0; i < data.products.length; i++) {
			html = '<div class="home-product"><a class="home-product-pointer" href="' + data.products[i].product_url + '">'+
				   '<img class="home-product-mainImage" src="' + data.products[i].image_url + '" /></a>'+
				   '<p class="home-product-name">'+ data.products[i].name +'</p>' +
				   '<div class="home-product-lovemeImage" slug="' + data.products[i].slug + '" onclick="return hart_clicked(this)" alt="loveme"></div>'+ 
				   '<p class="home-product-price">$'+ data.products[i].price.toFixed(2) + 
				   '</div>';
			$(html, {
				'class' : 'home-product-list',
				html : ''
			}).appendTo(element);
		}
	});	
}


$(function() {
	getProductList('/explorer/get_top_inspirations', '#top-inspirations');
	getProductList('/explorer/get_recent_products', '#recent-products');
	setInterval("slideSwitch()", 4000);
	setInterval("textSwitch()", 4000);
	$('#slideshow').on('click', function() {
		window.location = '/create'
	});
});
