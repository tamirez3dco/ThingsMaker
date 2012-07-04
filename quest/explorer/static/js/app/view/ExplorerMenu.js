Ext.define('Quest.view.ExplorerMenu', {
	extend : 'Ext.panel.Panel',
	width : 120,
	//border: false,
	//frame: false,
	items : [{
		xtype : 'combo',
		store : 'Materials',
		id : 'materialCombo',
		fieldLabel : 'Material',
		labelAlign : 'top',
		queryMode : 'local',
		displayField : 'name',
		value : "Gold",
		width: 100,
	},{
		xtype : 'combo',
		store : 'Algos',
		id : 'algoCombo',
		fieldLabel : 'Algo',
		labelAlign : 'top',
		queryMode : 'local',
		displayField : 'name',
		value : "Explore",
		width: 100,
	},{
		xtype: 'textfield',
		fieldLabel : 'Text',
		id: 'explorer-text',
		labelAlign : 'top',
		width: 100
	}]
});
