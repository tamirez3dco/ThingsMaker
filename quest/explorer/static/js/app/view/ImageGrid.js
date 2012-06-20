Ext.define('Quest.view.ImageGrid', {
	extend : 'Ext.view.View',
	alias : 'widget.quest-imagegrid',
	border : 4,
	frame : false,
	padding : 8,
	//id : 'quest-explorer-imagegrid',
	tpl : ['<tpl for=".">', '<div class="thumb-wrap" id="{tstid}">', '<div class="thumb small"><img id="img_{id}" src="{image_url}" title="{index}"></div>', '<span class="x-editable"></span></div>', '</tpl>', '<div class="x-clear"></div>'],
	trackOver : true,
	loadMask : false,
	overItemCls : 'x-item-over',
	itemSelector : 'div.thumb-wrap',
	emptyText : '',
	itemsType : 'definition',
	prepareData : function(data) {
		data.tstid = this.id + data.id;
		return data;
	}
});
