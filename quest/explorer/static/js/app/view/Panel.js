Ext.define('Quest.view.Panel', {
	extend : 'Ext.panel.Panel',
	layout : 'card',
	width : 605,
	qItemsType : 'definition',
	qFadoutDuration : 3500,
	qFadinDuration : 1200,
	qImageDisplayInterval : 800,
	nextImageIndex : 0,
	pageSize : 8,
	qFirstPage : true,
	/*tbar : [{
	 xtype : 'button',
	 text : 'Near',
	 width : 80,
	 id : 'distance-near',
	 toggleGroup : 'mygroup',
	 enableToggle : true
	 }, {
	 xtype : 'button',
	 text : 'Far',
	 width : 80,
	 id : 'distance-medium',
	 toggleGroup : 'mygroup',
	 enableToggle : true,
	 pressed : true
	 }, {
	 xtype : 'button',
	 text : 'Far',
	 width: 80,
	 id: 'distance-far',
	 toggleGroup : 'mygroup',
	 enableToggle : true,
	 //listeners:
	 }],*/
	initComponent : function() {
		this.qCreateDialog();
		this.callParent();
		store0 = Ext.create('Quest.store.Items');
		store1 = Ext.create('Quest.store.Items');
		/*
		 this.historyStore = Ext.create('Quest.store.Items');
		 this.historyView = Ext.create('Quest.view.History', {
		 store : this.historyStore,
		 height : 640,
		 width : 630
		 });
		 */
		this.qStores = [store0, store1];
		grid0 = Ext.create('Quest.view.ImageGrid', {
			store : store0,
			height : 605,
			width : 605
		});
		grid1 = Ext.create('Quest.view.ImageGrid', {
			store : store1,
			height : 605,
			width : 605
		});
		this.qGrids = [grid0, grid1]

		Ext.iterate(this.qGrids, function(grid, index) {
			grid.qIndex = index;
			grid.on({
				itemClick : {
					fn : this.qqOnItemClick,
					scope : this
				},
				refresh : {
					fn : this.qOnGridRefresh,
					scope : this
				},
				beforeitemmouseenter : {
					fn : this.qOnMouseEnter,
					scope : this
				},
				beforeitemmouseleave : {
					fn : this.qOnMouseLeave,
					scope : this
				}
			});
		}, this);

		Ext.iterate(this.qStores, function(store, index) {
			store.qIndex = index;
			store.on({
				load : {
					fn : this.qOnStoreLoad,
					scope : this
				}
			});
		}, this);

		this.qFront = 0;
		this.qBack = 1;
		this.clickIndex = 0;
		this.add(this.qGrids);
		this.itemTpl = ['<tpl for=".">', '<div class="thumb-wrap" id="{id}">', '<div class="thumb"><img id="img_{id}" src="{image_url}" title="{index}"></div>', '<span class="x-editable"></span></div>', '</tpl>', '<div class="x-clear"></div>'];

	},
	qCreateDialog : function() {
		var dialogOpts = {
			buttons : {
				"Ok" : function() {
				},
				"Cancel" : function() {
					$("#creation-details-dialog").dialog("close");
				}
			},
			autoOpen : false,
			modal : true,
			width : "auto",
			dialogClass : 'noTitleStuff'
		};
		$("#creation-details-dialog").dialog(dialogOpts);
	},
	afterRender : function() {
		this.callParent();
		this.qStores[this.qFront].load({
			params : {
				show_definitions : true
			}
		});
		this.qCreateCanvas();
	},
	afterLayout: function(){
		console.log('hi');
		console.log(this.getPosition());
		pos = this.getPosition();
		this.qCenter = [pos[0]+195+3,pos[1]+195+3];
	},
	qOnStoreLoad : function(store, records) {
		var ln = records.length
		p = self.page_size
		hp = p / 2
		if(this.qFirstPage == false) {
			store.add(this.qLastClickedRec);
			ln += 1;
		} 

		this.imageOrder = this.qRandomPermutation(ln);
		this.qSetImageEvents(store, records);

		if(this.qItemsType == 'definition') {
			task2 = {
				run : this.qWaitImages,
				args : [this.qFront],
				interval : 200,
				scope : this
			};
			Ext.TaskManager.start(task2);
		}
	},
	qSetImageEvents : function(store, records) {
		//console.log('qSetImageEvents');
		var grid = this.qGrids[store.qIndex];
		var nodes = grid.getNodes();
		for(var i = 0; i < nodes.length; i++) {
			im = Ext.fly(nodes[i].firstChild.firstChild);
			node = nodes[i];
			im.on('load', function(evt, el) {
				//console.log('loaded image');
				id = el.id.substring(4);
				var rec = store.getAt(store.findExact('id', id));
				//console.log(rec.data.id);
				//console.log(rec.data.image_url);
				rec.data.loaded = true;
			}, this);
			im.on('error', function(evt, el) {
				id = el.id.substring(4);
				var rec = store.getAt(store.findExact('id', id));
				var date = new Date();
				var url = rec.data.image_url + '?v=' + date.getTime();
				var task = new Ext.util.DelayedTask(function(el, url) {
					el.src = url;
				}, this, [el, url]);
				task.delay(600);
			}, this);
		}
	},
	qqOnItemClick : function(view, record, item) {
		return this.qOnItemClick(view, record, item, 'medium')
	},
	qOnItemClick : function(view, record, item, distance) {
		this.clickIndex++;
		console.log(this.clickIndex);
		this.qLastClickedRec = record
		//console.log(this.qFirstPage)
		Ext.TaskManager.stop(task2);
		task2 = {
			run : this.qWaitImage2,
			args : [this.qBack],
			interval : 200,
			scope : this
		};
		var animate = this.qItemsType == 'model';
		this.qLoadStore(this.qBack, record, distance, this.clickIndex-2);
		var task1 = new Ext.util.DelayedTask(function() {
			this.qStores[this.qFront].removeAll();
			this.qToggleActive();
			var p = Ext.getCmp('floating-panel' + this.qLastClickedRec.data.id);
			if(p != null) {
				Ext.destroy(p);
			}
			this.showNextImage = true;
			Ext.TaskManager.start(task2);
		}, this);
		duration = 1000;
		if(animate) {
			duration = this.qFadoutDuration
			this.qAnimateSelected(this.qFront, this.qFadoutDuration - 200, record, item);
		}
		this.qFadeOut(this.qFront, duration);
		task1.delay(duration);

		return false;
	},
	qWaitImages : function(index) {
		//console.log('waitImages');
		store = this.qStores[index];
		if(store.getCount() == 0)
			return;
		var idx = store.findExact('loaded', false);
		if(idx == -1) {
			//console.log('all here');
			Ext.TaskManager.stop(task2);
			this.qFadeIn(index, this.qFadinDuration);
		}
	},
	qWaitImage2 : function(storeIndex) {
		//console.log(this.showNextImage);
		if(this.showNextImage == false) {
			return;
		}
		this.showNextImage = false;

		var toDisplay = null;
		var store = this.qStores[storeIndex];
		var records = store.getRange();
		for(var i = 0; i < records.length; i++) {
			o = this.imageOrder[i];
			if(records[o].data.loaded == true && records[o].data.displayed == false) {
				//toDisplay = records[i];
				toDisplay = o;
				break;
			}
		}

		if(toDisplay == null) {
			this.showNextImage = true;
			return;
		}

		records[toDisplay].data.displayed = true;
		this.qFadeInOne(storeIndex, this.qFadinDuration, toDisplay);

		if(store.findExact('displayed', false) == -1) {
			Ext.TaskManager.stop(task2);
		}

		var task = new Ext.util.DelayedTask(function(storeIndex, itemIndex) {
			this.showNextImage = true;
		}, this, [storeIndex, toDisplay]);

		task.delay(this.qImageDisplayInterval)
	},
	qAnimateSelected : function(index, duration, record, item) {
		var el = Ext.get(item);
		var top = el.getTop();
		var left = el.getLeft();
		id = 'fl-im-' + record.data.id;
		pos = this.getPosition();
		this.qCenter = [pos[0]+195+3,pos[1]+195+3];
		//console.log(top + ' ' + left);
		var p = Ext.create('Ext.panel.Panel', {
			width : 195,
			height : 195,
			padding : 7,
			id : 'floating-panel' + record.data.id,
			frame : true,
			floating : true,
			shadow : true,
			hidden : true,
			html : '<img id="' + id + '" width=180px height=180px src="' + item.firstChild.firstChild.src + '">',
			listeners : {
				'afterrender' : function(panel) {
					panel.setPosition(left, top);
					Ext.fly(id).on('load', function(evt, nel) {
						p.show();
						el.setVisible(false);
					}, this);
				}
			}
		});
		p.render(Ext.getBody());
		//pos = this.qGrids[0].getPosition(true);
		Ext.create('Ext.fx.Anim', {
			target : p,
			duration : duration,
			from : {
				top : top,
				left : left
			},
			to : {
				top : this.qCenter[1],
				left : this.qCenter[0]
			},
		});
	},
	qFadeOut : function(index, duration) {
		var nodes = this.qGrids[index].getNodes();
		for(var i = 0; i < nodes.length; i++) {
			var el = Ext.get(nodes[i]);
			el.fadeOut({
				opacity : 0,
				easing : 'easeOut',
				duration : duration,
				remove : false,
				useDisplay : false
			});
		}
	},
	qFadeIn : function(index, duration) {
		var nodes = this.qGrids[index].getNodes();
		for(var i = 0; i < nodes.length; i++) {
			var el = Ext.get(nodes[i]);
			el.fadeOut({
				opacity : 1,
				easing : 'easeIn',
				duration : duration,
				remove : false,
				useDisplay : false
			});
		}
	},
	qFadeInOne : function(index, duration, itemIndex) {
		var node = this.qGrids[index].getNode(itemIndex);
		var el = Ext.get(node);
		el.fadeOut({
			opacity : 1,
			easing : 'easeIn',
			duration : duration,
			remove : false,
			useDisplay : false
		});
	},
	qLoadStore : function(index, record, distance, param_index) {
		if(this.qItemsType == 'definition') {
			this.qItemsType = 'model';
			this.qFirstPage = true;
			this.qDefinitionId = record.data.id;
			this.qStores[0].definitionId = record.data.id;
			this.qStores[1].definitionId = record.data.id;
			this.qStores[index].load({
				params : {
					definition_id : record.data.id,
					distance : distance,
					param_index: param_index
				}
			});
		} else {
			this.qFirstPage = false
			this.qItemId = record.data.id;
			this.qStores[index].itemId = record.data.id;
			this.qStores[index].load({
				params : {
					item_id : record.data.id,
					distance : distance,
					param_index: param_index
				}
			});
		}
	},
	qToggleActive : function() {
		t = this.qFront;
		this.qFront = this.qBack;
		this.qBack = t;
		this.getLayout().setActiveItem(this.qFront);
	},
	qRandomPermutation : function(x) {
		var l = []
		for(var i = 0; i < x; i++)
		l.push(i);
		for(var j = x - 1; x >= 0; x--) {
			a = Math.floor(Math.random() * j);
			t = l[a];
			l[a] = l[j];
			l[j] = t;
		}
		//console.log(l);
		return l;
	},
	qFindDistance : function() {
		if(Ext.getCmp('distance-near').pressed == true) {
			return 'near';
			return [0.01, 0.13];
		}
		if(Ext.getCmp('distance-medium').pressed == true) {
			return 'medium';
			return [0.05, 0.25];
		}
		if(Ext.getCmp('distance-far').pressed == true) {
			return 'far';
			return [0.1, 0.4];
		}
	},
	qOnGridRefresh : function(grid) {
		//console.log('refresh');

		var nodes = grid.getNodes();
		if(nodes.length != this.pageSize + 1)
			return;
		//console.log(nodes.length)
		var parentEl = grid.getTargetEl();
		//items_pos = [[95, 0], [290, 0], [0, 195], [390, 195], [95, 390], [290, 390], [195, 195]]
		items_pos = [[0, 0],    [195, 0],     [390, 0], 
		             [0, 195],               [390, 195],
		             [0, 390],  [195, 390],   [390, 390],
		             [195, 195]]
		if(this.qFirstPage != true) {
			Ext.get(nodes[this.pageSize]).applyStyles({
				opacity : 1
			});
		}

		//console.log(Ext.get(nodes[0]));
		for(var i = 0; i < nodes.length; i++) {
			Ext.get(nodes[i]).applyStyles({
				position : 'absolute',
				left : items_pos[i][0] + "px",
				top : items_pos[i][1] + "px"
			});
		}
	},
	qCreateCanvas : function() {
		var p = Ext.create('Ext.panel.Panel', {
			width : 198,
			height : 225,
			border:false,
			padding : 7,
			id : 'canvas-panel',
			frame : false,
			floating : true,
			shadow : false,
			bodyStyle: 'background:transparent;',
			hidden : true,
			html : '<canvas id="hover-canvas" style="opacity: 1; position: absolute; left: 0px; top: 0px" width=180px height=180px></canvas>'+
				'<div style="height: 30px; position: absolute; left: 0px; top: 154px" id="image-buttons">'+
				'<button id="makeit-button" style="position: absolute; width: 76px; left: -11px; top: -3px;" >Make It!</button></div>',
			listeners : {
				'afterrender' : {
					fn : function(panel) {
						canvas = this.qCreateTarget();
						Ext.fly(canvas).on('click', function(evt, el, o) {
							var p1 = Ext.fly(el).getXY();
							var p2 = evt.getXY();
							var x = (p2[0] - p1[0]);
							var y = (p2[1] - p1[1]);
							var r = (Math.sqrt(Math.pow(x - 55, 2) + Math.pow(y - 20, 2)));
							var r1 = (Math.sqrt(Math.pow(x - 20, 2) + Math.pow(y - 160, 2)))
							var distance = 'linear'
							if(r <= 20)
								distance = 'random';
							this.qOnItemClick(null, this.currRec, this.curItem, distance);
							Ext.getCmp('canvas-panel').hide();
						}, this);
						Ext.fly(canvas).on('mouseout', function() {
							Ext.getCmp('canvas-panel').hide();

						}, this);
					},
					scope : this
				}
			}
		});
		p.render(Ext.getBody());
	},
	qCreateTarget : function() {
		canvas = document.getElementById("hover-canvas");
		ctx = canvas.getContext('2d');
		ctx.globalCompositeOperation = 'source-over';
		//outer
		ctx.beginPath();
		ctx.fillStyle = "rgba(255, 0, 0, 0.15)";
		ctx.arc(20, 20, 15, 0, 2 * Math.PI, false);
		//ctx.fill();
		ctx.closePath();
		//inner
		ctx.beginPath();
		ctx.fillStyle = "rgba(0, 255, 0, 0.12)";
		ctx.arc(55, 20, 15, 0, 2 * Math.PI, false);
		//ctx.fill();
		ctx.closePath();
		Ext.fly('makeit-button').on('click', function(){
			this.qAddProductVariant(this.currRec);
		}, this);
		return canvas;
	},
	qOnMouseEnter : function(view, rec, item) {
		//console.log('enter')
		if(rec.data.displayed != true)
			return;
		p = Ext.getCmp('canvas-panel');
		//if(p.is)
		xy = Ext.fly(item).getXY();
		p.setPosition(xy[0]-2, xy[1]);
		this.currRec = rec;
		this.curItem = item;
		p.show();
	},
	qOnMouseLeave : function(view, rec, item) {
		//console.log('leave')
		//Ext.getCmp('canvas-panel').hide();
	},
	qAddProductVariant : function(rec) {
		//this.qOpenDialog();
		Ext.Ajax.request({
			url : '/explorer/add_product_variant',
			params : {
				item_uuid : rec.data.id
			},
			success : function(response) {
				window.location = '/product/'+rec.data.id
			}
		});

	},
	qOpenDialog : function() {
		$("#creation-details-dialog").dialog("open");
	}
});
