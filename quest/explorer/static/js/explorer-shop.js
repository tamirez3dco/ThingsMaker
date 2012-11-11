function create_product_html(product)
{
	var likeClass = "home-product-like empty";
	if(product.lovers > 0) {
		likeClass = "home-product-like";
	}

	var product_name = product.name;
	if (product_name.length > 15) {
		product_name = product_name.substring(0,13) + '..';
	}
	var addClass = 'home-product';
	var	html = '<div class="'+ addClass +'"><a class="home-product-pointer" href="' + product.product_url + '">'+
			   '<img class="home-product-mainImage" src="' + product.image_url + '" />'+
			   '<p class="home-product-name">'+ product_name +'</p>' +
			   '<p class="home-product-price">$'+ product.price.toFixed(2) + '</p></a>' +
			   '<div class="home-product-hover">'+
			   '<div class="'+ likeClass +'" slug="' + product.slug + '" onclick="return hart_clicked(this)" alt="loveme"><span>' + product.lovers +'</span></div>'+
			   '<div class="home-product-customize"><a href="/create?start_product='+ product.slug + '&material=' + product.material + '&textParam=' + product.text + '&product_type=variant">Customize</a></div>'+
			   '</div>'+
			   + '</div>';	
	return html;
}
function hart_clicked(element)
{
	// first increase the number in element
	var currentNum = parseInt(element.innerText);
	currentNum += 1;
	element.innerHTML = "<span>"+currentNum +"<\span>";
	$(element).removeClass('empty');
	console.log($(element).parent());
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
		var productList = $('<div class="home-product-list"></div>').appendTo(element);
		for(var i = 0; i < data.products.length; i++) {
			var html = create_product_html(data.products[i]);
			$(html, {}).appendTo(productList);
		}
	});	
}

function TMLoadMore(jsonobj, begin, end, el)
{
	jsonobj['limits'] = begin + '-' + end;
	var jsonstr = JSON.stringify(jsonobj);
	getProductsURL = "/get_ssp/"+jsonstr;
	getProductList(getProductsURL, el);
}