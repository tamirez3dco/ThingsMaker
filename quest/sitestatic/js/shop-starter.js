var TMInterval = 20;
var TMlast = 30;
var TMCanLoad=true;
function runTransition(start, duration, el1, el2){
	duration = duration*1000;
	start = start*1000;
	setTimeout(function() {
		$(el1).animate({opacity: 0}, duration);
	} , start);
	
	setTimeout(function() {
		$(el2).css('opacity', 0);
		$(el2).css('display', 'block');
		$(el2).animate({opacity: 1}, duration)
	} , start);	
}

function runSequence(imList, start, durations){
	for(var i=0; i<(imList.length-1); i++){
		runTransition(start, durations[i], imList[i], imList[i+1]);
		start=start+durations[i];
	}
}

function fastTransition(el1, el2, start){
	start = start*1000;
	setTimeout(function() {
		$(el2).css('display', 'block');
		$(el1).css('display', 'none');
	} , start);
}
function runRingAnimation(start) {
	runSequence(['#ph','#im-r-l2', '#im-r-l3', '#im-r-l1'], start, [3,3,3]);
	runSequence(['#ph','#im-r-r2', '#im-r-r3', '#im-r-r1'], start, [3,3,3]);
}

function runPhoneAnimation(start) {
	runSequence(['#im-p-l1', '#im-p-l2', '#im-p-l4', '#im-p-l3'], start+2, [2,2,2]);
	runSequence(['#im-p-c1', '#im-p-c2', '#im-p-c1'], start+2, [6,6]);
	runSequence(['#im-p-r1', '#im-p-r2', '#im-p-r1'], start+2, [6,6]);
	
	fastTransition('#im-p-l3', '#im-p-l5', start+8);
	fastTransition('#im-p-l5', '#im-p-l6', start+8.8);
	fastTransition('#im-p-l6', '#im-p-l7', start+9.6);
	fastTransition('#im-p-l7', '#im-p-l8', start+10.4);
}
function runAnimation(){
	$('#banner-bg').css('display', 'block');
	$('#hpbutton').css('display', 'block');
	$('#hppreview').css('display', 'block');
	runRingAnimation(0);
	runTransition(10, 3, '#im-r-l1', '#im-p-l1');
	runTransition(10, 3, '#im-r-c1', '#im-p-c1');
	runTransition(10, 3, '#im-r-r1', '#im-p-r1');
	runPhoneAnimation(12);	
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
