// 基于IO.Ajax (IO.Script可选) 封装好的服务器端对应服务调用
if(typeof IO == 'undefined' )IO = {};
IO.SRV = function(){
	this.Init.apply(this, arguments);
}; 
/**
 * JSON格式传输数据
 * 接口调用模式
 * /path/to/api/gateway.php/srv.method
 * 
 * post参数为 json格式 key -> value 配对格式串
 *
 *
 */  
IO.SRV.prototype = {
  _xhr : null,
  _url : null,
  _cblist : [],
  _err_cb : null,
	Init : function(a_ServiceURL, a_ErrorCB, a_randomURL){
		var l_opt = {};
		if(a_randomURL)l_opt.randomURL = true;
		if(a_ErrorCB)l_opt.err_cb = a_ErrorCB;
		this._err_cb = a_ErrorCB;
		this._xhr = new IO.Ajax(l_opt);	
		this._url = a_ServiceURL;
	},
	Call : function(a_srvname, a_callback, a_arguments, req_sign){
		var l_callurl = this._url + '/' + a_srvname;
		var l_poststr = '';
		
    	var l_opt = {};
		if(typeof a_arguments == 'object')
		{
			for(var k in a_arguments)
			{
				var l_p = encodeURIComponent(a_arguments[k]);
				if(l_poststr == '')
				{
					l_poststr = k + '=' + l_p;
				}
				else
				{
					l_poststr += '&' + k + '=' + l_p;
				}
			}
			l_opt.postBody = l_poststr;
			//alert(req_sign + ' ' + l_poststr);
		}
		var l = this._cblist.length;
		this._cblist[l] = a_callback; 
		if (req_sign) {
			this._xhr.get(l_callurl + (l_poststr ? ("?" + l_poststr) : '') , this._StdCallBack(this, l));	
		} else {
			this._xhr.post(l_callurl , this._StdCallBack(this, l) , l_opt);	
		}
	},
	_StdCallBack : function(o, a_idx){
		return function(rtn){
			var l_cb = o._cblist[a_idx];
			delete o._cblist[a_idx];
			if(!rtn.responseText)
			{
			   if(l_cb)l_cb();
				 return;
			}
			
			try{
				eval("var v_l_data = " + rtn.responseText);
				
				/*
				 * var l_data = eval(rtn.responseText);
				 * 对于{t : "s"}这种JSON串会出错
				 */
			}
			catch(e){
				//throw e;
				o._err_cb(4000, rtn.responseText);
				return;
			}
			
			if(v_l_data && v_l_data.__ERROR ){
				  	o._err_cb(8001, v_l_data.__ERROR, v_l_data.__ERRORNO);
			}
			else/* if(v_l_data)*/
			{
				if(l_cb)l_cb(v_l_data, rtn.responseText);
			}
			/*else{
				o._err_cb(8000);
			}*/
		}
	}	
};
