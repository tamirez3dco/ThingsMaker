Ext.define('Quest.model.Algo', {
	extend: 'Ext.data.Model',
	fields: [{
		type: 'string',
		name: 'id'
	},{
		type: 'string',
		name: 'name'
	}],
	idProperty: 'id',
});
Ext.define('Quest.model.Material', {
	extend: 'Ext.data.Model',
	fields: [{
		type: 'string',
		name: 'id'
	},{
		type: 'string',
		name: 'name'
	},{
		type: 'number',
		name: 'price'
	}],
	idProperty: 'id',
});
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
	},{
		type: 'boolean',
		name: 'loaded',
		defaultValue: false
	},{
		type: 'boolean',
		name: 'shouldDisplay',
		defaultValue: false		
	},{
		type: 'boolean',
		name: 'displayed',
		defaultValue: false		
	}],
	idProperty: 'id'
});