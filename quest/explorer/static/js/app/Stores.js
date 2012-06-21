Ext.define('Quest.store.Algos', {
	extend : 'Ext.data.Store',
	model : 'Quest.model.Algo',
	storeId: 'Algos',
	data : [{
		id : 1,
		name : "Iterate"
	},{
		id : 2,
		name : "Explore"
	},{
		id : 3,
		name : "Axis"
	}]
});
Ext.define('Quest.store.Materials', {
	extend : 'Ext.data.Store',
	model : 'Quest.model.Material',
	storeId: 'Materials',
	data : [{
		id : 1,
		name : "Gold"
	},{
		id : 2,
		name : "Silver"
	},{
		id : 3,
		name : "Plastic_Red"
	},{
		id : 4,
		name : "Plastic_Green"
	},{
		id : 4,
		name : "Clay"
	}]
});
Ext.define('Quest.store.Items', {
	extend : 'Ext.data.Store',
	model : 'Quest.model.Item',
	sorters : [{
		property : 'id',
		direction : 'ASC'
	}],

	autoLoad : false,
	
	proxy: {
        type: 'jsonp',
        url : 'http://' + Quest.config.site_domain + '/explore',
        timeout: 60000,
        callbackKey: 'callback',
        reader: {
            type: 'json',
            root: 'items'
        }
  },
  listeners: {
  	load: function(){
  		//console.log('loaded');
  		if (this.definitionId != null) {
  			console.log(this.definitionId);
  			var page = '/quest/' + this.definitionId
  			if (this.itemId != null) {
  				page += '/' + this.itemId
  			}
  			//_gaq.push(['_trackPageview', page]);
  			
  		}
  	}
  }
});
