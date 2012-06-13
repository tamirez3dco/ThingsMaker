Ext.define('EZ3D_store.model.Material', {
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