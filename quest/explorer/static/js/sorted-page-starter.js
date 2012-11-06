
function tab_clicked(element)
{
	var elems = document.getElementsByName("one_small_tab");
	var screenerName = "";
	for (var i = 0 ; i < elems.length ; i++)
	{
		var one_tab = elems[i];
		if (one_tab == element)
		{
			sorterName = one_tab.getAttribute("sorterName");
			$(one_tab).addClass('selected');
		}
		else
		{
			//one_tab.style.backgroundColor="white";
			$(one_tab).removeClass('selected');
			
		}
	}
	removeAllImages();
	
	initImages(sorterName);
	return false;
}

function removeAllImages()
{
	var mainElem = document.getElementById("sorted-products");
	
	if ( mainElem.hasChildNodes() )
	{
    	while ( mainElem.childNodes.length >= 1 )
    	{
        	mainElem.removeChild( mainElem.firstChild );       
    	}	 
	}
	
}
function getJSONableStringFromURLString(urlStr)
{
	return decodeURIComponent(urlStr);
}

function initImages(sorterName)
{
	var strs = window.location.href.split("sorted_products/");
	var urlStr = strs[1];
	var jsonobj = JSON.parse(getJSONableStringFromURLString(urlStr));
	if (sorterName != undefined) 
	{
		jsonobj["sorter"] = sorterName;
	}
	var jsonstr = JSON.stringify(jsonobj);
	
	getProductsURL = "/get_ssp/"+jsonstr;
	getProductList(getProductsURL, '#sorted-products');
}

function TMgetJsonObj(sorterName)
{
	var strs = window.location.href.split("sorted_products/");
	var urlStr = strs[1];
	var jsonobj = JSON.parse(getJSONableStringFromURLString(urlStr));
	if (sorterName != undefined) 
	{
		jsonobj["sorter"] = sorterName;
	}
	console.log(jsonobj);
	return jsonobj;
}

function TMLoadMore(jsonobj, begin, end)
{
	jsonobj['limits'] = begin + '-' + end;
	var jsonstr = JSON.stringify(jsonobj);
	getProductsURL = "/get_ssp/"+jsonstr;
	getProductList(getProductsURL, '#sorted-products');
}
var TMInterval = 20;
var TMlast = 30;
$(function() {
	var screenerExists = document.URL.indexOf("screener") > 0;
	if (screenerExists)
	{
		var elems = document.getElementsByName("one_small_tab");
		for (var i = 0 ; i < elems.length ; i++)
		{
			var one_tab = elems[i];
			var sorterName = one_tab.getAttribute("sorterName");
			if (window.location.href.indexOf(sorterName) > 0)
			{
				tab_clicked(one_tab);
				return;
			}
		}
	}
	else
	{
		var child = document.getElementById("small_tabs");
		child.parentNode.removeChild(child);
		//initImages();
		var jsonobj = TMgetJsonObj();
		TMLoadMore(jsonobj,0, 10);
		setTimeout(function(){TMLoadMore(jsonobj,0, 20);}, 1000);
		$(document).scroll(function(){
			console.log('scroll');
			if($(window).scrollTop()+$(window).height()>=$(document).height()-200) {
				TMLoadMore(jsonobj,TMlast, TMlast+TMInterval);
				TMlast = TMlast+TMInterval;
				console.log('load!!!');
			}
			
		});
	}
});


