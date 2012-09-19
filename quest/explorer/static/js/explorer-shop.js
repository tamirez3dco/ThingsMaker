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
	// first increase the number in element
	var currentNum = parseInt(element.innerText);
	currentNum += 1;
	element.innerHTML = "<small>"+currentNum +"<\small>";
	
	// next send the AJAX
	myslug = element.getAttribute("slug");

	$.post("/addlover", { 
    item_uuid: myslug 
	},
    	function(data) {
        /*	alert(data); */
    	}
	);
	return false;
}

function getProductList(url, element) {
	$.getJSON(url, function(data) {
		var items = [];
		for(var i = 0; i < data.products.length; i++) {
			var addClass = 'home-product';
			if (((i+1)%5) == 0) {
				console.log('last');
				addClass = 'home-product last';
			}
			html = '<div class="'+ addClass +'"><a class="home-product-pointer" href="' + data.products[i].product_url + '">'+
				   '<img class="home-product-mainImage" src="' + data.products[i].image_url + '" />'+
				   '<p class="home-product-name">'+ data.products[i].name +'</p>' +
				   '<p class="home-product-price">$'+ data.products[i].price.toFixed(2) + '</p></a>' +
				   '<div class="home-product-lovemeImage" slug="' + data.products[i].slug + '" onclick="return hart_clicked(this)" alt="loveme"><small>' + data.products[i].lovers +'</small></div>'+
				   '<div class="home-product-customize"><a href="/create?start_product='+ data.products[i].slug + '&material=' + data.products[i].material + '&textParam=' + data.products[i].text + '&product_type=variant" class="button">Customize</a></div>'+
				    + '</div>';
			$(html, {
				'class' : 'home-product-list',
				html : ''
			}).appendTo(element);
		}
	});	
}

