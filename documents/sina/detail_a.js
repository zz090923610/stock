if (typeof $ == "undefined") {
	$ = function(A) {
		return document.getElementById(A)
	}
}
if (typeof $C == "undefined") {
	$C = function(A) {
		return document.createElement(A)
	}
}
Function.prototype.Bind = function() {
	var D = this, B = arguments[0], A = new Array();
	for ( var C = 1; C < arguments.length; C++) {
		A.push(arguments[C])
	}
	return function() {
		var F = [];
		for ( var E = 0; E < arguments.length; E++) {
			F.push(arguments[E])
		}
		return D.apply(B, F.concat(A))
	}
};
Function.prototype._Bind = function() {
	var D = this, B = arguments[0], A = new Array();
	for ( var C = 1; C < arguments.length; C++) {
		A.push(arguments[C])
	}
	return function() {
		return D.apply(B, A)
	}
};
Function.prototype.BindForEvent = function() {
	var D = this, B = arguments[0], A = new Array();
	for ( var C = 1; C < arguments.length; C++) {
		A.push(arguments[C])
	}
	return function(E) {
		return D.apply(B, [ (E || window.event) ].concat(A))
	}
};
var TblCtrl = {
	_lastVolume : null,
	Init : function() {
		var A = window.frames.list_frame ? window.frames.list_frame : window;
		this.oTbody = A.document.getElementById("datatbl").tBodies[0]
	},
	add : function(D) {
		if (!this._lastVolume) {
			this._setLast(D);
			if (window.lastTradeTime) {
				this._timeend = parseInt(window.lastTradeTime.replace(/:/g, ""));
				var A = parseInt(D.time.replace(/:/g, ""));
				if (A < this._timeend) {
					this._lastVolume = null
				}
			}
			return
		} else {
			if ((D.volume - this._lastVolume).toFixed(0) != 0) {
				var C = D.price >= this._lastSellone ? "<h5>买盘</h5>"
						: (D.price <= this._lastBuyone ? "<h6>卖盘</h6>" : "中性");
				var B = D.price - this._lastPrice == 0 ? "--"
						: (D.price - this._lastPrice).toFixed(2);
				this.insert([ D.time, D.price, D.chgRate, B,
						(D.volume - this._lastVolume).toFixed(0),
						(D.turnover - this._lastTurnover).toFixed(0), C ]);
				this._setLast(D)
			}
		}
	},
	_setLast : function(A) {
		this._lastVolume = A.volume;
		this._lastPrice = A.price;
		this._lastTurnover = A.turnover;
		this._lastBuyone = A.buyoneP;
		this._lastSellone = A.selloneP
	},
	insert : function(B) {
		this.aData = B;
		var D = this.oTbody.insertRow(0);
		for ( var C = 0; C < this.aData.length; C++) {
			var A = (C != 0 && C != 6) ? $C("TD") : $C("TH");
			A.innerHTML = B[C];
			D.appendChild(A)
		}
		this._blink(D, 0);
		this._remove()
	},
	_remove : function() {
		var A = this.oTbody.rows.length - 1;
		this.oTbody.removeChild(this.oTbody.rows[A])
	},
	_blink : function(B, A) {
		if (typeof A == "undefined") {
			A = 0
		}
		if (A % 2 == 0) {
			B.className = "highlight"
		} else {
			B.className = ""
		}
		if (A == 3) {
			this._setTrColor(B);
			return
		}
		A++;
		window.setTimeout(this._blink._Bind(this, B, A), 300)
	},
	_setTrColor : function(B) {
		var A = this.aData[5];
		if (A >= 100000) {
			B.className = A < 1000000 ? "medium" : "huge"
		}
	}
};
var HqCtrl = {
	_data : {},
	Init : function() {
		var A = window["hq_str_" + symbol].split(",");
		this._data = {
			name : A[0],
			code : symbol,
			date : A[30],
			time : A[31],
			price : A[3],
			change : (A[3] * 1 - A[2] * 1).toFixed(2).replace(/^([^-])/, "+$1"),
			chgRate : ((A[3] * 1 - A[2] * 1) * 100 / (A[2] * 1)).toFixed(2)
					.replace(/^([^-])/, "+$1")
					+ "%",
			redOrGreen : (A[3] * 1 - A[2] * 1 > 0 ? "#F00" : (A[3] * 1 - A[2]
					* 1 < 0 ? "#080" : "#000")),
			last : A[2],
			open : A[1],
			high : A[4],
			low : A[5],
			turnover : A[9],
			volume : (A[8] * 1 / 100).toFixed(0),
			buy : A[6],
			sell : A[7],
			buyoneM : (A[10] * 1 / 100).toFixed(0),
			buyoneP : A[11],
			selloneM : (A[20] * 1 / 100).toFixed(0),
			selloneP : A[21]
		};
		this._update();
		if (window.lastTradeTime) {
			TblCtrl.add(this._data)
		}
	},
    socketInit:function (data) {
        var A = data[symbol].split(",");
        this._data = {
			name : A[0],
			code : symbol,
			date : A[30],
			time : A[31],
			price : A[3],
			change : (A[3] * 1 - A[2] * 1).toFixed(2).replace(/^([^-])/, "+$1"),
			chgRate : ((A[3] * 1 - A[2] * 1) * 100 / (A[2] * 1)).toFixed(2)
					.replace(/^([^-])/, "+$1")
					+ "%",
			redOrGreen : (A[3] * 1 - A[2] * 1 > 0 ? "#F00" : (A[3] * 1 - A[2]
					* 1 < 0 ? "#080" : "#000")),
			last : A[2],
			open : A[1],
			high : A[4],
			low : A[5],
			turnover : A[9],
			volume : (A[8] * 1 / 100).toFixed(0),
			buy : A[6],
			sell : A[7],
			buyoneM : (A[10] * 1 / 100).toFixed(0),
			buyoneP : A[11],
			selloneM : (A[20] * 1 / 100).toFixed(0),
			selloneP : A[21]
		};
		this._update();
		if (window.lastTradeTime) {
			TblCtrl.add(this._data)
		}
    },
	_update : function() {
		var A = this._html;
		for ( var B in this._data) {
			A = A.replace(new RegExp(B, ""), this._data[B]);
			if (B == "code") {
				A = A.replace(new RegExp(B, ""), this._data[B])
			}
		}
		//$("quote_area").innerHTML = A
	},
	_html : '<table class="head"><tbody><tr><th><h1><a href="http://biz.finance.sina.com.cn/suggest/lookup_n.php?country=stock&q=code" target="_blank">name</a></h1>code</th><td>date time</td></tr></tbody></table> <table><tbody> <tr><th rowspan="3"><h5 style="color:redOrGreen;">price</h5>change (chgRate)</th><td>昨收盘:last</td><td>今开盘:open</td><td>最高价:high</td><td>最低价:low</td></tr> <tr><td>成交额:turnover</td><td>成交量:volume</td><td>买入价:buy</td><td>卖出价:sell</td></tr> <tr><td>买一量:buyoneM</td><td>买一价:buyoneP</td><td>卖一量:selloneM</td><td>卖一价:selloneP</td></tr> </tbody></table>'
};
function loadScript(A, D, B) {
	var C = document.createElement("script");
	C.type = "text/javascript";
	C.charset = "gb2312";
	C.src = A.replace("@RANDOM@", (new Date()).getTime());
	C.callback = D;
	C.value = B;
	C[document.all ? "onreadystatechange" : "onload"] = function() {
		if (document.all && this.readyState != "loaded"
				&& this.readyState != "complete") {
			return
		}
		this.callback(B);
		this[document.all ? "onreadystatechange" : "onload"] = null;
		this.value = null;
		this.parentNode.removeChild(this)
	};
	$("ScriptLoader").appendChild(C)
}
var __page_url_ori = "http://vip.stock.finance.sina.com.cn/quotes_service/view/vMS_tradedetail.php?symbol="
		+ symbol + "&date=@DATE@&page=";
var __iframe_url_ori = "http://market.finance.sina.com.cn/transHis.php?symbol="
		+ symbol + "&date=@DATE@&page=";
Ruler = function() {
	this.init.apply(this, arguments)
};
Ruler.prototype = {
	_IOSrv : new IO.SRV("/quotes_service/api/json_v2.php"),
	init : function() {
		this._IOSrv.Call("CN_Transactions.getAllPageTime", this.repaintRuler
				.Bind(this), {
			date : pageDate,
			symbol : symbol
		}, "GET");
		window.setTimeout(this.init.Bind(this), 60000)
	},
	repaintRuler : function(J) {
		window.__page_url = __page_url_ori.replace("@DATE@", window.pageDate);
		window.__container = window;
		var F = J.detailPages;
		var D = F[0].end_ts.split(":");
		var K = (D[0] * 1 > 12 ? 319 : 0)
				+ (D[0] * 60 + D[1] * 1 - (D[0] * 1 > 12 ? 780 : 570)) / 120
				* 310;
		var G = Math.floor(K / F.length);
		var B = __container.delistQuarter;
		var I = 50;
		var A = I * B;
		var G = Math.floor((K - A) / F.length);
		var L = '<div class="today">当日时间线→</div><div style="width:650px" class="ruler"><div style="width:620px" class="linbox"><div class="blueline" style="width:'
				+ (K - 7)
				+ 'px;">'
				+ F[0].end_ts.replace(/^(\d{2}:\d{2}):\d{2}$/, "$1")
				+ '</div></div><div class="underline" style="overflow:hidden;"><div  style="width:10px;" class="line"></div><div class="line"></div><div class="line"></div><div class="line"></div></div><div class="times"><div class="timeA" id="time_0930">9:30</div><div style="width:110px;"></div><div class="time" id="time_1030">10:30</div><div style="width:95px;"></div><div class="time" id="time_1130">11:30</div><div style="width:10px;"></div><div class="time" id="time_1300">13:00</div><div style="width:95px;"></div><div class="time" id="time_1400">14:00</div><div style="width:110px;"></div><div class="time" id="time_1500">15:00</div></div></div>';
		L += '<div class="pages">';
		L += "<div class='delist' style='position:relative;top:7px;height:9px;float:left;width:"
				+ A + "px;background:#ECA16A;'></div>";
		var C = 0;
		for ( var H = F.length - 1; H > -1; H--) {
			var E = H == 0 ? K - C - A : G;
			if (F[H].page == __container.currentPage) {
				L += '<div class="on" id="currentPageTime" style="width:' + E
						+ 'px;"><div class="time" style="left:'
						+ ((G - 120) / 2) + 'px;">'
						+ F[H].begin_ts.replace(/^(\d{2}:\d{2}):\d{2}$/, "$1")
						+ " - "
						+ F[H].end_ts.replace(/^(\d{2}:\d{2}):\d{2}$/, "$1")
						+ '</div><a class="space" href="' + window.__page_url
						+ F[H].page + '" title="点击查看成交明细"></a></div>'
			} else {
				L += '<div class="off" style="width:'
						+ E
						+ "px;\" onmouseover=\"this.className='on';$('currentPageTime').className = 'off';\" onmouseout=\"this.className='off';$('currentPageTime').className = 'on';\"><div class=\"time\" style=\"left:"
						+ ((G - 120) / 2) + 'px;">'
						+ F[H].begin_ts.replace(/^(\d{2}:\d{2}):\d{2}$/, "$1")
						+ " - "
						+ F[H].end_ts.replace(/^(\d{2}:\d{2}):\d{2}$/, "$1")
						+ '</div><a class="space" href="' + window.__page_url
						+ F[H].page + '" title="点击查看成交明细"></a></div>'
			}
			C += G
		}
		__container.document.getElementById("ruler").innerHTML = L + "</div>";
		__container.document.getElementById("time_1030").className = K > 198 ? "timeA"
				: "time";
		__container.document.getElementById("time_1130").className = K > 397 ? "timeA"
				: "time";
		__container.document.getElementById("time_1300").className = K > 398 ? "timeA"
				: "time";
		__container.document.getElementById("time_1400").className = K > 597 ? "timeA"
				: "time";
		__container.document.getElementById("time_1500").className = K == 797 ? "timeA"
				: "time"
	}
};

function main() {
	if (window.lastTradeTime) {
		TblCtrl.Init()
	}
    if (!window.IO || !window.IO.WebPush4) {
        hqCtrl();
    	window.setInterval(hqCtrl, 5000);
    }else {
        loadSocket(HqCtrl.socketInit.Bind(HqCtrl))
    }

	var A = new Ruler()
}
function hqCtrl() {
	if (window.refreshCtrl) {
		loadScript("http://hq.sinajs.cn/rn=@RANDOM@&list=" + symbol,
				HqCtrl.Init.Bind(HqCtrl))
	}
};
// 添加websocket
function loadSocket(callback){
    var _this = this;
    // 启用websocket组件
    var hqWebsockt = new IO.WebPush4('hq.sinajs.cn', symbol, function(data) {
        if (typeof callback === "function") {
            callback(data);
        }
    }, {
        interval: 3,
    });
}
