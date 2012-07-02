Ext.define('Quest.view.MessagePanel', {
	extend : 'Ext.panel.Panel',
	id : 'explorer-message-panel',
	border : false,
	padding : 7,
	frame : false,
	floating : true,
	shadow : false,
	width: 500,
	height: 100,
	//z-index: 1000,
	bodyStyle : 'background:transparent; font-size: 20px;',
	hidden : true,
	html: '<div style="float: left;">Creating new models based on your selection..</div><img style="width: 20px; height: 20px; float: right;" src="/static/images/large-loading.gif"></img>',
	afterRender : function() {
		this.callParent();
		
	},
});
