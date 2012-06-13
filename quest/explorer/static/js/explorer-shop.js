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

function getRecentImages() {
	$.getJSON('/explorer/get_recent_products', function(data) {
		var items = [];
		for(var i = 0; i < data.products.length; i++) {
			//items.push('<li id=recent-product-img-"' + i + '">' + data.products[i] + '</li>');
			//items.push('<img id=recent-product-img-"' + i + '" src="' + data.products[i] + '">');
			html = '<img style="float: left; width: 135px; padding: 4px;" id=recent-product-img-"' + i + '" src="' + data.products[i] + '">'
			$(html, {
				'class' : 'my-new-list',
				html : ''
			}).appendTo('#recent-products');
		}
	});
}

function getTopInspirations() {
	$.getJSON('/explorer/get_top_inspirations', function(data) {
		var items = [];
		for(var i = 0; i < data.products.length; i++) {
			//items.push('<li id=recent-product-img-"' + i + '">' + data.products[i] + '</li>');
			//items.push('<img id=recent-product-img-"' + i + '" src="' + data.products[i] + '">');
			html = '<img style="float: left; width: 135px; padding: 4px;" id=top-insp-img-"' + i + '" src="' + data.products[i] + '">'
			$(html, {
				'class' : 'my-new-list',
				html : ''
			}).appendTo('#top-inspirations');
		}
	});
}
$(function() {
	getRecentImages();
	getTopInspirations();
	setInterval("slideSwitch()", 4000);
	setInterval("textSwitch()", 4000);
	$('#slideshow').on('click', function() {
		window.location = '/create'
	});
});
