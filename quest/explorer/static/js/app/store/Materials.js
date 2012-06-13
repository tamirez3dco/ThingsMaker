Ext.define('EZ3D_store.store.Materials', {
	extend : 'Ext.data.Store',
	model : 'EZ3D_store.model.Material',
	proxy : {
		type : 'direct',
		directFn : django.material.material_list,
		pageParam : undefined,
		reader : {
			idProperty : 'name',
			root : 'records',
			type : 'json'
		}
	}
});
