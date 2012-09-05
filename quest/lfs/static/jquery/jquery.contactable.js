/*
 * contactable 1.2.1 - jQuery Ajax contact form
 *
 * Copyright (c) 2009 Philip Beel (http://www.theodin.co.uk/)
 * Dual licensed under the MIT (http://www.opensource.org/licenses/mit-license.php) 
 * and GPL (http://www.opensource.org/licenses/gpl-license.php) licenses.
 *
 * Revision: $Id: jquery.contactable.js 2010-01-18 $
 *
 */
 
//extend the plugin
(function($){

	//define the new for the plugin ans how to call it	
	$.fn.contactable = function(options) {
		//set default options  
		var defaults = {
			url: 'http://YourServerHere.com/contactable/mail.php',
			name: 'Name',
			email: 'Email',
			message : 'Message',
			subject : 'A contactable message',
			submit : 'SEND',
			recievedMsg : 'Thank you for your message',
			notRecievedMsg : 'Sorry but your message could not be sent, try again later',
			disclaimer: 'Please feel free to get in touch, we value your feedback',
			hideOnSubmit: false,
			center: false
		};

		//call in the default otions
		var options = $.extend(defaults, options);
		//act upon the element that is passed into the design 
		if(options.center) {
			$(this).addClass('center');
		}
		$(this).addClass('contactable');
		return this.each(function() {
			//construct the form
			var this_id_prefix = '#'+this.id+' ';
			$(this).html('<div class="contactable-inner"></div><form class="contactable-form" method="" action="">'+
			             '<div class="contactable-loading"></div><div class="contactable-callback">'+
			             '</div><div class="contactable-holder"><p><label for="name">'+options.name+
			             '<span class="contactable-red"> * </span></label><br />'+
			             '<input class="contactable-name" name="name"/>'+
			             '</p><p><label for="email">'+options.email+
			             '<span class="contactable-red"> * </span></label><br />'+
			             '<input class="contactable-email" name="email" /></p><p><label for="message">'+options.message+
			             '<span class="contactable-red"> * </span></label><br />'+
			             '<textarea name="message" class="contactable-message" rows="4" cols="30" ></textarea></p>'+
			             '<p><input class="submit" type="submit" value="'+options.submit+
			             '"/></p><p class="disclaimer">'+options.disclaimer+'</p></div></form>');
			             
			//show / hide function
			$(this_id_prefix+'div.contactable-inner').toggle(function() {
				$(this).animate({"marginLeft": "-=5px"}, "fast"); 
				$(this_id_prefix+'.contactable-form').animate({"marginLeft": "-=0px"}, "fast");
				$(this).animate({"marginLeft": "+=387px"}, "slow"); 
				$(this_id_prefix+'.contactable-form').animate({"marginLeft": "+=390px"}, "slow"); 
			}, 
			function() {
				$(this_id_prefix+'.contactable-form').animate({"marginLeft": "-=390px"}, "slow");
				$(this).animate({"marginLeft": "-=387px"}, "slow").animate({"marginLeft": "+=5px"}, "fast"); 
			});
			
			//validate the form 
			$(this_id_prefix+".contactable-form").validate({
				//set the rules for the fild names
				rules: {
					name: {
						required: true,
						minlength: 2
					},
					email: {
						required: true,
						email: true
					},
					message: {
						required: true
					}
				},
				//set messages to appear inline
					messages: {
						name: "",
						email: "",
						message: ""
					},			

				submitHandler: function() {
					$(this_id_prefix+'.contactable-holder').hide();
					$(this_id_prefix+'.contactable-loading').show();
$.ajax({
  type: 'POST',
  url: options.url,
  data: {subject:options.subject, name:$(this_id_prefix+'.contactable-name').val(), email:$(this_id_prefix+'.contactable-email').val(), message:$(this_id_prefix+'.contactable-message').val()},
  success: function(data){
						$(this_id_prefix+'.contactable-loading').css({display:'none'}); 
						if( data == 'success') {
							$(this_id_prefix+'.contactable-callback').show().append(options.recievedMsg);
							if(options.hideOnSubmit == true) {
								//hide the tab after successful submition if requested
								$(this_id_prefix+'.contactable-form').animate({dummy:1}, 2000).animate({"marginLeft": "-=450px"}, "slow");
								$(this_id_prefix+'div.contactable-inner').animate({dummy:1}, 2000).animate({"marginLeft": "-=447px"}, "slow").animate({"marginLeft": "+=5px"}, "fast"); 
							}
						} else {
							$(this_id_prefix+'.contactable-callback').show().append(options.notRecievedMsg);
							setTimeout(function(){
								$(this_id_prefix+'.contactable-holder').show();
								$(this_id_prefix+'.contactable-callback').hide().html('');
							},2000);
						}
					},
  error:function(){
						$(this_id_prefix+'.contactable-loading').css({display:'none'}); 
						$(this_id_prefix+'.contactable-callback').show().append(options.notRecievedMsg);
                                        }
});		
				}
			});
		});
	};
 
})(jQuery);
