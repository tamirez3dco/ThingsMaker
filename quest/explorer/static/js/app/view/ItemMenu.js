Ext.define('Quest.view.ItemMenu', {
	extend : 'Ext.panel.Panel',
	id : 'explorer-item-menu',
	border : false,
	padding : 7,
	frame : false,
	floating : true,
	shadow : false,
	width: 200,
	height: 200,
	bodyStyle : 'background:transparent;',
	hidden : true,
	html: '<canvas class="item-menu-canvas" id="item-menu-explore"></canvas>' +
	'<canvas class="item-menu-canvas" id="item-menu-iterate"></canvas>' +  
	'<canvas class="item-menu-canvas" id="item-menu-axis"></canvas>' +  
	'<div class="item-menu-buttons" id="item-menu-buttons">' + 
	'<button id="makeit-button" style="position: absolute; width: 76px; left: -11px; top: -3px;" >Make It!</button></div>',
	afterRender : function() {
		this.callParent();
		
	},
});
