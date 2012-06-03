/*
Copyright(c) 2012 EZ3D
*/
Ext.define('Quest.model.Item', {
	extend: 'Ext.data.Model',
	fields: [{
		type: 'string',
		name: 'id'
	},{
		type: 'string',
		name: 'image_url'
	},{
		type: 'float',
		name: 'price',
	},{
		type: 'string',
		name: 'index'
	}],
	idProperty: 'id'
});
Ext.define('Quest.store.Items', {
	extend : 'Ext.data.Store',
	model : 'Quest.model.Item',
	sorters : [{
		property : 'id',
		direction : 'DESC'
	}],

	autoLoad : false,
	
	proxy: {
        type: 'jsonp',
        url : 'http://growing-ice-2442.herokuapp.com/explorer',
        //url : 'http://127.0.0.1:8000/explorer',
        timeout: 60000,
        callbackKey: 'callback',
        reader: {
            type: 'json',
            root: 'items'
        }
  },
  listeners: {
  	load: function(){
  		console.log('loaded');
  		if (this.definitionId != null) {
  			console.log(this.definitionId);
  			var page = '/quest/' + this.definitionId
  			if (this.itemId != null) {
  				page += '/' + this.itemId
  			}
  			_gaq.push(['_trackPageview', page]);
  			
  		}
  	}
  }
});
Ext.define('Quest.view.ImageGrid', {
	extend : 'Ext.view.View',
	alias : 'widget.quest-imagegrid',
	border : 4,
	frame : false,
	hideHeaders : true,
	padding : 8,
	id : 'quest-explorer-imagegrid',
	tpl : ['<tpl for=".">', '<div class="thumb-wrap" id="{id}">', '<div class="thumb"><img src="{image_url}" title="{index}"></div>', '<span class="x-editable"></span></div>', '</tpl>', '<div class="x-clear"></div>'],
	//tpl : ['<tpl for=".">', '<div class="thumb-wrap" id="{id}">', '<div class="thumb"><img src="{url}" title="{id}"></div>', '<span class="x-editable">{id}</span></div>', '</tpl>', '<div class="x-clear"></div>'],
	multiSelect : true,
	//height: 310,
	trackOver : true,
	overItemCls : 'x-item-over',
	itemSelector : 'div.thumb-wrap',
	emptyText : 'No images to display',
	itemsType : 'definition',
	prepareData : function(data) {
		//data.url = 'http://ec2-184-73-9-184.compute-1.amazonaws.com/testim/yofi_' + data.index + '.jpg';
		return data;
	},
	listeners : {
		viewready : function() {
			//console.log('viewready');
		},
		itemClick : function(view, record, item) {
			if(this.itemsType == 'definition') {
				this.itemsType='model'
				this.store.definitionId = record.data.id
				this.store.load({
					params : {
						definition_id : record.data.id
					}
				});
			} else {
				this.store.itemId = record.data.id
				this.store.load({
					params : {
						item_id : record.data.id
					}
				});
			}
			console.log('click');
		}
	}

});

Ext.onReady(function(){
	var store = Ext.create('Quest.store.Items');
	var grid = Ext.create('Quest.view.ImageGrid',{store: store, height: 640});
	var container = document.getElementById('explorer-container');
	var panel = Ext.create('Ext.panel.Panel',{
		width: 630,
		frame:false,
		border:false,
		items: [grid]
	});
	panel.render(container);
	store.load({params:{show_definitions: true}});
});



