$.extend({
	getUrlVars : function() {
		var vars = [], hash;
		//var base = $.address.queryString();
		var base = $.address.baseURL();
		console.log(base);
		var hashes = base.slice(base.indexOf('?') + 1).split('&');
		for(var i = 0; i < hashes.length; i++) {
			hash = hashes[i].split('=');
			vars.push(hash[0]);
			vars[hash[0]] = hash[1];
		}
		return vars;
	},
	getUrlVar : function(name) {
		return $.getUrlVars()[name];
	}
});
$.fn.exists = function() {
	return this.length !== 0;
}( function($) {
	/**
	 * @class The jWizard object will be fed into $.widget()
	 */
	$.widget("db.jWizard", {
		/**
		 * @private
		 * @property int _stepIndex Represents the index of the current active/visible step
		 */
		_stepIndex : 0,

		/**
		 * @private
		 * @property int _stepCount Represents the `functional` number of steps
		 */
		_stepCount : 0,

		/**
		 * @private
		 * @property int _actualCount Represents the `actual` number of steps
		 */
		_actualCount : 0,

		_exploreURL : '/explore',
		_itemId : null,
		_startProduct : null,
		_productType : null,
		_stepAfterLast : 0,
		_material : null,
		_firstStep : true,
		/**
		 * @description Initializes jWizard
		 * @return void
		 */
		_create : function() {
			this._startProduct = $.getUrlVar('start_product');
			this._productType = $.getUrlVar('product_type');
			this._userText = $.getUrlVar('textParam');
			this._material = $.getUrlVar('material');
			this._buildSteps();
			this._buildTitle();
			this._buildDialog();
			this._buildMakeitDialog();

			if(this.options.menuEnable) {
				//this._buildMenu();
				//this._buildTopMenu();
				this._buildTriangleButtons();
				this._buildTopMenu();
			}

			this._buildButtons();

			if(this.options.counter.enable) {
				this._buildCounter();
			}

			this.element.addClass("ui-widget jw-widget");

			this.element.find(".ui-state-default").live("mouseover mouseout", function(event) {
				if(event.type === "mouseover") {
					$(this).addClass("ui-state-hover");
				} else {
					$(this).removeClass("ui-state-hover");
				}
			});
			this._initAddress();
			//this._changeStep(this._stepIndex, true);
		},
		/**
		 * @private
		 * @description Additional processing before destroying the widget.
		 *    Will eventually be used to restore everything to it's pre-widget state.
		 * @return void
		 */
		destroy : function() {
			this._destroySteps();
			this._destroyTitle();

			if(this.options.menuEnable) {
				this._destroyMenu();
			}

			this._destroyButtons();

			if(this.options.counter.enable) {
				this._destroyCounter();
			}

			this.element.removeClass("ui-widget");
			this.element.find(".ui-state-default").unbind("mouseover").unbind("mouseout");

			$.Widget.prototype.destroy.call(this);
		},
		/**
		 * @public
		 * @description Disables the wizard (mainly the buttons)
		 */
		disable : function() {
			this.element.addClass("ui-state-disabled").find("button").attr("disabled", "disabled");
		},
		/**
		 * @public
		 * @description Disables the wizard (mainly the buttons)
		 */
		enable : function() {
			this.element.removeClass("ui-state-disabled").find("button").removeAttr("disabled");
		},
		/**
		 * @private
		 * @description Can set options within the widget programmatically
		 * @return void
		 */
		_setOption : function(key, value) {
			var keys = key.split('.');

			if(keys.length > 1) {
				switch (keys[0]) {
					case "buttons":
						this.options[keys[0]][keys[1]] = value;

						switch (keys[1]) {
							case "jqueryui":
								this.options[keys[0]][keys[1]][keys[2]] = value;
								if(keys[2] === "enable") {
									if(value) {
										this.find(".jw-buttons > button").button("destroy");
									} else {
										this._destroyButtons();
										this._buildButtons();
									}
									break;
								}
								break;
							case "cancelHide":
								this.element.find(".jw-button-cancel")[value ? "addClass" : "removeClass"]("ui-helper-hidden");
								break;
							case "cancelType":
								this.element.find(".jw-button-cancel").attr("type", value);
								break;
							case "finishType":
								this.element.find(".jw-button-finish").attr("type", value);
								break;
							case "cancelText":
								this.element.find(".jw-button-cancel").text(value);
								break;
							case "previousText":
								this.element.find(".jw-button-previous").text(value);
								break;
							case "nextText":
								this.element.find(".jw-button-next").text(value);
								break;
							case "finishText":
								this.element.find(".jw-button-finish").text(value);
								break;
						}
						break;

					case "counter":
						this.options[keys[0]][keys[1]] = value;

						switch (keys[1]) {
							case "enable":
								if(value) {
									this._buildCounter();
									this._updateCounter();
								} else {
									this._destroyCounter();
								}
								break;
							case "type":
							case "progressbar":
							case "location":
								if(this.options.counter.enable) {
									this._destroyCounter();
									this._buildCounter();
									this._updateCounter();
								}
								break;
							case "startCount":
							case "startHide":
							case "finishCount":
							case "finishHide":
							case "appendText":
							case "orientText":
								if(this.options.counter.enable) {
									this._updateCounter();
								}
								break;
						}
						break;

					case "effects":
						if(keys.length === 2) {
							this.options[keys[0]][keys[1]] = value;
						} else {
							this.options[keys[0]][keys[1]][keys[2]] = value;
						}
						break;
				}
			} else {
				this.options[keys[0]] = value;

				switch (keys[0]) {
					case "titleHide":
						this.element.find(".jw-header")[value ? "addClass" : "removeClass"]("ui-helper-hidden");
						break;

					case "menuEnable":
						if(value) {
							this._buildMenu();
							this._updateMenu();
						} else {
							this._destroyMenu();
						}
						break;

					case "counter":
						this._destroyCounter();
						this._buildCounter();
						this._updateCounter();
						break;
				}
			}
		},
		/**
		 * @description Jumps to the first step in the wizard's step collection
		 * @return void
		 */
		firstStep : function() {
			this.changeStep(0, "first");
		},
		/**
		 * @description Jumps to the last step in the wizard's step collection
		 * @return void
		 */
		lastStep : function() {
			this.changeStep(this._stepCount - 1, "last");
		},
		/**
		 * @description Jumps to the next step in the wizard's step collection
		 * @return void
		 */
		nextStep : function() {
			var $steps = this.element.find(".jw-step");
			if(this._stepIndex == $steps.length - 1) {
				this._onLastStep();
				return;
			}
			var options = {
				wizard : this.element,
				currentStepIndex : this._stepIndex,
				nextStepIndex : this._stepIndex + 1,
				delta : 1
			};

			if(this._trigger("next", null, options) !== false) {
				this.changeStep(this._stepIndex + 1, "next");
			}
		},
		/**
		 * @description Jumps to the previous step in the wizard's step collection
		 * @return void
		 */
		previousStep : function() {
			var options = {
				wizard : this.element,
				currentStepIndex : this._stepIndex,
				nextStepIndex : this._stepIndex - 1,
				delta : -1
			};

			if(this._trigger("previous", null, options) !== false) {
				this.changeStep(this._stepIndex - 1, "previous");
			}
		},
		/**
		 * @description Goes to an arbitrary `step` in the collection based on input
		 * @return void
		 */
		changeStep : function(nextStep, type) {
			type = type || "manual";
			nextStep = typeof nextStep === "number" ? nextStep : $(nextStep).index();
			var options = {
				wizard : this.element,
				currentStepIndex : this._stepIndex,
				nextStepIndex : nextStep,
				delta : nextStep - this._stepIndex,
				type : type
			};

			if(this._trigger("changestep", null, options) !== false) {
				this._changeStep(nextStep);
			}
		},
		/**
		 * @private
		 * @description Internal wrapper for performing animations
		 * @return void
		 */
		_effect : function($element, action, subset, type, callback) {
			var wizard = this, opt = this.options.effects[action][subset];
			type = type || "effect";

			if(!$element.length || !$element.hasClass("jw-animated")) {
				$element[type]();

				if(callback) {
					callback.call(this);
				}

				return false;
			}

			opt.callback = callback || $.noop;

			$element[type](opt.type, opt.options, opt.duration, opt.callback);
		},
		/**
		 * @private
		 * @description Internal wrapper for logging (and potentially debugging)
		 * @return void
		 */
		_log : function() {
			if(this.options.debug && window.console) {
				console.log[console.firebug ? "apply" : "call"](console, Array.prototype.slice.call(arguments));
			}
		},
		_updateNavigation : function(firstStep) {
			this._updateButtons();
			if(this.options.menuEnable) {
				//this._updateMenu(firstStep);
				this._updateTopMenu(firstStep);
			}
			if(this.options.counter.enable) {
				this._updateCounter(firstStep);
			}
		},
		/**
		 * @private
		 * @description Generates the header/title
		 * @return void
		 */
		_buildTitle : function() {
			this.element.prepend($("<div />", {
				"class" : "jw-header ui-widget-header ui-corner-top" + (this.options.hideTitle ? " ui-helper-hidden" : ""),
				html : '<h2 class="jw-title' + ((this.options.effects.enable || this.options.effects.title.enable) ? " jw-animated" : "") + '" />'
			}));
		},
		/**
		 * @private
		 * @description Updates the title
		 * @return void
		 */
		_updateTitle : function(firstStep) {
			var wizard = this, $title = this.element.find(".jw-title"), $currentStep = this.element.find(".jw-step:eq(" + this._stepIndex + ")");

			if(!firstStep) {
				this._effect($title, "title", "hide", "hide", function() {
					$title.text($currentStep.attr("title"));
					wizard._effect($title, "title", "show", "show");
				});
			} else {
				$title.text($currentStep.attr("title"));
			}
		},
		/**
		 * @private
		 * @description Destroys the title element (used in `destroy()`)
		 * @return void
		 */
		_destroyTitle : function() {
			$(".jw-header").remove();
		},
		/**
		 * @private
		 * @description Initializes the step collection.
		 *    Any direct children <div> (with a title attr) or <fieldset> (with a <legend>) are considered steps, and there should be no other sibling elements.
		 *    All steps without a specified `id` attribute are assigned one based on their index in the collection.
		 *    Lastly, a <div> is wrapped around all the steps to isolate them from the rest of the widget.
		 * @return void
		 */
		_buildSteps : function() {
			var $steps = this.element.children("div, fieldset");
			var afterLast = 0;
			var wizard = this;
			$steps.each(function(index, element) {
				var param = element.id.replace('create-param-', '');
				if(param == 'text') {
					afterLast = 1;
					if(wizard._userText != null) {
						$(element).find("#create-param-text-input").val(wizard._userText);
					}
				}
				var paramIndex = parseInt(param, 10);
				if(isNaN(paramIndex)) {
					$(element).data('paramType', param);
				} else {
					$(element).data('paramType', 'model');
					$(element).data('paramIndex', paramIndex);
				}
			});
			this._stepAfterLast = afterLast;
			this._stepCount = $steps.length;

			$steps.addClass("jw-step").each(function(x) {
				var $step = $(this);

				if(this.tagName.toLowerCase() === "fieldset") {
					$step.attr("title", $step.find("legend").text());
				}
			});
			if(this.options.effects.enable || this.options.effects.step.enable) {
				$steps.addClass("jw-animated");
			}

			$steps.hide().wrapAll($("<div />", {
				"class" : "jw-content ui-widget-content ui-helper-clearfix",
				html : '<div class="jw-steps-wrap" />'
			})).eq(this._stepIndex).show();
		},
		/**
		 * @private
		 * @description Destroys the step wrappers and restores the steps to their original state (used in `destroy()`)
		 * @return void
		 */
		_destroySteps : function() {
			$(".jw-step").show().unwrap().unwrap();
			// Unwrap 2x: .jw-steps-wrap + .jw-content
			$(".jw-step").unbind("show").unbind("hide").removeClass("jw-step");
		},
		/**
		 * @private
		 * @description Changes the "active" step.
		 * @param number|jQuery nextStep Either an index or a jQuery object/element
		 * @param bool isInit Behavior needs to change if this is called during _init (as opposed to manually through the global setter)
		 * @return void
		 */
		_changeStep : function(nextStep, firstStep) {
			if (this._firstStep == true) {
				firstStep = true;
				this._firstStep = false;
			} else {
				firstStep = false;
			}
			var reloadStep = false;
			if(nextStep == this._stepIndex) {
				reloadStep = true;
			}
			var wizard = this, $steps = this.element.find(".jw-step"), $currentStep = $steps.eq(this._stepIndex);

			if($('#create-param-text-input').length) {
				this._userText = $('#create-param-text-input').val();
			}

			if( typeof nextStep === "number") {
				if(nextStep < 0 || nextStep > ($steps.length - 1)) {
					alert("Index " + nextStep + " Out of Range");
					return false;
				}
				nextStep = $steps.eq(nextStep);
			} else if( typeof nextStep === "object") {
				if(!nextStep.is($steps.selector)) {
					alert("Supplied Element is NOT one of the Wizard Steps");
					return false;
				}
			}
			clearInterval(this._showImagesTask);
			if(!firstStep) {
				this._disableButtons();
				this._stepIndex = $steps.index(nextStep);
				this._updateTitle(firstStep);

				if((nextStep.data('paramType') != 'text') && (!reloadStep)) {
					nextStep.children(".create-image-container").html('');
					//wizard._loadImages(nextStep, this._stepIndex);
				}
				if(nextStep.data('paramType') != 'text') {
					wizard._loadImages(nextStep, this._stepIndex, false);
				}
				$currentStep.animate({
					opacity : 0.0
				}, 2000, 'linear', function() {
					wizard._setAddress();
					$currentStep.hide();
					
					if(($currentStep.data('paramType') != 'text')) {
						$currentStep.children(".create-image-container").html('');
					}
					wizard._addImagesToStep(nextStep, wizard._stepIndex);
					nextStep.css({
						opacity : 1.0
					}).show();
					
					wizard._showImages();
					wizard._enableButtons();
					wizard._updateNavigation(firstStep);
					
				});
			} else {
				this._stepIndex = $steps.index(nextStep);
				//this._setAddress();
				this._updateTitle(firstStep);
				this._updateNavigation(firstStep);
				if(nextStep.data('paramType') != 'text') {
					if (!reloadStep) $currentStep.hide();
					wizard._loadImages(nextStep, this._stepIndex, true);
					//wizard._addImagesToStep(nextStep, wizard._stepIndex);
					nextStep.css({
						opacity : 1.0
					}).show();
					wizard._showImages();
				}
			}
		},
		_waitImage : function(imgsrc, imageId, imageTitle, count) {
			var img = new Image();
			var self = this;
			img.onerror = function(evt) {
				if(count < 100) {
					setTimeout(self._waitImage(imgsrc, imageId, imageTitle, count + 1), 300);
				}
			}
			img.onload = function(evt) {
				$("#explorer-image-" + imageId).prepend(img);
				$("#explorer-image-" + imageId).data('loaded', true);
			}
			img.src = imgsrc;
		},
		_showImages : function() {
			var wizard = this;
			//wizard._showNextImage = true;
			wizard._showImagesTask = setInterval(function() {
				if(wizard._showNextImage != true)
					return;
				var done = 0;
				$('.explorer-image').each(function(index, element) {
					if(($(element).data('visible') == true) || ($(element).data('aborted') == true)) {
						done++;
					}
					if(($(element).data('loaded') == true) && ($(element).data('visible') != true)) {
						wizard._showNextImage = false;
						$(element).data('visible', true);
						$(element).css({
							opacity : 0.0,
							visibility : "visible"
						}).animate({
							opacity : 1.0
						}, 700, 'linear');
						setTimeout(function() {
							wizard._showNextImage = true;
						}, 350);
						return false;
					}
				});
				if(done == $('.explorer-image').size()) {
					clearInterval(wizard._showImagesTask);
				}
			}, 100);
		},
		_addImagesToStep : function(step, stepidx) {
			var data = this._loadedImages;
			var wizard = this;
			for(var i = 0; i < data.length; i++) {
				var id = stepidx + '-' + i;
				var html = '<div class="explorer-image" id="explorer-image-' + id + '"><button class="explorer-image-button" type="button">Make It</button></div>';
				step.children(".create-image-container").append(html);
				$("#explorer-image-" + id).data('itemId', data[i].id);
				$("#explorer-image-" + id).data('material', data[i].material);
				$("#explorer-image-" + id).click(function() {
					wizard._itemId = $(this).data('itemId');
					wizard._material = $(this).data('material');
					wizard._imageClick(this);
				});
				$("#explorer-image-" + id + " button").click(function() {
					wizard._itemId = $(this).parent().data('itemId');
					wizard._appendHistory($(this).parent());
					wizard._addProductVariant();
					//$("#create-finish-dialog").dialog('close');
					$("#create-makeit-dialog").dialog('open');
					//wizard.makeIt();
					return false;
				});
				wizard._waitImage(data[i].image_url, id, 'hi', 0);
			}
			wizard._showNextImage = true;
		},
		_loadImages : function(step, stepidx, add) {
			var wizard = this;
			var params = this._getExploreParams();
			this._loadedImages = [];
			//console.log(wizard._itemId);
			$.getJSON(this._exploreURL, params, function(data) {
				wizard._loadedImages = data;
				if(add) {
					wizard._addImagesToStep(step, stepidx);
				}
			});
		},
		_getExploreParams : function() {
			var $steps = this.element.find(".jw-step"), $currentStep = $steps.eq(this._stepIndex);

			var paramType = $currentStep.data('paramType');
			var paramIndex = 0;

			if(paramType == 'model') {
				paramIndex = $currentStep.data('paramIndex');
			}

			var params = {
				param_index : paramIndex,
				text : this._userText,
				explore_type : 'iterate'
			};

			if(paramType == 'material') {
				params['material'] = 'Available'
			} else {
				params['material'] = this._material;
			}
			if(this._itemId != null) {
				params['item_id'] = this._itemId;
			} else {
				params['start_product'] = this._startProduct;
			}
			return params;
		},
		_imageClick : function(image_parent) {
			var $steps = this.element.find(".jw-step")
			this._appendHistory(image_parent);
			if(this._stepIndex == $steps.length - 1) {
				this._onLastStep();
			} else {
				this.nextStep();
			}
		},
		_appendHistory : function(image_parent) {
			var wizard = this;
			var last_image_clone = $(".jw-last").find(':first-child').find(':first-child').clone();
			//console.log(last_image_clone);
			var new_history_div;
			if(last_image_clone.length > 0) {
				new_history_div = $('<div />').append(last_image_clone);
				this._copyItemData($(".jw-last").find(':first-child')[0], new_history_div);
			}
			var cur_image_clone1 = $(image_parent).find(':first-child').clone();
			var cur_image_clone2 = $(cur_image_clone1).clone();
			var cur_image_clone3 = $(cur_image_clone1).clone();
			$('#create-finish-dialog-left').html(cur_image_clone2);
			$('#create-makeit-dialog-left').html(cur_image_clone3);
			var new_last_div = $('<div />').append(cur_image_clone1);
			new_last_div.append('<button class="explorer-image-button" type="button">Make It</button>');
			$(new_last_div).find('button').click(function() {
				wizard._itemId = $(this).parent().data('itemId');
				wizard._appendHistory($(this).parent());
				wizard._addProductVariant();
				//$("#create-finish-dialog").dialog('close');
				$("#create-makeit-dialog").dialog('open');
				return false;
			});
			this._copyItemData(image_parent, new_last_div);
			this.element.find(".jw-last").html(new_last_div);

			if(new_history_div != null) {
				new_history_div.append('<button class="explorer-image-button" type="button">Make It</button>');
				this.element.find(".jw-history").append(new_history_div);
				$(new_history_div).click(function() {
					wizard._itemId = $(this).data('itemId');
					wizard._material = $(this).data('material');
					wizard._appendHistory(this);
					wizard._changeStep(wizard._stepIndex);
				});

				$(new_history_div).find('button').click(function() {
					wizard._itemId = $(this).parent().data('itemId');
					wizard._appendHistory($(this).parent());
					wizard._addProductVariant();
					//$("#create-finish-dialog").dialog('close');
					$("#create-makeit-dialog").dialog('open');
					return false;
				});

				$(".jw-history").animate({
					scrollLeft : $(".jw-history")[0].scrollWidth
				}, 4000);
			}
		},
		_copyItemData : function(from, to) {
			var props = ['itemId', 'material', 'itemText'];
			for(var i = 0; i < props.length; i++) {
				$(to).data(props[i], $(from).data(props[i]));
			}
		},
		_getCurrentItem : function() {
			return $("#explorer-image-" + this._itemId);
		},
		_onLastStep : function() {
			//var currentItem =
			$("#create-finish-dialog").dialog('open');
		},
		_buildDialog : function() {
			var wizard = this;
			$("#create-finish-dialog").dialog({
				autoOpen : false,
				width : 570,
				height : 200,
				//position: [300, 300],
				resizable : false,
				modal : true,
				//dialogClass: 'alert'
			});
			$("#create-continue-creating").click(function() {
				wizard.changeStep(wizard._stepAfterLast);
				$("#create-finish-dialog").dialog('close');
				return false;
			});
			$("#create-show-details").click(function() {
				wizard._addProductVariant();
				$("#create-finish-dialog").dialog('close');
				$("#create-makeit-dialog").dialog('open');
			});
		},
		_addProductVariant : function() {
			var url = '/explorer/add_product_variant';
			var params = {
				item_uuid : this._itemId
			};
			$.getJSON(url, params, function(data) {
			});
		},
		_buildMakeitDialog : function() {
			var wizard = this;
			$("#create-makeit-dialog").dialog({
				autoOpen : false,
				width : 570,
				height : 200,
				//position: [300, 300],
				resizable : false,
				modal : true,
				//dialogClass: 'alert'
			});
			$("#create-makeit-dialog").find("button").click(function() {
				wizard._makeIt();
				$("#create-makeit-dialog").dialog('close');
			});
		},
		_makeIt : function() {
			var url = '/explorer/set_product_name';
			var name = $('#new-product-name').val();
			var params = {
				slug : this._itemId,
				new_name : name
			};
			var wizard = this;
			$.getJSON(url, params, function(data) {
				window.location = '/product/' + wizard._itemId + "?waitImages=true"
			});
		},
		_setAddress: function() {
			//console.log(this._stepIndex);
			//$.address.value(this._stepIndex);
			console.log(this._itemId);
			$.address.autoUpdate(false);
			$.address.parameter('step', this._stepIndex.toString());
			$.address.parameter('item', this._itemId);
			$.address.update();
			$.address.autoUpdate(true);
			
		},
		_initAddress: function() {
			var wizard = this;
			//$.address.autoUpdate(false);
			$.address.externalChange(function(evt){
				var stepIndex = parseInt($.address.parameter('step'),10)
				if(isNaN(stepIndex)||(stepIndex==-1)){
					stepIndex=0;
				}
				wizard._itemId = $.address.parameter('item');
				wizard._changeStep(stepIndex);
			});
		},
		/**
		 * @private
		 * @description Initializes the menu
		 *    Builds the menu based on the collection of steps
		 *    Assigns a class to the main <div> to indicate to CSS that there is a menu
		 *    Binds a click event to each of the <a> that will change the step accordingly when clicked
		 * @return void
		 */
		_buildMenu : function() {
			var list = [], $menu, $anchors;

			this.element.addClass("jw-hasmenu");
			this.element.find(".jw-step").each(function(x) {
				console.log(x);
				list.push($("<li />", {
				"class": "ui-corner-all " + (x === 0 ? "jw-current ui-state-highlight" : "jw-inactive ui-state-disabled"),
				html: $("<a />", {
				step: x,
				text: $(this).attr("title")
				})
				})[0]);
			});
			$menu = $("<div />", {
				"class" : "jw-menu-wrap",
				html : $("<div />", {
					"class" : "jw-menu",
					html : $("<ol />", {
						html : $(list)
					})
				})
			});

			this.element.find(".jw-content").prepend($menu);

			if(this.options.effects.enable || this.options.effects.menu.enable) {
				$menu.find("li").addClass("jw-animated");
			}

			$menu.find("a").click($.proxy(function(event) {
				var $target = $(event.target), nextStep = parseInt($target.attr("step"), 10);

				if($target.parent().hasClass("jw-active")) {
					this.changeStep(nextStep, nextStep <= this._stepIndex ? "previous" : "next");
				}
			}, this));
		},
		_buildTriangleButtons : function() {
			var $menu = $("<div />", {
				"class" : "jw-right-menu-wrap",
				html : $("<div />", {
					"class" : "jw-right-menu",
					html : $("<div />", {
						"class" : "triangle-button-right"
					})
				})
			});
			this.element.find(".jw-content").prepend($menu);
			var wizard = this;
			$menu.find(".triangle-button-right").click(function(event) {
				wizard.nextStep();
			});
			var $menu = $("<div />", {
				"class" : "jw-left-menu-wrap",
				html : $("<div />", {
					"class" : "jw-left-menu",
					html : $("<div />", {
						"class" : "triangle-button-left"
					})
				})
			});
			this.element.find(".jw-content").prepend($menu);
			var wizard = this;
			$menu.find(".triangle-button-left").click(function(event) {
				wizard.previousStep();
			});
		},
		_buildTopMenu : function() {
			var list = [], $menu, $anchors;
			var $steps = this.element.find(".jw-step");
			var constWidth = 26 * $steps.size();
			var stepWidth = Math.floor((840 - constWidth) / $steps.size());
			this.element.addClass("jw-hastopmenu");
			$steps.each(function(x) {
				var sClass = "wizard-steps-inner";
				var l = $(this).attr("title").split(' ');
				if(l.length == 1) {
					sClass = "wizard-steps-inner-ol";
				}
				var menuTitle = $(this).attr("title").replace(/ /g, "<br>");
				list.push($("<div />",{
				"class": "completed-step",
				step: x,
				html: $("<a />", {
				style: 'width: '+ stepWidth + 'px;',
				html: '<span>'+ (x+1).toString() + '</span>' + '<div class="'+ sClass +'">' + menuTitle + '</div>'
				})
				})[0]);
			});
			$menu = $("<div />", {
				"class" : "wizard-steps",
				html : $(list)
			});

			//console.log($menu);

			this.element.find(".jw-content").prepend($menu);

			/*if(this.options.effects.enable || this.options.effects.menu.enable) {
			 $menu.find("li").addClass("jw-animated");
			 }
			 */
			$menu.find("a").click($.proxy(function(event) {
				var $target = $(event.target), parent = $target.parents('div')[0], nextStep = parseInt($(parent).attr("step"), 10);
				console.log('click');
				console.log(parent);
				if($(parent).hasClass("completed-step")) {
					this.changeStep(nextStep, nextStep <= this._stepIndex ? "previous" : "next");
				}
			}, this));
		},
		/**
		 * @private
		 * @description Removes the 'jw-hasmenu' class and pulls the menu out of the DOM entirely
		 * @return void
		 */
		_destroyMenu : function() {
			this.element.removeClass("jw-hasmenu").find(".jw-menu-wrap").remove();
		},
		/**
		 * @private
		 * @description Updates the menu at the end of each call to _changeStep()
		 *    Each <a> is looped over, along with the parent <li>
		 *    Status (jw-current, jw-active, jw-inactive) set depending on progress through wizard
		 * @see this._changeStep()
		 * @return void
		 */
		_updateMenu : function(firstStep) {
			var wizard = this, currentStep = this._stepIndex, $menu = this.element.find(".jw-menu");

			if(!firstStep) {
				this._effect($menu.find("li:eq(" + currentStep + ")"), "menu", "change");
			}

			$menu.find("a").each(function(x) {
				var $a = $(this), $li = $a.parent(), iStep = parseInt($a.attr("step"), 10), sClass = "";

				if(iStep < currentStep) {
					sClass += "jw-active ui-state-default";
				} else if(iStep === currentStep) {
					sClass += "jw-current ui-state-highlight";
				} else if(iStep > currentStep) {
					sClass += "jw-active ui-state-default";
					//$a.removeAttr("href");
				}

				$li.removeClass("jw-active jw-current jw-inactive ui-state-default ui-state-highlight ui-state-disabled").addClass(sClass);
			});
		},
		_updateTopMenu : function(firstStep) {
			var wizard = this, currentStep = this._stepIndex, $menu = this.element.find(".wizard-steps");
			$menu.children().each(function(x) {
				var $d = $(this), iStep = parseInt($d.attr("step"), 10);
				//console.log(iStep);
				var sClass = "";
				if(iStep == currentStep) {
					sClass = "active-step";
				}
				$d.removeClass("active-step").addClass(sClass)
			});
		},
		/**
		 * @private
		 * @description Initializes the step counter.
		 *    A new <span> is created and used as the main element
		 * @return void
		 */
		_buildCounter : function() {
			var $counter = $("<span />", {
				"class" : "jw-counter ui-widget-content ui-corner-all jw-" + this.options.counter.orientText
			});

			if(this.options.counter.location === "header") {
				this.element.find(".jw-header").prepend($counter);
			} else if(this.options.counter.location === "footer") {
				this.element.find(".jw-footer").prepend($counter);
			}

			if(!this.options.counter.startCount) {
				this._stepCount--;
			}
			if(!this.options.counter.finishCount) {
				this._stepCount--;
			}

			if(this.options.effects.enable || this.options.effects.counter.enable) {
				$counter.addClass("jw-animated");
			}

			if(this.options.counter.progressbar) {
				$counter.html('<span class="jw-counter-text" /> <span class="jw-counter-progressbar" />').find(".jw-counter-progressbar").progressbar();
			}
		},
		/**
		 * @private
		 * @description This is run at the end of every call to this._changeStep()
		 * @return void
		 * @see this._changeStep()
		 */
		_updateCounter : function(firstStep) {
			var $counter = this.element.find(".jw-counter"), counterOptions = this.options.counter, counterText = "", actualIndex = this._stepIndex, actualCount = this._stepCount, percentage = 0;

			if(!counterOptions.startCount) {
				actualIndex--;
				actualCount--;
			}

			if(!firstStep) {
				this._effect($counter, "counter", "change");
			}
			percentage = Math.round((actualIndex / actualCount) * 100);

			if(counterOptions.type === "percentage") {
				counterText = ((percentage <= 100) ? percentage : 100) + "%";
			} else if(counterOptions.type === "count") {
				if(actualIndex < 0) {
					counterText = 0;
				} else if(actualIndex > actualCount) {
					counterText = actualCount;
				} else {
					counterText = actualIndex;
				}
				counterText += " of " + actualCount;
			} else {
				counterText = "N/A";
			}

			if(counterOptions.appendText) {
				counterText += " " + counterOptions.appendText;
			}

			if(counterOptions.progressbar) {
				this.element.find(".jw-counter-progressbar").progressbar("option", "value", percentage);
				this.element.find(".jw-counter-text").text(counterText);
			} else {
				$counter.text(counterText);
			}

			if((counterOptions.startHide && this._stepIndex === 0) || (counterOptions.finishHide && this._stepIndex === (this._actualCount - 1))) {
				$counter.hide();
			} else {
				$counter.show();
			}
		},
		/**
		 * @private
		 * @description Removes the counter DOM elements, resets _stepCount
		 * @return void
		 */
		_destroyCounter : function() {
			this.element.find(".jw-counter").remove();
		},
		/**
		 * @private
		 * @description This generates the <button> elements for the main navigation and binds `click` handlers to each of them
		 * @see this._changeStep()
		 */
		_buildButtons : function() {
			var self = this, options = this.options.buttons, $footer = $("<div />", {
				"class" : "jw-footer ui-corner-bottom"
			}), $cancel = $('<button type="' + options.cancelType + '" class="ui-state-default ui-corner-all jw-button-cancel jw-priority-secondary' + (options.cancelHide ? " ui-helper-hidden" : "") + '">' + options.cancelText + '</button>'), $previous = $('<button type="button" class="ui-state-default ui-corner-all jw-button-previous">' + options.previousText + '</button>'), $next = $('<button type="button" class="ui-state-default ui-corner-all jw-button-next">' + options.nextText + '</button>'), $finish = $('<button type="' + options.finishType + '" class="ui-state-default ui-corner-all jw-button-finish ui-state-highlight">' + options.finishText + '</button>');

			$cancel.click(function(event) {
				self._trigger("cancel", event);
			});
			$previous.click(function(event) {
				self.previousStep();
			});
			$next.click(function(event) {
				self.nextStep();
			});
			$finish.click(function(event) {
				self._trigger("finish", event);
			});
			if(options.jqueryui.enable) {
				$cancel.button({
					icons : {
						primary : options.jqueryui.cancelIcon
					}
				});
				$previous.button({
					icons : {
						primary : options.jqueryui.previousIcon
					}
				});
				$next.button({
					icons : {
						secondary : options.jqueryui.nextIcon
					}
				});
				$finish.button({
					icons : {
						secondary : options.jqueryui.finishIcon
					}
				});
			}

			this.element.append($footer.append('<div class="jw-history" /><div class="jw-last" />'));
			if(this._productType == 'variant') {
				var new_div = $('<div />').append($("#start-product-img").clone());
				this.element.find(".jw-last").html(new_div);
			}
		},
		/**
		 * @private
		 * @description Updates the visibility status of each of the buttons depending on the end-user's progress
		 * @see this._changeStep()
		 */
		_updateButtons : function() {
			var $steps = this.element.find(".jw-step"), $previous = this.element.find(".jw-button-previous"), $next = this.element.find(".jw-button-next"), $finish = this.element.find(".jw-button-finish");
			var $trPrevious = this.element.find(".triangle-button-left");
			switch ($steps.index($steps.filter(":visible"))) {
				case 0:
					$previous.hide();
					$next.show();
					$finish.hide();
					$trPrevious.hide();
					break;

				case $steps.length - 1:
					$previous.show();
					$next.hide();
					$finish.show();
					$trPrevious.show();
					break;

				default:
					$previous.show();
					$next.show();
					$finish.hide();
					$trPrevious.show();
					break;
			}
		},
		_disableButtons : function() {
			this.element.find(".jw-buttons button").addClass("ui-state-disabled").attr("disabled", true);
		},
		_enableButtons : function() {
			this.element.find(".jw-buttons button").removeClass("ui-state-disabled").attr("disabled", false);
		},
		/**
		 * @private
		 * @description Updates the visibility status of each of the buttons depending on the end-user's progress
		 * @see this._changeStep()
		 */
		_destroyButtons : function() {
			this.element.find(".jw-footer").remove();
		},
		/**
		 * @property object options This is the set of configuration options available to the user.
		 */
		options : {
			debug : false,
			disabled : false,
			titleHide : false,
			menuEnable : false,
			//hotkeys: false,

			buttons : {
				jqueryui : {
					enable : false,
					cancelIcon : "ui-icon-circle-close",
					previousIcon : "ui-icon-circle-triangle-w",
					nextIcon : "ui-icon-circle-triangle-e",
					finishIcon : "ui-icon-circle-check"
				},
				cancelHide : false,
				cancelType : "button",
				finishType : "button",
				cancelText : "Cancel",
				previousText : "Previous",
				nextText : "Next",
				finishText : "Finish"
			},

			counter : {
				enable : false,
				type : "count",
				progressbar : false,
				location : "footer",
				startCount : true,
				startHide : false,
				finishCount : true,
				finishHide : false,
				appendText : "Complete",
				orientText : "left"
			},

			effects : {
				enable : false,
				step : {
					enable : false,
					hide : {
						type : "slide",
						options : {
							direction : "left"
						},
						duration : "fast"
					},
					show : {
						type : "slide",
						options : {
							direction : "left"
						},
						duration : "fast"
					}
				},
				title : {
					enable : false,
					hide : {
						type : "slide",
						duration : "fast"
					},
					show : {
						type : "slide",
						duration : "fast"
					}
				},
				menu : {
					enable : false,
					change : {
						type : "highlight",
						duration : "fast"
					}
				},
				counter : {
					enable : false,
					change : {
						type : "highlight",
						duration : "fast"
					}
				}
			},

			cancel : $.noop,
			previous : $.noop,
			next : $.noop,
			finish : $.noop,

			changestep : function(event, ui) {
				if(event.isDefaultPrevented()) {
					if( typeof event.nextStepIndex !== "undefined") {
						ui.wizard.jWizard("changeStep", event.nextStepIndex);
						return false;
					}
				}
			}
		}
	});
}(jQuery));

$(document).ready(function() {
	$("#wizard").jWizard({
		menuEnable : true,
		effects : {
			enable : false,
			step : {
				enable : false,
				hide : {
					type : "fade",
					options : {
					},
					duration : 2000
				},
				show : {
					type : "slide",
					options : {
					},
					duration : 0
				}
			},
			title : {
				enable : false,
				hide : {
					type : "slide",
					duration : "fast"
				},
				show : {
					type : "slide",
					duration : "fast"
				}
			},
			menu : {
				enable : false,
				change : {
					type : "highlight",
					duration : "fast"
				}
			},
			counter : {
				enable : false,
				change : {
					type : "highlight",
					duration : "fast"
				}
			}
		},
	});
	
	$('#text-next').click(function() {
		$("#wizard").jWizard("nextStep");
	});
});
