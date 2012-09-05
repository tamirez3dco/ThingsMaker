$(function(){
	$('#contact').contactable({
		subject: 'feedback URL:'+location.href,
		url: '/feedback',
		center: true
	});
	$('#contact-link').click(function(){
		$('#contact .contactable-form').css({display:'block'});
	});
});