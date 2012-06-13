Ext.onReady(function(){   
	var container = document.getElementById('explorer-container');
	var image_panel = Ext.create('Quest.view.Panel',{
		width: 605,
		frame:false,
		border:false
	});
	
	var control_panel = Ext.create('Quest.view.ExplorerMenu',{
		width: 180,
		frame:false,
		border:false
	});
		
	var panel = Ext.create('Ext.panel.Panel',{
		layout: 'hbox',
		border: false,
		items: [image_panel, control_panel]
	});
	panel.render(container);
});
