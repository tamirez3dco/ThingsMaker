Ext.onReady(function() {
	var materials = Ext.create('Quest.store.Materials', {});
	var algos = Ext.create('Quest.store.Algos', {});
	var container = document.getElementById('explorer-container');
	var image_panel = Ext.create('Quest.view.Panel', {
		width : 605,
		frame : false,
		border : false
	});

	var control_panel = Ext.create('Quest.view.ExplorerMenu', {
		width : 120,
		frame : false,
		border : false
	});

	var panel = Ext.create('Ext.panel.Panel', {
		layout : 'hbox',
		border : false,
		items : [image_panel, control_panel]
	});

	var item_menu = Ext.create('Quest.view.ItemMenu', {});

	controller = Ext.create('Quest.Controller', {});
	controller.init();

	panel.render(container);
	item_menu.render(container);
});
