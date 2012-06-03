Ext.onReady(function(){   
	var container = document.getElementById('explorer-container');
	var panel = Ext.create('Quest.view.Panel',{
		width: 605,
		frame:false,
		border:false
	});
	panel.render(container);
});
