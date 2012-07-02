Ext.define('Quest.Controller', {
	extend : 'Ext.app.Controller',
	//stores: ['EZ3D_store.store.Materials'],
	//views: ['EZ3D.creators.snow.view.Panel'],
	gridWidth : 600,
	gridHeight : 600,
	pageSize : 6,
	imageSize : 195,
	imageNetSize : 180,
	rowSize : 3,
	fadoutDuration : 3500,
	fadinDuration : 1200,
	imageDisplayInterval : 800,
	nextImageIndex : 0,
	firstPage : true,
	algoName : 'Explore',
	itemsType : 'definition',
	refs : [{
		ref : 'explorerPanel',
		selector : '#explorer-panel'
	}, {
		ref : 'itemMenu',
		selector : '#explorer-item-menu'
	}, {
		ref : 'messagePanel',
		selector : '#explorer-message-panel'
	}, {
		ref : 'algoCombo',
		selector : '#algoCombo'
	}, {
		ref : 'materialCombo',
		selector : '#materialCombo'
	}],

	init : function() {
		console.log('init');
		this.getAlgoCombo().on('change', this.algoChange, this);
		this.getMaterialCombo().on('change', this.materialChange, this);
		var store0 = Ext.create('Quest.store.Items', {
			storeId : 'Items0'
		});
		var store1 = Ext.create('Quest.store.Items', {
			storeId : 'Items1'
		});
		this.itemStores = [store0, store1];
		var grid0 = Ext.create('Quest.view.ImageGrid', {
			store : store0,
			width : this.gridWidth,
			height : this.gridHeight
		});
		var grid1 = Ext.create('Quest.view.ImageGrid', {
			store : store1,
			width : this.gridWidth,
			height : this.gridHeight
		});
		this.grids = [grid0, grid1];
		Ext.iterate(this.grids, function(grid, index) {
			grid._index = index;
			grid.on({
				itemClick : {
					fn : function(view, record, item) {
						this.onItemClick(view, record, item, 'medium', 'linear', 'explore');
					},
					scope : this
				},
				refresh : {
					fn : this.onGridRefresh,
					scope : this
				},
				beforeitemmouseenter : {
					fn : this.onItemMouseEnter,
					scope : this
				},
				beforeitemmouseleave : {
					fn : this.onItemMouseLeave,
					scope : this
				}
			});
		}, this);

		Ext.iterate(this.itemStores, function(store, index) {
			store._index = index;
			store.on({
				load : {
					fn : this.onStoreLoad,
					scope : this
				}
			});
		}, this);

		this.front = 0;
		this.back = 1;
		this.clickIndex = 0;
		/*this.itemStores[this.front].load({
		 params : {
		 show_definitions : true
		 }
		 });*/

		this.loadInitialItems();
		this.getExplorerPanel().on('afterrender', this.afterExplorerPanelRender, this);
		this.getItemMenu().on('afterrender', this.afterItemMenuRender, this);
		//this.getItemMenu().on('afterrender', this.afterItemMenuRender, this);
	},
	loadInitialItems : function() {
		console.log(window.location)
		var qs = Ext.Object.fromQueryString(window.location.search.substring(1));
		if(qs.start_product != null) {
			this.firstPage = false;
			this.itemsType = 'model';
			waitImagesTask = {
				run : this.waitImagesIterate,
				args : [this.front],
				interval : 200,
				scope : this
			};
			this.itemStores[this.front].load({
				params : {
					start_product : qs.start_product
				}
			});

			this.showNextImage = true;
			Ext.TaskManager.start(waitImagesTask);
			//this.showMessage('Hi');
		} else {
			this.itemStores[this.front].load({
				params : {
					show_definitions : true
				}
			});
		}
		//console.log(qs.start_product !);
	},
	afterItemMenuRender : function() {
		console.log('afterItemMenuRender');
		this.getItemMenu().setWidth(this.imageSize);
		this.getItemMenu().setHeight(this.imageSize);

		var canvas0 = Ext.get('item-menu-explore');
		canvas0.dom.width = this.imageNetSize;
		canvas0.dom.height = this.imageNetSize;
		this.createExploreMenu(canvas0.dom);

		canvas0.on('click', function(evt, el, o) {
			this.exploreMenuClick(el, evt);
			this.getItemMenu().hide();
		}, this);
		canvas0.on('mouseout', function() {
			this.getItemMenu().hide();
		}, this);
		canvas1 = Ext.get('item-menu-iterate');
		canvas1.dom.width = this.imageNetSize;
		canvas1.dom.height = this.imageNetSize;
		this.createIterateMenu(canvas1.dom);
		canvas1.hide();
		canvas1.on('click', function(evt, el, o) {
			this.iterateMenuClick(el, evt);
			this.getItemMenu().hide();
		}, this);
		canvas1.on('mouseout', function() {
			this.getItemMenu().hide();
		}, this);
		canvas2 = Ext.get('item-menu-axis');
		canvas2.dom.width = this.imageNetSize;
		canvas2.dom.height = this.imageNetSize;
		this.createAxisMenu(canvas2.dom);
		canvas2.hide();
		canvas2.on('click', function(evt, el, o) {
			this.axisMenuClick(el, evt);
			this.getItemMenu().hide();
		}, this);
		canvas2.on('mouseout', function() {
			this.getItemMenu().hide();
		}, this);

		this.itemMenus = {
			'Explore' : canvas0,
			'Iterate' : canvas1,
			'Axis' : canvas2
		};

		Ext.fly('item-menu-buttons').setTop(this.imageSize - 40);
		Ext.fly('makeit-button').on('click', function() {
			this.addProductVariant(this.currRec);
		}, this);
	},
	afterExplorerPanelRender : function() {
		console.log('afterExplorerPanelRender');
		this.getExplorerPanel().add(this.grids);
		var qs = Ext.Object.fromQueryString(window.location.search.substring(1));
		if(qs.start_product != null) {
			this.showMessage('Hi');
		}
		//this.control();

	},
	algoChange : function(combo, newVal, oldVal) {
		this.algoName = newVal;
		this.itemMenus[oldVal].hide();
		this.itemMenus[newVal].show();
		if(newVal == 'Axis') {
			this.pageSize = 8;
		} else {
			this.pageSize = 6;
		}
	},
	materialChange : function(combo, newVal, oldVal) {
		console.log(newVal);
		//this.showMessage('hi');
	},
	onStoreLoad : function(store, records) {
		var ln = records.length
		if((this.firstPage == false) && (this.lastClickedRec != null)) {
			store.add(this.lastClickedRec);
			ln += 1;
		}

		if(this.algoName == 'Iterate') {
			this.imageOrder = [0, 1, 2, 3, 4, 5, 6];
		} else {
			this.imageOrder = this.randomPermutation(ln);
		}
		if((this.firstPage == false) && (this.lastClickedRec == null)) {
			//store.add(this.lastClickedRec);
			this.imageOrder = this.randomPermutation(ln - 1);
			this.imageOrder.push(6);
		}
		this.setImageEvents(store, records);

		if(this.itemsType == 'definition') {
			waitImagesTask = {
				run : this.waitImagesAll,
				args : [this.front],
				interval : 200,
				scope : this
			};
			Ext.TaskManager.start(waitImagesTask);
		}
		r = store.getRange();
		console.log(r);
	},
	setImageEvents : function(store, records) {
		var grid = this.grids[store._index];
		var nodes = grid.getNodes();
		for(var i = 0; i < nodes.length; i++) {
			im = Ext.fly(nodes[i].firstChild.firstChild);
			node = nodes[i];
			im.on('load', function(evt, el) {
				id = el.id.substring(4);
				var rec = store.getAt(store.findExact('id', id));
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
	waitImagesAll : function(index) {
		store = this.itemStores[index];
		if(store.getCount() == 0)
			return;
		var idx = store.findExact('loaded', false);
		if(idx == -1) {
			Ext.TaskManager.stop(waitImagesTask);
			this.fadeIn(index, this.fadinDuration);
		}
	},
	waitImagesIterate : function(storeIndex) {
		if(this.showNextImage == false) {
			return;
		}
		this.showNextImage = false;

		var toDisplay = null;
		var store = this.itemStores[storeIndex];
		var records = store.getRange();
		console.log(records.length);
		for(var i = 0; i < records.length; i++) {
			o = this.imageOrder[i];
			if(records[o].data.loaded == true && records[o].data.displayed == false) {
				toDisplay = o;
				break;
			}
		}

		if(toDisplay == null) {
			this.showNextImage = true;
			return;
		}

		records[toDisplay].data.displayed = true;
		this.fadeInOne(storeIndex, this.fadinDuration, toDisplay);
		if(records[toDisplay].data.index != 6) {
			this.getMessagePanel().hide();
		};
		if(store.findExact('displayed', false) == -1) {
			Ext.TaskManager.stop(waitImagesTask);
		}

		var task = new Ext.util.DelayedTask(function(storeIndex, itemIndex) {
			this.showNextImage = true;
		}, this, [storeIndex, toDisplay]);

		task.delay(this.imageDisplayInterval)

	},
	fadeIn : function(index, duration) {
		var nodes = this.grids[index].getNodes();
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
	fadeOut : function(index, duration) {
		var nodes = this.grids[index].getNodes();
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
	fadeInOne : function(index, duration, itemIndex) {
		var node = this.grids[index].getNode(itemIndex);
		var el = Ext.get(node);
		el.fadeOut({
			opacity : 1,
			easing : 'easeIn',
			duration : duration,
			remove : false,
			useDisplay : false
		});
	},
	onGridRefresh : function(grid) {
		var nodes = grid.getNodes();
		if(nodes.length != this.pageSize + 1)
			return;

		var parentEl = grid.getTargetEl();
		items_pos = []
		if(this.pageSize != 6) {
			for(var i = 0; i < this.rowSize; i++) {
				for(var j = 0; j < this.rowSize; j++) {
					if((i == 0) || (j == 0) || (i == this.rowSize - 1) || (j == this.rowSize - 1)) {
						items_pos.push([i * this.imageSize, j * this.imageSize])
					}
				}
			}
		} else {
			items_pos = [[this.imageSize * (1 / 2), 0], [this.imageSize * (3 / 2), 0], [0, this.imageSize], [this.imageSize * 2, this.imageSize], [this.imageSize * (1 / 2), this.imageSize * 2], [this.imageSize * (3 / 2), this.imageSize * 2]]
		}
		items_pos.push([this.imageSize, this.imageSize])

		if(this.firstPage != true) {
			Ext.get(nodes[this.pageSize]).applyStyles({
				opacity : 1
			});
		}

		for(var i = 0; i < nodes.length; i++) {
			Ext.get(nodes[i]).applyStyles({
				position : 'absolute',
				left : items_pos[i][0] + "px",
				top : items_pos[i][1] + "px"
			});
		}
	},
	randomPermutation : function(x) {
		var l = []
		for(var i = 0; i < x; i++)
		l.push(i);
		for(var j = x - 1; x >= 0; x--) {
			a = Math.floor(Math.random() * j);
			t = l[a];
			l[a] = l[j];
			l[j] = t;
		}
		return l;
	},
	onItemMouseEnter : function(view, rec, item) {
		console.log('enter')
		if(rec.data.displayed != true)
			return;
		p = Ext.getCmp('explorer-item-menu');
		//p = Ext.getCmp('canvas-panel');
		//if(p.is)
		//p.setWidth(165);
		xy = Ext.fly(item).getXY();
		p.setPosition(xy[0] - 2, xy[1]);
		this.currRec = rec;
		this.curItem = item;
		p.show();
	},
	onItemMouseLeave : function() {
		return true;
	},
	onItemClick : function(view, record, item, distance, iterateType, exploreType) {
		this.clickIndex++;
		this.lastClickedRec = record
		Ext.TaskManager.stop(waitImagesTask);
		waitImagesTask = {
			run : this.waitImagesIterate,
			args : [this.back],
			interval : 200,
			scope : this
		};
		var animate = this.itemsType == 'model';
		this.loadStore(this.back, record, distance, this.clickIndex - 2, iterateType, exploreType);
		var task1 = new Ext.util.DelayedTask(function() {
			this.itemStores[this.front].removeAll();
			this.toggleActive();
			var p = Ext.getCmp('floating-panel' + this.lastClickedRec.data.id);
			if(p != null) {
				Ext.destroy(p);
			}
			this.showNextImage = true;
			Ext.TaskManager.start(waitImagesTask);
		}, this);
		duration = 1000;
		if(animate) {
			duration = this.fadoutDuration
			this.animateSelected(this.front, this.fadoutDuration - 200, record, item);
		}
		this.fadeOut(this.front, duration);
		task1.delay(duration);
		this.showMessage('Hi');
		return false;
	},
	loadStore : function(index, record, distance, paramIndex, iterateType, exploreType) {
		console.log(this.getMaterialCombo().getValue());
		if(this.itemsType == 'definition') {
			this.itemsType = 'model';
			this.firstPage = true;
			this.definitionId = record.data.id;
			this.itemStores[0].definitionId = record.data.id;
			this.itemStores[1].definitionId = record.data.id;
			this.itemStores[index].load({
				params : {
					definition_id : record.data.id,
					distance : distance,
					param_index : paramIndex,
					explore_type : exploreType,
					iterate_type : iterateType,
					page_size : this.pageSize,
					material : this.getMaterialCombo().getValue()
				}
			});
		} else {
			this.firstPage = false
			this.itemId = record.data.id;
			this.itemStores[index].itemId = record.data.id;
			this.itemStores[index].load({
				params : {
					item_id : record.data.id,
					distance : distance,
					param_index : paramIndex,
					explore_type : exploreType,
					iterate_type : iterateType,
					page_size : this.pageSize,
					material : this.getMaterialCombo().getValue()
				}
			});
		}
	},
	toggleActive : function() {
		t = this.front;
		this.front = this.back;
		this.back = t;
		this.getExplorerPanel().getLayout().setActiveItem(this.front);
	},
	animateSelected : function(index, duration, record, item) {
		var el = Ext.get(item);
		var top = el.getTop();
		var left = el.getLeft();
		id = 'fl-im-' + record.data.id;
		pos = this.getExplorerPanel().getPosition();
		this.center = [pos[0] + this.imageSize + 3, pos[1] + this.imageSize + 3];
		var realSize = this.imageSize - 15;
		var p = Ext.create('Ext.panel.Panel', {
			width : this.imageSize,
			height : this.imageSize,
			padding : 7,
			id : 'floating-panel' + record.data.id,
			frame : true,
			floating : true,
			shadow : true,
			hidden : true,
			html : '<img id="' + id + '" width="' + realSize + 'px" height="' + realSize + 'px" src="' + item.firstChild.firstChild.src + '">',
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
		p.toBack();
		//pos = this.qGrids[0].getPosition(true);
		Ext.create('Ext.fx.Anim', {
			target : p,
			duration : duration,
			from : {
				top : top,
				left : left,
				width : this.imageSize,
				height : this.imageSize
			},
			to : {
				top : this.center[1],
				left : this.center[0],
				width : this.imageSize,
				height : this.imageSize
			},
		});
	},
	createIterateMenu : function(canvas) {
		ctx = canvas.getContext('2d');
		ctx.globalCompositeOperation = 'source-over';
		//outer
		ctx.beginPath();
		ctx.fillStyle = "rgba(0, 255, 0, 0.15)";
		ctx.arc(20, 20, 15, 0, 2 * Math.PI, false);
		ctx.fill();
		ctx.closePath();
		//inner
		ctx.beginPath();
		ctx.fillStyle = "rgba(255, 0, 0, 0.12)";
		ctx.arc(55, 20, 15, 0, 2 * Math.PI, false);
		//ctx.fill();
		ctx.closePath();
	},
	createAxisMenu : function(canvas) {

	},
	createExploreMenu : function(canvas) {
		ctx = canvas.getContext('2d');
		ctx.globalCompositeOperation = 'source-over';
		//outer
		ctx.beginPath();
		ctx.fillStyle = "rgba(255, 165, 0, 0.15)";
		ctx.arc(90, 90, 70, 0, 2 * Math.PI, false);
		ctx.fill();
		ctx.closePath();
		//inner
		ctx.beginPath();
		ctx.fillStyle = "rgba(255, 0, 0, 0.12)";
		ctx.arc(90, 90, 30, 0, 2 * Math.PI, false);
		ctx.fill();
		ctx.closePath();
	},
	exploreMenuClick : function(el, evt) {
		var p1 = Ext.fly(el).getXY();
		var p2 = evt.getXY();
		var x = (p2[0] - p1[0]);
		var y = (p2[1] - p1[1]);
		var r = (Math.sqrt(Math.pow(x - 90, 2) + Math.pow(y - 90, 2)));

		var distance = 'medium';
		if(r <= 30)
			distance = 'near';

		this.onItemClick(null, this.currRec, this.curItem, distance, 'linear', 'explore');
	},
	iterateMenuClick : function(el, evt) {
		var p1 = Ext.fly(el).getXY();
		var p2 = evt.getXY();
		var x = (p2[0] - p1[0]);
		var y = (p2[1] - p1[1]);
		var r = (Math.sqrt(Math.pow(x - 20, 2) + Math.pow(y - 20, 2)));
		var iterate_type = 'linear'
		if(r <= 15)
			iterate_type = 'random';

		this.onItemClick(null, this.currRec, this.curItem, 'medium', iterate_type, 'iterate');
	},
	axisMenuClick : function(el, evt) {
		this.onItemClick(null, this.currRec, this.curItem, 'medium', 'linear', 'axis');
	},
	addProductVariant : function(rec) {
		//this.qOpenDialog();
		Ext.Ajax.request({
			url : '/explorer/add_product_variant',
			params : {
				item_uuid : rec.data.id
			},
			success : function(response) {
				window.location = '/product/' + rec.data.id
			}
		});

	},
	showMessage : function(message) {
		console.log(this.center);
		pos = this.getExplorerPanel().getPosition();
		this.getMessagePanel().setPosition(pos[0] + 20, pos[1] - 25);
		this.getMessagePanel().show();
		this.getMessagePanel().toFront();

	}
	/*destroy: function() {
	 this.callParent();
	 },*/
});
