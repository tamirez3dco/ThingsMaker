var TMInterval = 20;
var TMlast = 30;
var TMCanLoad=true;
function runAnimation(){
	$('#banner-bg').css('display', 'block');
	$('#iml1').css('display', 'block');
	$('#imc1').css('display', 'block');
	$('#imr1').css('display', 'block');
	$('#hpbutton').css('display', 'block');
	
	var delayCounter = 0;
	//$("#im1").animate({opacity: 0}, 10000);
	
	//Left
	/////
	var pause=2000;
	var duration=3000;
	delayCounter+=pause;
	setTimeout(function() {
		$("#iml1").animate({opacity: 0}, 3000);
	} , 2000);
	
	setTimeout(function() {
		$('#iml2').css('opacity', 0);
		$('#iml2').css('display', 'block');
		$("#iml2").animate({opacity: 1}, 3000)
	} , 2000);
	
	//delayCounter+=duration;	
	
	//////
	pause=0;
	duration=3000;
	delayCounter+=pause;
	setTimeout(function() {
		//$('#iml2').css('display', 'none');
		$("#iml2").animate({opacity: 0}, 3000);
	} , 5000);
	
	
	setTimeout(function() {
		$('#iml3').css('opacity', 0);
		$('#iml3').css('display', 'block');
		$("#iml3").animate({opacity: 1}, 3000);
	} , 5000);
	

	setTimeout(function() {
		$('#iml4').css('display', 'block');
		$('#iml3').css('display', 'none');
	} , 8000);
	setTimeout(function() {
		$('#iml5').css('display', 'block');
		$('#iml4').css('display', 'none');
	} , 8600);
	setTimeout(function() {
		$('#iml6').css('display', 'block');
		$('#iml5').css('display', 'none');
	} , 9200);
	setTimeout(function() {
		$('#iml7').css('display', 'block');
		$('#iml6').css('display', 'none');
	} , 9800);
	setTimeout(function() {
		$('#iml8').css('display', 'block');
		$('#iml7').css('display', 'none');
	} , 10400);
		

	//Center
	setTimeout(function() {
		$("#imc1").animate({opacity: 0}, 5000);
	} , 3000);
	
	setTimeout(function() {
		$('#imc2').css('opacity', 0);
		$('#imc2').css('display', 'block');
		$("#imc2").animate({opacity: 1}, 5000)
	} , 3000);
		

	//Right
	setTimeout(function() {
		$("#imr1").animate({opacity: 0}, 5000);
	} , 500);
	
	setTimeout(function() {
		$('#imr2').css('opacity', 0);
		$('#imr2').css('display', 'block');
		$("#imr2").animate({opacity: 1}, 5000)
	} , 500);	
	
}
$(function() {
	/*$('#slideshow').cycle({ 
	    fx:    'fade', 
	    timeout:  1000,  
	    speed: 3000,
	    continous: 1
 	});*/
 	runAnimation();
	jsonobj = {"limits":"0-10","sorter":"stock_amount"};
		TMLoadMore(jsonobj,0, 15,'#top-inspirations');
		setTimeout(function(){TMLoadMore(jsonobj,15, 30,'#top-inspirations');}, 1000);
		$(document).scroll(function(){
			//console.log('scroll');
			if (TMlast>500) return;
			if($(window).scrollTop()+$(window).height()>=$(document).height()-350) {
				if(TMCanLoad==false) return;
				TMCanLoad=false;
				TMLoadMore(jsonobj,TMlast, TMlast+TMInterval, '#top-inspirations');
				TMlast = TMlast+TMInterval;
				//console.log('load!!!');
			}
			
		});
});
