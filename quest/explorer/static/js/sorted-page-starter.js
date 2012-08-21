
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
	
	var mainElem = document.getElementById("sorted-products");
	
	if ( mainElem.hasChildNodes() )
	{
    	while ( mainElem.childNodes.length >= 1 )
    	{
        	mainElem.removeChild( mainElem.firstChild );       
    	}	 
	}
	
	var strs = window.location.href.split("products_sorted/");
	
	strs[1] = strs[1].replace(/%22/g,'"');
	strs[1] = strs[1].replace(/%7B/g,'{');
	strs[1] = strs[1].replace(/%7D/g,'}');
	var jsonobj = JSON.parse(strs[1]);
	jsonobj["sorter"] = sorterName;
	var jsonstr = JSON.stringify(jsonobj);
	
	getProductsURL = window.location.origin+"/get_ssp/"+jsonstr;
	getProductList(getProductsURL, '#sorted-products');
	
	return false;
}



$(function() {
	var elems = document.getElementsByName("one_small_tab");
	var screenerName = "";
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
});


