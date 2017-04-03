// XHR Connections Pool
if(typeof IO == 'undefined' )IO = {};
IO.Ajax = function(){
	this.Init.apply(this, arguments);
}; 

IO.Ajax.prototype = {
	_standbyXmlHttpArray : [],
	
	_pendingXmlHttpArray : [],
	Init : function(opts)
	{
    if(opts){
			if(opts.nopool)this._nopool = true;
		  if(opts.randomURL)this._randomURL = true;
		  if(opts.err_cb) this._err_cb = opts.err_cb;
		}
		
	},
	get : function(url, callback, options){
	  if(typeof options == 'undefined')options = {};
		options.method = 'GET';
	  this.request(url, callback, options);
	},
	post : function(url, callback, options){
	  if(typeof options == 'undefined')options = {};
		options.method = 'POST';
	  this.request(url, callback, options);
	},
	request : function(url, callback, options){
		var xhr = this.getXmlHttp();
		if(xhr){
			if(!options)options = {};
			if(!options.method)
				options.method = 'GET';
			this._opt = options;			
			this.registerXmlhttpCallback(xhr, callback);
			if(this._randomURL){
				var tok = (url.indexOf('?') == -1)?'?':'&';
				url += tok+ Math.round(Math.random() * 2147483648);
			}
			//	url += '?' + Math.round(Math.random() * 2147483648);
      //else
			//	url += '&' + Math.round(Math.random() * 2147483648);
				
		  xhr.open(options.method, url, true);
		  if( options.method = 'POST' ){
				xhr.setRequestHeader('Content-type',
        											'application/x-www-form-urlencoded');
        xhr.send(options.postBody);											
			}
			else xhr.send(null);
			
		}
		else{
		  if(this._err_cb) this._err_cb(2000)
		}	
	},
	registerXmlhttpCallback : function(xmlhttp, callback)
	{
		var c = this._pendingXmlHttpArray.length;
		this._pendingXmlHttpArray[c] = xmlhttp;
		xmlhttp.onreadystatechange = this._internalXmlhttpCallback(this, callback, c);
	},	
	getXmlHttp : function ()
	{
		if(this._nopool){
			return this._createXmlHttp();
		}
		var xmlhttp = this._standbyXmlHttpArray.pop();
		
		if (! xmlhttp) {
			xmlhttp = this._createXmlHttp();
		}
		
		setTimeout(this._supplyXmlHttp(this), this._standbyXmlHttpArray.length * 20);
		
		return xmlhttp;
	},
	_supplyXmlHttp : function(obj)
	{
		return function(){
			try {
				while (obj._standbyXmlHttpArray.length < 5) {
					obj._standbyXmlHttpArray.push(obj._createXmlHttp());
				}
			}
			catch (a) {}		
		}
	},		
	_createXmlHttp : function ()
	{
		var xmlhttp = null;
		var b = "Msxml2.XMLHTTP";
		try {
			xmlhttp = new ActiveXObject(b);
		}
		catch (c) {
			try{
				b = "Microsoft.XMLHTTP";
				xmlhttp = new ActiveXObject(b);						
			}
			catch (d){
			}
		}
		if(!xmlhttp){
			try{
			 xmlhttp = new XMLHttpRequest;
			
			}catch(e){
				
			}
		}
		return xmlhttp;
	},
	_internalXmlhttpCallback : function(obj, callback, index)
	{
		var a_cbable = false;
		return function()
		{
			var xmlhttp = obj._pendingXmlHttpArray[index];
			try {
				if(obj._opt.raw){
					a_cbable = true;
				}else{				  
					if (xmlhttp.readyState == 4 && xmlhttp.status==200){
						a_cbable = true;
					}
				}
			}
			catch (d) {
				if(obj._err_cb)obj._err_cb(d);
			}
			if( a_cbable )
				callback(xmlhttp);
			
			if (xmlhttp.readyState == 4) {
				setTimeout(function()
					{
						xmlhttp.onreadystatechange = obj._doNothing;
				    delete obj._pendingXmlHttpArray[index];
					}
				, 1000);
			}
		}
	},	
	_doNothing : function(){} 
} 


  
