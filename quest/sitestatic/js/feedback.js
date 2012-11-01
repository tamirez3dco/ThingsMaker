$(function(){
	$('#feedback').contactable({
		subject: 'feedback URL:'+location.href,
		url: '/feedback',
		center: false
	});
});