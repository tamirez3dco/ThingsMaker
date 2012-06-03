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
        url : '/explorer',
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
  			_gaq.push(['_trackPageview', page]);
  			
  		}
  	}
  }
});
