/*
Copyright(c) 2012 EZ3D
*/
Ext.define("Quest.model.Item",{extend:"Ext.data.Model",fields:[{type:"string",name:"id"},{type:"string",name:"image_url"},{type:"float",name:"price",},{type:"string",name:"index"}],idProperty:"id"});Ext.define("Quest.store.Items",{extend:"Ext.data.Store",model:"Quest.model.Item",sorters:[{property:"id",direction:"DESC"}],autoLoad:false,proxy:{type:"jsonp",url:"http://growing-ice-2442.herokuapp.com/explorer",timeout:60000,callbackKey:"callback",reader:{type:"json",root:"items"}},listeners:{load:function(){console.log("loaded");if(this.definitionId!=null){console.log(this.definitionId);var a="/quest/"+this.definitionId;if(this.itemId!=null){a+="/"+this.itemId}_gaq.push(["_trackPageview",a])}}}});Ext.define("Quest.view.ImageGrid",{extend:"Ext.view.View",alias:"widget.quest-imagegrid",border:4,frame:false,hideHeaders:true,padding:8,id:"quest-explorer-imagegrid",tpl:['<tpl for=".">','<div class="thumb-wrap" id="{id}">','<div class="thumb"><img src="{image_url}" title="{index}"></div>','<span class="x-editable"></span></div>',"</tpl>",'<div class="x-clear"></div>'],multiSelect:true,trackOver:true,overItemCls:"x-item-over",itemSelector:"div.thumb-wrap",emptyText:"No images to display",itemsType:"definition",prepareData:function(a){return a},listeners:{viewready:function(){},itemClick:function(b,a,c){if(this.itemsType=="definition"){this.itemsType="model";this.store.definitionId=a.data.id;this.store.load({params:{definition_id:a.data.id}})}else{this.store.itemId=a.data.id;this.store.load({params:{item_id:a.data.id}})}console.log("click")}}});Ext.onReady(function(){var c=Ext.create("Quest.store.Items");var d=Ext.create("Quest.view.ImageGrid",{store:c,height:640});var b=document.getElementById("explorer-container");var a=Ext.create("Ext.panel.Panel",{width:630,frame:false,border:false,items:[d]});a.render(b);c.load({params:{show_definitions:true}})});
