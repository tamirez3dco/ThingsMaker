var galleries;
var step = 0;
var myInterval;
var waitImages = false;
$(document).ready(function() {
	var slug = ((this.URL.split('product/')[1]).split('#'))[0];
	console.log("slllug "+ slug)
	waitImages = (this.URL.indexOf("waitImages") != -1);
	if(waitImages) {
		console.log("waitImages");
		waitForImages();
		myInterval = setInterval(chooseRenderImage2, 500);
	} else {
		console.log("Dont waitImages");
		dontWaitImages();
	}
	getProductList('/get_ssp/%7B"limits":"0-5","screener":"'+ slug +'","sorter":"stock_amount"%7D', '.popular-variants');
});
function waitImage(imgsrc, imageId, imageTitle) {
	var img = new Image();

	img.onerror = function(evt) {
		console.log(this.src + " can't be loaded.");
		setTimeout(waitImage(imgsrc, imageId, imageTitle), 3000);
	}
	img.onload = function(evt) {
		console.log(this.src + " is loaded.");
		galleries[0].tamir_addImage(imgsrc, imageId, imageTitle);
	}
	img.src = imgsrc;
}

function chooseRenderImage2() {
	for(var i = 0; i < this.galleries[0].images.length; i++) {
		if(galleries[0].images[i].image.indexOf("Render") != -1) {
			console.log("i=" + i);
			if(step == 0) {
				galleries[0].removeImage(0);
				step++;
			} else if(step == 1) {
				galleries[0].in_transition = false;
				galleries[0].current_index = -1;
				galleries[0].showImage(i, undefined);
				clearInterval(myInterval);
			}
			return;
		}
	}
}

function waitForImages() {
	var tamir_element = document.getElementById('tamir-label');
	var urlTop = tamir_element.getAttribute("urlTop");
	var urlFront = tamir_element.getAttribute("urlFront");
	var urlRender = tamir_element.getAttribute("urlRender");
	var urlSmall = tamir_element.getAttribute("urlSmall");
	var statics = tamir_element.getAttribute("statics");

	console.log("Top=" + urlTop);
	console.log("Front=" + urlFront);
	console.log("Render=" + urlRender);
	galleries = $('.ad-gallery').adGallery({
		'loader_image' : statics + "adgalery/loader.gif"
	});
	galleries[0].settings.description_wrapper = $('#descriptions');
	/*
	 galleries[0].tamir_addImage(urlSmall, "Small_ID", "Small Title");
	 galleries[0].tamir_addImage(urlRender, "Render_ID", "Render Title");
	 galleries[0].tamir_addImage(urlTop, "Top_ID", "Top Title");
	 galleries[0].tamir_addImage(urlFront, "Front_ID", "Front Title");
	 */
	waitImage(urlRender, "RenderID", "Render Title");
	waitImage(urlTop, "TopID", "Top Title");
	waitImage(urlFront, "FrontID", "Front Title");

	console.log(galleries[0].images);
}

function dontWaitImages() {
	var tamir_element = document.getElementById('tamir-label');
	var urlTop = tamir_element.getAttribute("urlTop");
	var urlFront = tamir_element.getAttribute("urlFront");
	var urlRender = tamir_element.getAttribute("urlRender");
	var statics = tamir_element.getAttribute("statics");
	galleries = $('.ad-gallery').adGallery({
		'loader_image' : statics + "adgalery/loader.gif"
	});
	galleries[0].settings.description_wrapper = $('#descriptions');
	galleries[0].removeAllImages();
	//galleries[0].tamir_addImage(urlRender, "Render_ID", "Render Title");
	galleries[0].tamir_addImage(urlTop, "Top_ID", "Top Title");
	galleries[0].tamir_addImage(urlFront, "Front_ID", "Front Title");
	galleries[0].tamir_addImage(urlRender, "Render_ID", "Render Title");
	galleries[0].in_transition = false;
	galleries[0].showImage(2, undefined);
	//galleries[0].removeImage(0);
	console.log(galleries[0].images);
}