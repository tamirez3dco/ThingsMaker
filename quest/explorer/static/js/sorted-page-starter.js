
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
			one_tab.style.backgroundColor="silver";
		}
		else
		{
			one_tab.style.backgroundColor="white";
			
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
	var res = urlStr.replace(/%22/g,'"');
	res = res.replace(/%7B/g,'{');
	res = res.replace(/%7D/g,'}');
	return res;
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
	
	getProductsURL = window.location.origin+"/get_ssp/"+jsonstr;
	getProductList(getProductsURL, '#sorted-products');
}

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
		initImages();
	}
});


