
function paypal_checkout(element)
{
	
	$.post("/cart_items", {},
    	function(data) {
    		cart_items = JSON.parse(data);
			console.log(cart_items);
			
		    var paypalForm = document.createElement("form");
		    paypalForm.setAttribute("action","https://www.paypal.com/cgi-bin/webscr");
		    paypalForm.setAttribute("method","post");
		    var elem = document.createElement("input");
		    elem.setAttribute("type","hidden");
		    elem.setAttribute("name","cmd");
		    elem.setAttribute("value","_cart");
		    paypalForm.appendChild(elem);

		    elem = document.createElement("input");
		    elem.setAttribute("type","hidden");
		    elem.setAttribute("name","upload");
		    elem.setAttribute("value",1);
		    paypalForm.appendChild(elem);

		    elem = document.createElement("input");
		    elem.setAttribute("type","hidden");
		    elem.setAttribute("name","business");
		    elem.setAttribute("value","seller@dezignerfotos.com");
		    paypalForm.appendChild(elem);

		    elem = document.createElement("input");
		    elem.setAttribute("type","submit");
		    elem.setAttribute("value","PayPal");
		    paypalForm.appendChild(elem);

				var newElem = document.createElement("input");
				newElem.setAttribute("type","hidden");
				newElem.setAttribute("name","cancel_return");
				newElem.setAttribute("value",document.baseURI);
				paypalForm.appendChild(newElem);


            for (var i = 0 ; i < cart_items.items.length ; i++)
            {
            	item = cart_items.items[i];
				var newElem0 = document.createElement("input");
				newElem0.setAttribute("type","hidden");
				newElem0.setAttribute("name","item_name_"+(i+1));
				newElem0.setAttribute("value",item.product_name);
				paypalForm.appendChild(newElem0);
	
				var newElem1 = document.createElement("input");
				newElem1.setAttribute("type","hidden");
				newElem1.setAttribute("name","amount_"+(i+1));
				newElem1.setAttribute("value",item.product_price_per_item);
				paypalForm.appendChild(newElem1);
	
				var newElem2 = document.createElement("input");
				newElem2.setAttribute("type","hidden");
				newElem2.setAttribute("name","shipping_"+(i+1));
				newElem2.setAttribute("value",1);
				paypalForm.appendChild(newElem2);
	
				var newElem3 = document.createElement("input");
				newElem3.setAttribute("type","hidden");
				newElem3.setAttribute("name","quantity_"+(i+1));
				newElem3.setAttribute("value",item.quantity);
				paypalForm.appendChild(newElem3);
            	
            }

			paypalForm.submit();
    	}
    	
    	
	);
	
	return false;

}

