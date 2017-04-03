var IO = IO || {};
!function() {
    function escapeRegExp(e) {
        return e.replace(/([.*+?^${}()|[\]\/\\])/g, "\\$1")
    }
    function JsLoadHqM(e) {
        function t() {
            function t() {
                if (0 === n && 0 === o)
                    l = r,
                    Cookie.set(h, "0", f);
                else {
                    if (1 !== n && 1 !== o)
                        return;
                    l = c;
                    var e = (0 !== n ? 1 : 0) + (0 !== o ? 2 : 0);
                    Cookie.set(h, e, f)
                }
                i()
            }
            Cookie.set(h, "-1", {
                domain: u,
                path: "/",
                expires: 10
            });
            var n = -1
              , o = -1;
            !function() {
                function i() {
                    getScript(a + "://" + e.host + "/list=sys_hqEtagMode", function() {
                        var e = window.hq_str_sys_hqEtagMode;
                        if (void 0 === o)
                            o = e;
                        else {
                            if (r++,
                            o == e && s++,
                            r >= d)
                                return n = s ? 1 : 0,
                                void t();
                            o = e
                        }
                        setTimeout(i, 2e3)
                    })
                }
                var o, s = 0, r = 0;
                i()
            }(),
            !function() {
                e.ssl ? (o = 0,
                t()) : getScript(a + "://" + e.host + "/list=sys_clientip,sys_serverip", function() {
                    var e = window.hq_str_sys_clientip
                      , n = window.hq_str_sys_serverip;
                    getScript([a, "://", n, "/?list=sys_clientip"].join(""), function() {
                        var n = window.hq_str_sys_clientip;
                        o = e == n ? 0 : 1,
                        t()
                    })
                })
            }()
        }
        function n() {
            var e = Cookie.get(h);
            switch (e) {
            case "0":
                l = r,
                i();
                break;
            case "1":
            case "2":
            case "3":
                l = c,
                i();
                break;
            case "-1":
                l = r;
                break;
            default:
                l = r,
                t()
            }
        }
        function i() {
            var e = Cookie.get(h);
            if (s !== e) {
                for (var t = 0, n = g.mode.length; n > t; t++)
                    g.mode[t](e);
                s = e
            }
        }
        function o(e, t, n) {
            n = n || {},
            getScript(l.replace("$rand", String((new Date).getTime())).replace("@type@", n.type ? "&format=" + n.type : "").replace("@others@", n.others ? n.others : "") + e, t, n.charset)
        }
        e = merge({
            ssl: !1,
            host: "hq.sinajs.cn"
        }, e || {}),
        _sslM.get() && (e.ssl = !0);
        var s, a = e.ssl ? "https" : "http", r = a + "://" + e.host + "/etag.php?rn=$rand@type@@others@&list=".replace("$rand", String((new Date).getTime())), c = a + "://" + e.host + "/?rn=$rand@type@@others@&list=", l = "", h = "hqEtagMode", u = "", f = {
            domain: u,
            path: "/",
            expires: 600
        }, d = 2, g = {
            mode: []
        };
        return o.addEventListener = function(e, t) {
            var n = g[e];
            n || (n = g[e] = []),
            n.push(t),
            void 0 !== s && t(s)
        }
        ,
        n(),
        setInterval(n, 1e3),
        o
    }
    function checkNative() {
        return "function" != typeof WebSocket && "object" != typeof WebSocket || WebSocket.isNotNative || /version\/5[\s\S]*safari/i.test(navigator.userAgent) ? !1 : !0
    }
    function AuthMgr(e) {
        function t(t) {
            a.ondebug("loading token from server...");
            var n = "https://current.sina.com.cn/auth/api/jsonp.php/$cb/AuthSign_Service.getSignCode?query=$type&ip=$ip&_=$rn&list=$list";
            e.cfg.isKick && (n += "&kick=1",
            e.cfg.isKick = !1),
            t && (n += "&s=1");
            var i = a.authtype || ""
              , o = "KKE_auth_" + genRandomStr()
              , r = "var%20" + o + "=";
            getScript(n.replace("$ip", s).replace("$type", i).replace("$cb", r).replace("$rn", String(Math.random())).replace("$list", c), function() {
                var e = window[o];
                window[o] = null,
                E(e)
            }, E)
        }
        function n(e) {
            a.ondebug("loading ipaddr...");
            var n = "sys_clientip"
              , i = ["http", a.ssl ? "s" : "", "://", r, "/?_=$rn&list=$symbol"].join("");
            getScript(i.replace("$rn", String((new Date).getTime())).replace("$symbol", n), function() {
                s = window["hq_str_" + n],
                t(e)
            })
        }
        var i, o, s, a = e.cfg, r = e.host, c = e.list, l = void 0, h = "KKE_TOKEN$", u = h + (a.authtype || ""), f = "|KKE|", d = 18e4, g = 1, p = -7, v = -9, m = !1, y = 0, b = 0, _ = function() {
            clearInterval(o)
        }, S = function(t) {
            m = !0,
            isFunc(i) && (i.apply(e),
            i = null),
            e.setReTimeout(t)
        }, w = function(t) {
            m = !1,
            e.close(),
            _(),
            a.onerr(t),
            a.ondebug("exception occurred while authoring:" + t.result)
        }, k = function(e) {
            l = e;
            var t = [l, "x"].join(f);
            if (a.ondebug("got new token"),
            hasLs)
                try {
                    localStorage.setItem(u, t)
                } catch (n) {
                    localStorage.removeItem(u),
                    localStorage.setItem(u, t)
                }
        }, C = function(e) {
            var t = null;
            if (e) {
                var n = e.split(f)
                  , i = n[0]
                  , o = 1 * n[1];
                if (a.ondebug("checking local token time:" + o),
                !i || i.length < 9 || isNaN(o))
                    a.ondebug("unexpected local token");
                else {
                    var s = (new Date).getTime() - o;
                    d > s ? t = {
                        token: i,
                        timeout: d - s
                    } : a.ondebug("local token is expired")
                }
            } else
                a.ondebug("local token does not exist");
            return t
        }, E = function(e) {
            if (!e && ++y < 3)
                return a.ondebug("error from php, retry..." + y),
                void n();
            e = e || {};
            var t = e.msg_code || 0
              , i = e.result || null
              , o = e.timeout || 0 / 0;
            t == g && i && !isNaN(o) ? (k(i),
            S(1e3 * o),
            a.onToken(t),
            y = 0,
            b = 0) : t == p && ++b < 2 ? (a.ondebug("php -7:nil cookie" + b),
            n()) : t == v ? (a.ondebug("php -9:simultaneous"),
            n(!0)) : w(e)
        }, I = function() {
            a.ondebug("checking local token...");
            var e;
            hasLs && (e = C(localStorage.getItem(u) || null)),
            e ? (a.ondebug("use local token"),
            l = e.token,
            S(e.timeout)) : n()
        };
        this.stop = _,
        this.getToken = function() {
            return l
        }
        ,
        this.auth = function(o) {
            a.authtype && (o = merge({
                forceOnline: !1,
                cb: null,
                noIp: !1
            }, o || {}),
            isFunc(o.cb) ? i = o.cb : !isFunc(i) && (i = e.init),
            o.forceOnline ? o.noIp && s ? (a.ondebug("existing client ip:" + s),
            t()) : n() : I(),
            _())
        }
    }
    function log(e) {
        window.console && window.console.log && console.log(e)
    }
    function addEvent(e, t, n) {
        e.addEventListener ? e.addEventListener(t, n, !1) : e.attachEvent("on" + t, n)
    }
    function getHashCode(e, t) {
        t || (e = e.toLowerCase());
        for (var n, i = 1315423911, o = e.length; o--; )
            n = e.charCodeAt(o),
            i ^= (i << 5) + n + (i >> 2);
        return 2147483647 & i
    }
    function merge(e, t) {
        for (var n in t)
            t.hasOwnProperty(n) && (e[n] = "object" == typeof e[n] && "object" == typeof t[n] ? arguments.callee(t[n], e[n]) : t[n]);
        return e
    }
    function fBind(e, t) {
        var n = Array.prototype.slice.call(arguments, 2);
        return function() {
            return e.apply(t, n.concat(Array.prototype.slice.call(arguments)))
        }
    }
    function fnBind(e, t, n) {
        return function() {
            if (n && arguments.length)
                for (var i = Array.prototype.slice.call(n, 0), o = 0; o < arguments.length; o++)
                    Array.prototype.push.call(i, arguments[o]);
            return e.apply(t || this, i || n || arguments)
        }
    }
    function getScript(e, t, n, i) {
        var o = document.createElement("script");
        o.type = "text/javascript",
        i && (o.charset = i),
        o.src = e;
        var s = document.getElementsByTagName("head")[0]
          , a = !1;
        o.onload = o.onreadystatechange = function() {
            a || this.readyState && "loaded" !== this.readyState && "complete" !== this.readyState || (a = !0,
            t && setTimeout(t, 1),
            o.onload = o.onreadystatechange = null,
            setTimeout(function() {
                s.removeChild(o)
            }, 1))
        }
        ,
        o.onerror = function() {
            o.onload = o.onreadystatechange = o.onerror = null,
            o.parentNode.removeChild(o),
            o = null,
            "function" == typeof n && n()
        }
        ,
        setTimeout(function() {
            s.appendChild(o)
        }, 1)
    }
    function isType(e) {
        return function(t) {
            return {}.toString.call(t) == "[object " + e + "]"
        }
    }
    function codeConvert(e) {
        for (var t = e.toString(16); t.length < 2; )
            t = "0" + t;
        return "%" + t
    }
    function genRandomStr(e) {
        e = e || 9;
        for (var t = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890", n = "", i = 0, o = t.length; e > i; i++)
            n += t.charAt(Math.floor(Math.random() * o));
        return n
    }
    var swfobject = function() {
        function e() {
            if (!P) {
                try {
                    var e = D.getElementsByTagName("body")[0].appendChild(v("span"));
                    e.parentNode.removeChild(e)
                } catch (t) {
                    return
                }
                P = !0;
                for (var n = $.length, i = 0; n > i; i++)
                    $[i]()
            }
        }
        function t(e) {
            P ? e() : $[$.length] = e
        }
        function n(e) {
            if (typeof x.addEventListener != T)
                x.addEventListener("load", e, !1);
            else if (typeof D.addEventListener != T)
                D.addEventListener("load", e, !1);
            else if (typeof x.attachEvent != T)
                m(x, "onload", e);
            else if ("function" == typeof x.onload) {
                var t = x.onload;
                x.onload = function() {
                    t(),
                    e()
                }
            } else
                x.onload = e
        }
        function i() {
            B ? o() : s()
        }
        function o() {
            var e = D.getElementsByTagName("body")[0]
              , t = v(W);
            t.setAttribute("type", A);
            var n = e.appendChild(t);
            if (n) {
                var i = 0;
                !function() {
                    if (typeof n.GetVariable != T) {
                        var o = n.GetVariable("$version");
                        o && (o = o.split(" ")[1].split(","),
                        H.pv = [parseInt(o[0], 10), parseInt(o[1], 10), parseInt(o[2], 10)])
                    } else if (10 > i)
                        return i++,
                        void setTimeout(arguments.callee, 10);
                    e.removeChild(t),
                    n = null,
                    s()
                }()
            } else
                s()
        }
        function s() {
            var e = R.length;
            if (e > 0)
                for (var t = 0; e > t; t++) {
                    var n = R[t].id
                      , i = R[t].callbackFn
                      , o = {
                        success: !1,
                        id: n
                    };
                    if (H.pv[0] > 0) {
                        var s = p(n);
                        if (s)
                            if (!y(R[t].swfVersion) || H.wk && H.wk < 312)
                                if (R[t].expressInstall && r()) {
                                    var h = {};
                                    h.data = R[t].expressInstall,
                                    h.width = s.getAttribute("width") || "0",
                                    h.height = s.getAttribute("height") || "0",
                                    s.getAttribute("class") && (h.styleclass = s.getAttribute("class")),
                                    s.getAttribute("align") && (h.align = s.getAttribute("align"));
                                    for (var u = {}, f = s.getElementsByTagName("param"), d = f.length, g = 0; d > g; g++)
                                        "movie" != f[g].getAttribute("name").toLowerCase() && (u[f[g].getAttribute("name")] = f[g].getAttribute("value"));
                                    c(h, u, n, i)
                                } else
                                    l(s),
                                    i && i(o);
                            else
                                _(n, !0),
                                i && (o.success = !0,
                                o.ref = a(n),
                                i(o))
                    } else if (_(n, !0),
                    i) {
                        var v = a(n);
                        v && typeof v.SetVariable != T && (o.success = !0,
                        o.ref = v),
                        i(o)
                    }
                }
        }
        function a(e) {
            var t = null
              , n = p(e);
            if (n && "OBJECT" == n.nodeName)
                if (typeof n.SetVariable != T)
                    t = n;
                else {
                    var i = n.getElementsByTagName(W)[0];
                    i && (t = i)
                }
            return t
        }
        function r() {
            return !J && y("6.0.65") && (H.win || H.mac) && !(H.wk && H.wk < 312)
        }
        function c(e, t, n, i) {
            J = !0,
            C = i || null,
            E = {
                success: !1,
                id: n
            };
            var o = p(n);
            if (o) {
                "OBJECT" == o.nodeName ? (w = h(o),
                k = null) : (w = o,
                k = n),
                e.id = F,
                (typeof e.width == T || !/%$/.test(e.width) && parseInt(e.width, 10) < 310) && (e.width = "310"),
                (typeof e.height == T || !/%$/.test(e.height) && parseInt(e.height, 10) < 137) && (e.height = "137"),
                D.title = D.title.slice(0, 47) + " - Flash Player Installation";
                var s = H.ie && H.win ? "ActiveX" : "PlugIn"
                  , a = "MMredirectURL=" + x.location.toString().replace(/&/g, "%26") + "&MMplayerType=" + s + "&MMdoctitle=" + D.title;
                if (typeof t.flashvars != T ? t.flashvars += "&" + a : t.flashvars = a,
                H.ie && H.win && 4 != o.readyState) {
                    var r = v("div");
                    n += "SWFObjectNew",
                    r.setAttribute("id", n),
                    o.parentNode.insertBefore(r, o),
                    o.style.display = "none",
                    function() {
                        4 == o.readyState ? o.parentNode.removeChild(o) : setTimeout(arguments.callee, 10)
                    }()
                }
                u(e, t, n)
            }
        }
        function l(e) {
            if (H.ie && H.win && 4 != e.readyState) {
                var t = v("div");
                e.parentNode.insertBefore(t, e),
                t.parentNode.replaceChild(h(e), t),
                e.style.display = "none",
                function() {
                    4 == e.readyState ? e.parentNode.removeChild(e) : setTimeout(arguments.callee, 10)
                }()
            } else
                e.parentNode.replaceChild(h(e), e)
        }
        function h(e) {
            var t = v("div");
            if (H.win && H.ie)
                t.innerHTML = e.innerHTML;
            else {
                var n = e.getElementsByTagName(W)[0];
                if (n) {
                    var i = n.childNodes;
                    if (i)
                        for (var o = i.length, s = 0; o > s; s++)
                            1 == i[s].nodeType && "PARAM" == i[s].nodeName || 8 == i[s].nodeType || t.appendChild(i[s].cloneNode(!0))
                }
            }
            return t
        }
        function u(e, t, n) {
            var i, o = p(n);
            if (H.wk && H.wk < 312)
                return i;
            if (o)
                if (typeof e.id == T && (e.id = n),
                H.ie && H.win) {
                    var s = "";
                    for (var a in e)
                        e[a] != Object.prototype[a] && ("data" == a.toLowerCase() ? t.movie = e[a] : "styleclass" == a.toLowerCase() ? s += ' class="' + e[a] + '"' : "classid" != a.toLowerCase() && (s += " " + a + '="' + e[a] + '"'));
                    var r = "";
                    for (var c in t)
                        t[c] != Object.prototype[c] && (r += '<param name="' + c + '" value="' + t[c] + '" />');
                    o.outerHTML = '<object classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000"' + s + ">" + r + "</object>",
                    K[K.length] = e.id,
                    i = p(e.id)
                } else {
                    var l = v(W);
                    l.setAttribute("type", A);
                    for (var h in e)
                        e[h] != Object.prototype[h] && ("styleclass" == h.toLowerCase() ? l.setAttribute("class", e[h]) : "classid" != h.toLowerCase() && l.setAttribute(h, e[h]));
                    for (var u in t)
                        t[u] != Object.prototype[u] && "movie" != u.toLowerCase() && f(l, u, t[u]);
                    o.parentNode.replaceChild(l, o),
                    i = l
                }
            return i
        }
        function f(e, t, n) {
            var i = v("param");
            i.setAttribute("name", t),
            i.setAttribute("value", n),
            e.appendChild(i)
        }
        function d(e) {
            var t = p(e);
            t && "OBJECT" == t.nodeName && (H.ie && H.win ? (t.style.display = "none",
            function() {
                4 == t.readyState ? g(e) : setTimeout(arguments.callee, 10)
            }()) : t.parentNode.removeChild(t))
        }
        function g(e) {
            var t = p(e);
            if (t) {
                for (var n in t)
                    "function" == typeof t[n] && (t[n] = null);
                t.parentNode.removeChild(t)
            }
        }
        function p(e) {
            var t = null;
            try {
                t = D.getElementById(e)
            } catch (n) {}
            return t
        }
        function v(e) {
            return D.createElement(e)
        }
        function m(e, t, n) {
            e.attachEvent(t, n),
            U[U.length] = [e, t, n]
        }
        function y(e) {
            var t = H.pv
              , n = e.split(".");
            return n[0] = parseInt(n[0], 10),
            n[1] = parseInt(n[1], 10) || 0,
            n[2] = parseInt(n[2], 10) || 0,
            t[0] > n[0] || t[0] == n[0] && t[1] > n[1] || t[0] == n[0] && t[1] == n[1] && t[2] >= n[2] ? !0 : !1
        }
        function b(e, t, n, i) {
            if (!H.ie || !H.mac) {
                var o = D.getElementsByTagName("head")[0];
                if (o) {
                    var s = n && "string" == typeof n ? n : "screen";
                    if (i && (I = null,
                    O = null),
                    !I || O != s) {
                        var a = v("style");
                        a.setAttribute("type", "text/css"),
                        a.setAttribute("media", s),
                        I = o.appendChild(a),
                        H.ie && H.win && typeof D.styleSheets != T && D.styleSheets.length > 0 && (I = D.styleSheets[D.styleSheets.length - 1]),
                        O = s
                    }
                    H.ie && H.win ? I && typeof I.addRule == W && I.addRule(e, t) : I && typeof D.createTextNode != T && I.appendChild(D.createTextNode(e + " {" + t + "}"))
                }
            }
        }
        function _(e, t) {
            if (V) {
                var n = t ? "visible" : "hidden";
                P && p(e) ? p(e).style.visibility = n : b("#" + e, "visibility:" + n)
            }
        }
        function S(e) {
            var t = /[\\\"<>\.;]/
              , n = null != t.exec(e);
            return n && typeof encodeURIComponent != T ? encodeURIComponent(e) : e
        }
        {
            var w, k, C, E, I, O, T = "undefined", W = "object", N = "Shockwave Flash", L = "ShockwaveFlash.ShockwaveFlash", A = "application/x-shockwave-flash", F = "SWFObjectExprInst", M = "onreadystatechange", x = window, D = document, j = navigator, B = !1, $ = [i], R = [], K = [], U = [], P = !1, J = !1, V = !0, H = function() {
                var e = typeof D.getElementById != T && typeof D.getElementsByTagName != T && typeof D.createElement != T
                  , t = j.userAgent.toLowerCase()
                  , n = j.platform.toLowerCase()
                  , i = /win/.test(n ? n : t)
                  , o = /mac/.test(n ? n : t)
                  , s = /webkit/.test(t) ? parseFloat(t.replace(/^.*webkit\/(\d+(\.\d+)?).*$/, "$1")) : !1
                  , a = !1
                  , r = [0, 0, 0]
                  , c = null;
                if (typeof j.plugins != T && typeof j.plugins[N] == W)
                    c = j.plugins[N].description,
                    !c || typeof j.mimeTypes != T && j.mimeTypes[A] && !j.mimeTypes[A].enabledPlugin || (B = !0,
                    a = !1,
                    c = c.replace(/^.*\s+(\S+\s+\S+$)/, "$1"),
                    r[0] = parseInt(c.replace(/^(.*)\..*$/, "$1"), 10),
                    r[1] = parseInt(c.replace(/^.*\.(.*)\s.*$/, "$1"), 10),
                    r[2] = /[a-zA-Z]/.test(c) ? parseInt(c.replace(/^.*[a-zA-Z]+(.*)$/, "$1"), 10) : 0);
                else if (typeof x.ActiveXObject != T)
                    try {
                        var l = new ActiveXObject(L);
                        l && (c = l.GetVariable("$version"),
                        c && (a = !0,
                        c = c.split(" ")[1].split(","),
                        r = [parseInt(c[0], 10), parseInt(c[1], 10), parseInt(c[2], 10)]))
                    } catch (h) {}
                return {
                    w3: e,
                    pv: r,
                    wk: s,
                    ie: a,
                    win: i,
                    mac: o
                }
            }();
            !function() {
                H.w3 && ((typeof D.readyState != T && "complete" == D.readyState || typeof D.readyState == T && (D.getElementsByTagName("body")[0] || D.body)) && e(),
                P || (typeof D.addEventListener != T && D.addEventListener("DOMContentLoaded", e, !1),
                H.ie && H.win && (D.attachEvent(M, function() {
                    "complete" == D.readyState && (D.detachEvent(M, arguments.callee),
                    e())
                }),
                x == top && !function() {
                    if (!P) {
                        try {
                            D.documentElement.doScroll("left")
                        } catch (t) {
                            return void setTimeout(arguments.callee, 0)
                        }
                        e()
                    }
                }()),
                H.wk && !function() {
                    return P ? void 0 : /loaded|complete/.test(D.readyState) ? void e() : void setTimeout(arguments.callee, 0)
                }(),
                n(e)))
            }(),
            function() {
                H.ie && H.win && window.attachEvent("onunload", function() {
                    for (var e = U.length, t = 0; e > t; t++)
                        U[t][0].detachEvent(U[t][1], U[t][2]);
                    for (var n = K.length, i = 0; n > i; i++)
                        d(K[i]);
                    for (var o in H)
                        H[o] = null;
                    H = null;
                    for (var s in swfobject)
                        swfobject[s] = null;
                    swfobject = null
                })
            }()
        }
        return {
            registerObject: function(e, t, n, i) {
                if (H.w3 && e && t) {
                    var o = {};
                    o.id = e,
                    o.swfVersion = t,
                    o.expressInstall = n,
                    o.callbackFn = i,
                    R[R.length] = o,
                    _(e, !1)
                } else
                    i && i({
                        success: !1,
                        id: e
                    })
            },
            getObjectById: function(e) {
                return H.w3 ? a(e) : void 0
            },
            embedSWF: function(e, n, i, o, s, a, l, h, f, d) {
                var g = {
                    success: !1,
                    id: n
                };
                H.w3 && !(H.wk && H.wk < 312) && e && n && i && o && s ? (_(n, !1),
                t(function() {
                    i += "",
                    o += "";
                    var t = {};
                    if (f && typeof f === W)
                        for (var p in f)
                            t[p] = f[p];
                    t.data = e,
                    t.width = i,
                    t.height = o;
                    var v = {};
                    if (h && typeof h === W)
                        for (var m in h)
                            v[m] = h[m];
                    if (l && typeof l === W)
                        for (var b in l)
                            typeof v.flashvars != T ? v.flashvars += "&" + b + "=" + l[b] : v.flashvars = b + "=" + l[b];
                    if (y(s)) {
                        var S = u(t, v, n);
                        t.id == n && _(n, !0),
                        g.success = !0,
                        g.ref = S
                    } else {
                        if (a && r())
                            return t.data = a,
                            void c(t, v, n, d);
                        _(n, !0)
                    }
                    d && d(g)
                })) : d && d(g)
            },
            switchOffAutoHideShow: function() {
                V = !1
            },
            ua: H,
            getFlashPlayerVersion: function() {
                return {
                    major: H.pv[0],
                    minor: H.pv[1],
                    release: H.pv[2]
                }
            },
            hasFlashPlayerVersion: y,
            createSWF: function(e, t, n) {
                return H.w3 ? u(e, t, n) : void 0
            },
            showExpressInstall: function(e, t, n, i) {
                H.w3 && r() && c(e, t, n, i)
            },
            removeSWF: function(e) {
                H.w3 && d(e)
            },
            createCSS: function(e, t, n, i) {
                H.w3 && b(e, t, n, i)
            },
            addDomLoadEvent: t,
            addLoadEvent: n,
            getQueryParamValue: function(e) {
                var t = D.location.search || D.location.hash;
                if (t) {
                    if (/\?/.test(t) && (t = t.split("?")[1]),
                    null == e)
                        return S(t);
                    for (var n = t.split("&"), i = 0; i < n.length; i++)
                        if (n[i].substring(0, n[i].indexOf("=")) == e)
                            return S(n[i].substring(n[i].indexOf("=") + 1))
                }
                return ""
            },
            expressInstallCallback: function() {
                if (J) {
                    var e = p(F);
                    e && w && (e.parentNode.replaceChild(w, e),
                    k && (_(k, !0),
                    H.ie && H.win && (w.style.display = "block")),
                    C && C(E)),
                    J = !1
                }
            }
        }
    }()
      , Cookie = {};
    Cookie.get = function(e) {
        var t = document.cookie.match("(?:^|;)\\s*" + escapeRegExp(e) + "=([^;]*)");
        return t ? t[1] || "" : ""
    }
    ,
    Cookie.set = function(e, t, n) {
        n = n || {},
        null === t && (t = "",
        n.expires = -1);
        var i = "";
        if (n.expires && (1 * n.expires || n.expires.toUTCString)) {
            var o;
            1 * n.expires ? (o = new Date,
            o.setTime(o.getTime() + 1e3 * n.expires)) : o = n.expires,
            i = "; expires=" + o.toUTCString()
        }
        var s = n.path ? "; path=" + n.path : ""
          , a = n.domain ? "; domain=" + n.domain : ""
          , r = n.secure ? "; secure" : "";
        document.cookie = [e, "=", t, i, s, a, r].join("")
    }
    ;
    var _sslM = new function() {
        var e = !1;
        0 == location.protocol.indexOf("https:") && (e = !0),
        this.SSL_SWF_URL = "https://current.sina.com.cn/theone/SwfWebSocket.swf",
        this.get = function() {
            return e
        }
    }
      , _PHP_UA_VAR = "httpheaderuavons"
      , __phpUA = void 0;
    WEB_SOCKET_SWF_LOCATION = window.WEB_SOCKET_SWF_LOCATION || "http://image2.sina.com.cn/woocall/swf/sina_financews_20150514c.swf",
    checkNative() || !function() {
        var e;
        return e = window.WEB_SOCKET_LOGGER ? WEB_SOCKET_LOGGER : window.console && window.console.log && window.console.error ? window.console : {
            log: function() {},
            error: function() {}
        },
        swfobject.getFlashPlayerVersion().major < 10 ? (e.error("Flash Player >= 10.0.0 is required."),
        window.WebSocket = window.WebSocket || {},
        window.WebSocket.canUse = !1,
        void (window.WebSocket.isNotNative = !0)) : ("file:" == location.protocol && e.error("WARNING: web-socket-js doesn't work in file:///... URL unless you set Flash Security Settings properly. Open the page via Web server i.e. http://..."),
        window.WebSocket = function(e, t, n, i, o) {
            var s = this;
            s.__id = WebSocket.__nextId++,
            WebSocket.__instances[s.__id] = s,
            s.readyState = WebSocket.CONNECTING,
            s.bufferedAmount = 0,
            s.__events = {},
            t ? "string" == typeof t && (t = [t]) : t = [],
            s.__createTask = setTimeout(function() {
                WebSocket.__addTask(function() {
                    s.__createTask = null,
                    WebSocket.__flash.create(s.__id, e, t, n || null, i || 0, o || null)
                })
            }, 0)
        }
        ,
        window.WebSocket.isNotNative = !0,
        WebSocket.prototype.send = function(e) {
            if (this.readyState == WebSocket.CONNECTING)
                throw "INVALID_STATE_ERR: Web Socket connection has not been established";
            var t = WebSocket.__flash.send(this.__id, encodeURIComponent(e));
            return 0 > t ? !0 : (this.bufferedAmount += t,
            !1)
        }
        ,
        WebSocket.prototype.initFlashLC = function(e, t) {
            WebSocket.__flash.init(e, t)
        }
        ,
        WebSocket.prototype.close = function() {
            return this.__createTask ? (clearTimeout(this.__createTask),
            this.__createTask = null,
            void (this.readyState = WebSocket.CLOSED)) : void (this.readyState != WebSocket.CLOSED && this.readyState != WebSocket.CLOSING && (this.readyState = WebSocket.CLOSING,
            WebSocket.__flash.close(this.__id)))
        }
        ,
        WebSocket.prototype.addEventListener = function(e, t) {
            e in this.__events || (this.__events[e] = []),
            this.__events[e].push(t)
        }
        ,
        WebSocket.prototype.removeEventListener = function(e, t) {
            if (e in this.__events)
                for (var n = this.__events[e], i = n.length - 1; i >= 0; --i)
                    if (n[i] === t) {
                        n.splice(i, 1);
                        break
                    }
        }
        ,
        WebSocket.prototype.dispatchEvent = function(e) {
            for (var t = this.__events[e.type] || [], n = 0; n < t.length; ++n)
                t[n](e);
            var i = this["on" + e.type];
            i && i.apply(this, [e])
        }
        ,
        WebSocket.prototype.__handleEvent = function(e) {
            "readyState"in e && (this.readyState = e.readyState),
            "protocol"in e && (this.protocol = e.protocol);
            var t;
            if ("open" == e.type || "error" == e.type)
                t = this.__createSimpleEvent(e.type);
            else if ("close" == e.type)
                t = this.__createSimpleEvent("close"),
                t.wasClean = e.wasClean ? !0 : !1,
                t.code = e.code,
                t.reason = e.reason;
            else {
                if ("message" != e.type)
                    throw "unknown event type: " + e.type;
                var n = decodeURIComponent(e.message);
                t = this.__createMessageEvent("message", n)
            }
            this.dispatchEvent(t)
        }
        ,
        WebSocket.prototype.__createSimpleEvent = function(e) {
            if (document.createEvent && window.Event) {
                var t = document.createEvent("Event");
                return t.initEvent(e, !1, !1),
                t
            }
            return {
                type: e,
                bubbles: !1,
                cancelable: !1
            }
        }
        ,
        WebSocket.prototype.__createMessageEvent = function(e, t) {
            if (document.createEvent && window.MessageEvent && !window.opera) {
                var n = document.createEvent("MessageEvent");
                if (!n.initMessageEvent && n.initEvent)
                    var n = new MessageEvent("message",{
                        view: window,
                        bubbles: !1,
                        cancelable: !1,
                        data: t
                    });
                else
                    n.initMessageEvent("message", !1, !1, t, null, null, window, null);
                return n
            }
            return {
                type: e,
                data: t,
                bubbles: !1,
                cancelable: !1
            }
        }
        ,
        WebSocket.CONNECTING = 0,
        WebSocket.OPEN = 1,
        WebSocket.CLOSING = 2,
        WebSocket.CLOSED = 3,
        WebSocket.__isFlashImplementation = !0,
        WebSocket.__initialized = !1,
        WebSocket.__flash = null,
        WebSocket.__instances = {},
        WebSocket.__tasks = [],
        WebSocket.__nextId = 0,
        WebSocket.loadFlashPolicyFile = function(e) {
            WebSocket.__addTask(function() {
                WebSocket.__flash.loadManualPolicyFile(e)
            })
        }
        ,
        WebSocket.canUse = !0,
        WebSocket.__initialize = function() {
            if (!WebSocket.__initialized) {
                if (WebSocket.__initialized = !0,
                WebSocket.__swfLocation && (window.WEB_SOCKET_SWF_LOCATION = WebSocket.__swfLocation),
                !window.WEB_SOCKET_SWF_LOCATION)
                    return void e.error("[WebSocket] set WEB_SOCKET_SWF_LOCATION to location of WebSocketMain.swf");
                !window.WEB_SOCKET_SUPPRESS_CROSS_DOMAIN_SWF_ERROR && !WEB_SOCKET_SWF_LOCATION.match(/(^|\/)WebSocketMainInsecure\.swf(\?.*)?$/) && WEB_SOCKET_SWF_LOCATION.match(/^\w+:\/\/([^\/]+)/);
                var t = document.createElement("div");
                t.id = "webSocketContainer",
                t.style.position = "absolute",
                WebSocket.__isFlashLite() ? (t.style.left = "0px",
                t.style.top = "0px") : (t.style.left = "-100px",
                t.style.top = "-100px");
                var n = document.createElement("div");
                n.id = "webSocketFlash",
                t.appendChild(n),
                document.body.insertBefore(t, document.body.childNodes[0]);
                var i = {}
                  , o = WEB_SOCKET_SWF_LOCATION;
                _sslM.get() && 0 != o.indexOf("https:") && (o = _sslM.SSL_SWF_URL,
                WEB_SOCKET_SWF_LOCATION = o),
                swfobject.embedSWF(o, "webSocketFlash", "1", "1", "10.0.0", null, i, {
                    hasPriority: !0,
                    swliveconnect: !0,
                    allowScriptAccess: "always"
                }, null, function(t) {
                    t.success || (WebSocket.canUse = !1,
                    e.error("[WebSocket] swfobject.embedSWF failed"))
                })
            }
        }
        ,
        WebSocket.flashOK = !1,
        WebSocket.__onFlashInitialized = function() {
            setTimeout(function() {
                WebSocket.flashOK = !0,
                WebSocket.__flash = document.getElementById("webSocketFlash"),
                WebSocket.__flash.setCallerUrl(location.href),
                WebSocket.__flash.setDebug(!!window.WEB_SOCKET_DEBUG);
                for (var e = 0; e < WebSocket.__tasks.length; ++e)
                    WebSocket.__tasks[e]();
                WebSocket.__tasks = []
            }, 0)
        }
        ,
        WebSocket.__onFlashEvent = function() {
            return setTimeout(function() {
                try {
                    for (var t = WebSocket.__flash.receiveEvents(), n = 0; n < t.length; ++n)
                        WebSocket.__instances[t[n].webSocketId].__handleEvent(t[n])
                } catch (i) {
                    e.error(i)
                }
            }, 0),
            !0
        }
        ,
        WebSocket.__log = function() {}
        ,
        WebSocket.__error = function(t) {
            e.error(decodeURIComponent(t))
        }
        ,
        WebSocket.__addTask = function(e) {
            WebSocket.__flash ? e() : WebSocket.__tasks.push(e)
        }
        ,
        WebSocket.__isFlashLite = function() {
            if (!window.navigator || !window.navigator.mimeTypes)
                return !1;
            var e = window.navigator.mimeTypes["application/x-shockwave-flash"];
            return e && e.enabledPlugin && e.enabledPlugin.filename && e.enabledPlugin.filename.match(/flashlite/i) ? !0 : !1
        }
        ,
        void (window.WEB_SOCKET_DISABLE_AUTO_INITIALIZATION || swfobject.addDomLoadEvent(function() {
            WebSocket.__initialize()
        })))
    }();
    var isFunc = isType("Function")
      , isBlob = isType("Blob")
      , isStr = isType("String")
      , hasLs = function() {
        if ("object" == typeof localStorage && localStorage && localStorage.setItem) {
            var e = "KKE_LOCALSTORAGE_TESTing";
            try {
                return localStorage.removeItem(e),
                localStorage.setItem(e, e),
                localStorage.removeItem(e),
                !0
            } catch (t) {
                return !1
            }
        }
        return !1
    }();
    if (!IO.WebPush4)
        if (IO.WebPush4 = function(e, t, n, i) {
            if (e = e.match(/(\w*:\/\/)?([^\/]+)(\/+.*)?/i)[2],
            this.id = "ws_" + getHashCode(e + t),
            this.host = e || "hq.sinajs.cn",
            this.list = (t + "").split(","),
            this.onmessage = n,
            i && isNaN(i.retryinterval)) {
                var o = this.host.split(".")[0];
                switch (o) {
                case "live":
                case "wslive":
                    i.retryinterval = 20;
                    break;
                case "newspush":
                    i.retryinterval = 39
                }
            }
            if (this.cfg = merge({
                interval: 3,
                retryinterval: 0,
                allowrepeat: !1,
                format: "",
                local: !1,
                ondebug: function() {},
                onMode: function() {},
                onToken: function() {},
                ishttp: !1,
                ssl: !1,
                ispmd: !1,
                authlocal: !1,
                authtype: void 0,
                onerr: function() {},
                isKick: !1
            }, i || {}),
            this.cfg.interval <= 0 && (this.cfg.interval = 1,
            log("set refresh interval to 1s")),
            this.cfg.retryinterval < 0 && (this.cfg.retryinterval = 0,
            log("set retry interval to 0")),
            _sslM.get() && (this.cfg.ssl = !0),
            this.cfg.ssl || "newspush.sinajs.cn" === this.host && (this.cfg.ssl = !0),
            this.isAuth = !1,
            this.authFailCount = 0,
            this.auth = void 0,
            this.getToken = void 0,
            this.stopAuthRe = void 0,
            this.cfg.authtype && "" != this.cfg.authtype) {
                this.isAuth = !0,
                this.cfg.local = this.cfg.authlocal;
                var s = new AuthMgr(this);
                this.auth = s.auth,
                this.getToken = s.getToken,
                this.stopAuthRe = s.stop,
                s.auth()
            } else
                this.init()
        }
        ,
        merge(IO.WebPush4.prototype, {
            VER: "4.4.9",
            MODE_NATIVE: "native",
            MODE_FLASH: "flash",
            MODE_JS: "js",
            socket: void 0,
            connection: void 0,
            localConn: void 0,
            mode: void 0,
            authReId: void 0,
            hasInit: !1,
            lastData: {},
            closeTimes: 0,
            maxRetryTimes: 3,
            resymbols: function(e) {
                if (e && !(e.length < 1) && this.connection)
                    if (1 == this.connection.readyState) {
                        var t = "=" + e;
                        this.cfg.ondebug("new keys" + t),
                        this.connection.send(t)
                    } else
                        this.cfg.ondebug("websocket connection is not available")
            },
            init: function() {
                if (!this.hasInit) {
                    if (!(this.tryNative() || this.tryFlash() || this.tryJS()))
                        return this.tryInitLater(),
                        !1;
                    this.hasInit = !0,
                    (this.tryNative() || this.tryFlash()) && (this.cfg.local ? this.createLocalConn() : this.subscribe())
                }
            },
            tryInitLater: function() {
                setTimeout(fnBind(this.init, this), 100)
            },
            createLocalConn: function() {
                this.cfg.ondebug("use Local-Conn");
                var e = this;
                this.localConn = new IO.LocalConn4({
                    key: this.id,
                    ssl: this.cfg.ssl,
                    onmessage: function(t) {
                        e.listen(t)
                    },
                    onchange: function() {
                        e.subscribe()
                    }
                })
            },
            disAndConn: function() {
                this.cfg.ondebug("disconnect aotumatically and reconnect with the new token"),
                this.retryClose(),
                this.subscribe()
            },
            renewalWithNewToken: function(e) {
                if (this.mode == this.MODE_JS)
                    return void this.cfg.ondebug("detected js mode, no need to renew the socket connect");
                if (this.cfg.ondebug("try to renew the connection with " + (e ? "exiting" : "new") + " token"),
                1 == this.connection.readyState)
                    if (this.getToken) {
                        var t = "*" + this.getToken();
                        this.connection.send(t)
                    } else
                        this.cfg.ondebug("cannot get token, should not be auth mode");
                else
                    this.cfg.ondebug("readyState error, try to reconnect..."),
                    this.disAndConn()
            },
            setReTimeout: function(e) {
                if (this.cfg.ondebug("receiving timeout(ms):" + e),
                !isNaN(e) && (clearInterval(this.authReId),
                0 != e)) {
                    e -= 1e3 * Math.floor(5 * Math.random() + 2),
                    this.cfg.ondebug("set timeout(ms):" + e);
                    var t = this;
                    this.authReId = setInterval(function() {
                        t.cfg.ondebug("timeup"),
                        t.auth({
                            cb: t.renewalWithNewToken,
                            forceOnline: !0,
                            noIp: !0
                        })
                    }, e)
                }
            },
            subscribe: function() {},
            receive: function() {},
            close: function() {},
            onClose: function() {},
            retryClose: function() {},
            listen: function(data) {
                function _makeKV($0, $1, $2) {
                    var d;
                    try {
                        d = "json" == _format ? eval("(" + $2 + ")") : $2
                    } catch (e) {}
                    d && (_self.lastData[$1] = _self.lastData[$1] || null,
                    _self.lastData[$1] === d ? _self.cfg.allowrepeat && (_data[$1] = d,
                    _hasData = !0) : (_data[$1] = _self.lastData[$1] = d,
                    _hasData = !0))
                }
                if (data) {
                    for (var _messages = data.match(/^[\s\S]+?$/gm), _data = {}, _format = this.cfg.format, _hasData = !1, _self = this, i = 0, l = _messages.length; l > i; i++)
                        /^sys_/.test(_messages[i]) || _messages[i].replace(/([^=]*)=([\s\S]*)/, _makeKV);
                    _hasData && (this.onmessage(_data),
                    this.authFailCount = 0)
                }
            },
            retry: function() {
                this.retryClose(),
                this.cfg.ondebug("retrying..."),
                this.isAuth ? this.auth({
                    cb: fnBind(this.subscribe, this),
                    forceOnline: !0
                }) : this.subscribe()
            },
            checkOnSysErr: function(e, t) {
                if (e && e.indexOf("sys_auth=") >= 0) {
                    if (t && (window[t + "sys_auth"] = null),
                    e.indexOf("FAILED") > 0) {
                        this.cfg.ondebug("receive FAILED from server");
                        var n = this.isAuth ? ++this.authFailCount > 2 : ++this.authFailCount > 9;
                        return n ? (this.cfg.ondebug("too many retries for FAILED, stop and disconnect"),
                        this.close(),
                        this.authFailCount = 0,
                        this.cfg.onerr({
                            msg_code: -3,
                            result: "too many retries for FAILED"
                        })) : this.retry(),
                        !0
                    }
                    if (e.indexOf("INVALID") > 0)
                        return this.cfg.ondebug("receive INVALID from server"),
                        this.isAuth ? ++this.authFailCount > 5 ? (this.cfg.ondebug("too many retries for FAILED, renew the token"),
                        this.retry()) : this.renewalWithNewToken(!0) : this.cfg.ondebug("ignore INVALID for non auth mode"),
                        !0;
                    e.indexOf("SUCCEED") > 0 && this.cfg.ondebug("successfully renewed")
                }
                return !1
            },
            tryNative: function() {
                return this.cfg.ishttp ? !1 : (this.cfg.ondebug("try Native WebSocket service"),
                checkNative() ? (this.nativeOK(),
                this.tryNative = function() {
                    return !0
                }
                ,
                !0) : (this.tryNative = function() {
                    return !1
                }
                ,
                !1))
            },
            nativeOK: function() {
                this.cfg.ondebug("Native WebSocket service is available"),
                this.mode = this.MODE_NATIVE,
                this.cfg.onMode(this.MODE_NATIVE),
                this.socket = WebSocket,
                this.subscribe = this.subScribeNative,
                this.receive = this.receiveNative,
                this.close = this.closeNative,
                this.onClose = this.onCloseNative,
                this.retryClose = this.retryCloseNative
            },
            subScribeNative: function() {
                this.cfg.ondebug(["master:try to connect and run,", "Auth mode:", this.isAuth, "Secure:", this.cfg.ssl, "Permessage Deflate:", this.cfg.ispmd].join(" "));
                var e = this.cfg.ssl ? "wss" : "ws"
                  , t = [e, "://", this.host, "/wskt"].join("");
                if (this.cfg.ispmd && (t += ".pmd"),
                t += "?",
                this.isAuth && (t += "token=" + this.getToken() + "&"),
                t += "list=" + this.list.join(","),
                this.connection = new this.socket(t),
                !this.socket.isNotNative && !this.connection.binaryType)
                    return this.cfg.ondebug("illegal WebSocket"),
                    this.connection.close(),
                    void this.tryJS(!0);
                var n = this;
                this.connection.toLongToConnectTimer = setTimeout(function() {
                    n.cfg.ondebug("nothing received from the server for a long time, try to close the connection...");
                    try {
                        n.connection.close()
                    } catch (e) {
                        n.cfg.ondebug("close connection err")
                    }
                }, 4e3),
                this.connection.onopen = function() {
                    n.resetCloseTimesTimer = setTimeout(function() {
                        n.cfg.ondebug("receiving data correctly, clear error count from " + n.closeTimes + " to 0"),
                        n.closeTimes = 0
                    }, 6e4)
                }
                ,
                this.connection.refresher = setInterval(function() {
                    1 == n.connection.readyState && n.connection.send("")
                }, 6e4),
                this.connection.onmessage = fnBind(this.receive, this),
                this.connection.onclose = fnBind(this.onClose, this),
                this.connection.onerror = function() {
                    n.mode == n.MODE_FLASH && (n.cfg.ondebug("flash error, close and retry..."),
                    n.onClose())
                }
            },
            parseData: function(e) {
                this.checkOnSysErr(e) || (this.cfg.local ? this.localConn && this.localConn.sendc(e.replace(/^sys_[\s\S]*?$(\r|\n)/gm, "")) : this.listen(e.replace(/^sys_[\s\S]*?$(\r|\n)/gm, "")))
            },
            receiveNative: function(e) {
                this.connection && clearTimeout(this.connection.toLongToConnectTimer);
                var t = e.data;
                this.parseData(t)
            },
            retryCloseNative: function() {
                clearInterval(this.authReId),
                this.isAuth && this.stopAuthRe(),
                this.connection && (clearInterval(this.connection.refresher),
                this.connection.refresher = this.connection.onmessage = this.connection.onclose = null,
                this.connection.close(),
                this.connection = null)
            },
            closeNative: function() {
                this.localConn && this.localConn.close(),
                this.localConn = null,
                this.socket = null,
                this.receive = null,
                this.subscribe = function() {}
                ,
                this.connection && (clearInterval(this.connection.refresher),
                this.connection.onclose = function() {}
                ,
                this.connection.close(),
                this.connection = null),
                this.isAuth && this.stopAuthRe(),
                clearInterval(this.authReId)
            },
            onCloseNative: function() {
                return clearTimeout(this.resetCloseTimesTimer),
                this.closeTimes++,
                this.cfg.ondebug("socket disconnected for " + this.closeTimes + " time(s)"),
                clearInterval(this.connection.refresher),
                this.connection.refresher = this.connection.onmessage = this.connection.onclose = null,
                this.connection = null,
                this.closeTimes > this.maxRetryTimes ? (this.cfg.ondebug("too many retries, switch to JS mode"),
                void this.tryJS(!0)) : void setTimeout(fnBind(this.subscribe, this), 1e3 * this.cfg.retryinterval)
            },
            __gotPhpUa: function() {
                if (!__phpUA) {
                    var e = String(window[_PHP_UA_VAR] || "");
                    try {
                        this.cfg.ondebug("php ua to flash:" + e),
                        WebSocket.__flash.setUA(e)
                    } catch (t) {
                        this.cfg.ondebug("[err]php ua to flash:" + e)
                    }
                    __phpUA = e
                }
            },
            setStaticFlashUa: function() {
                try {
                    WebSocket.__flash.setUA("hoshijiro")
                } catch (e) {
                    this.cfg.ondebug("error while calling Flash API:setUA")
                }
            },
            flashOK: function() {
                this.cfg.ondebug("flash component is available"),
                this.mode = this.MODE_FLASH,
                this.cfg.onMode(this.MODE_FLASH),
                this.socket = WebSocket,
                this.subscribe = this.subScribeNative,
                this.receive = this.receiveNative,
                this.close = this.closeNative,
                this.onClose = this.onCloseNative,
                this.retryClose = this.retryCloseNative
            },
            flashTryLimits: 5,
            tryFlash: function() {
                return this.cfg.ishttp ? !1 : this.flashTryLimits-- < 0 ? (this.cfg.ishttp = !0,
                !1) : (this.cfg.ondebug("try Flash mode, or waiting for Flash component responses"),
                WebSocket.flashOK ? (this.isAuth && this.setStaticFlashUa(),
                this.flashOK(),
                this.tryFlash = function() {
                    return !0
                }
                ,
                !0) : (WebSocket.canUse || (this.tryFlash = function() {
                    return !1
                }
                ),
                !1))
            },
            httpLoadHq: void 0,
            tryJS: function(e) {
                return this.cfg.ishttp && (e = !0),
                WebSocket.canUse && !e ? !1 : (this.httpLoadHq || (this.httpLoadHq = new JsLoadHqM({
                    ssl: this.cfg.ssl,
                    host: this.host
                })),
                this.jsHQOK(),
                !0)
            },
            jsHQOK: function() {
                this.cfg.ondebug("use JS mode"),
                this.mode = this.MODE_JS,
                this.cfg.onMode(this.MODE_JS),
                this.tryJS = function() {
                    return !0
                }
                ,
                this.subscribe = this.subScribeJS,
                this.receive = this.receiveJS,
                this.close = this.closeJS,
                this.retryClose = this.retryCloseJs,
                this.subscribe()
            },
            subScribeJS: function() {
                var e = this
                  , t = function() {
                    var t = {
                        domain: e.host,
                        type: e.cfg.format
                    };
                    e.isAuth && (t.others = "&token=" + e.getToken()),
                    e.httpLoadHq(e.list, fBind(e.receive, e), t)
                };
                t(),
                this.connection = setInterval(t, 1e3 * this.cfg.interval)
            },
            receiveJS: function() {
                var e = {}
                  , t = "json" == this.cfg.format ? "hq_json_" : "hq_str_";
                if (!this.checkOnSysErr(window[t + "sys_auth"], t)) {
                    for (var n, i = 0, o = this.list.length; o > i; i++)
                        this.lastData[this.list[i]] !== window[t + this.list[i]] && (this.lastData[this.list[i]] = e[this.list[i]] = window[t + this.list[i]],
                        n = !0);
                    n && (this.onmessage(e),
                    this.authFailCount = 0)
                }
            },
            closeJS: function() {
                this.subscribe = function() {}
                ,
                this.localConn && this.localConn.close(),
                this.localConn = null,
                clearInterval(this.connection),
                this.isAuth && this.stopAuthRe(),
                clearInterval(this.authReId)
            },
            retryCloseJs: function() {
                clearInterval(this.authReId),
                clearInterval(this.connection),
                this.isAuth && this.stopAuthRe()
            }
        }),
        hasLs && checkNative()) {
            var _iframeID = "IO_WEBPUSH4_LOCALCONN_IFRAME", _iframe, _pWin, proxy = void 0;
            IO.LocalConn4 = function(e) {
                var t = e.ssl ? "https://current.sina.com.cn/theone/IO.WebPush4.localConn.html" : "http://woocall.sina.com.cn/lib/iframe/IO.WebPush4.localConn.htm";
                if (_iframe || ((_iframe = document.getElementById(_iframeID)) || (_iframe = document.createElement("iframe"),
                _iframe.id = _iframeID,
                _iframe.style.display = "none",
                _iframe.src = t,
                document.body.insertBefore(_iframe, document.body.firstChild)),
                _pWin = _iframe.contentWindow,
                addEvent(window, "message", function(e) {
                    "M OK now!" == e.data && (proxy = {},
                    proxy.postMessage = function(e) {
                        _pWin.postMessage(e, "*")
                    }
                    ,
                    proxy.listen = function(e) {
                        addEvent(window, "message", e)
                    }
                    )
                })),
                !proxy)
                    return void setTimeout(fnBind(arguments.callee, this, arguments), 100);
                this.id = "lc" + Math.random(),
                this.id = this.id.replace("0.", ""),
                this.cfg = merge({
                    key: "",
                    ssl: !1,
                    onmessage: function() {},
                    onchange: function() {}
                }, e);
                var n = this;
                proxy.listen(function(e) {
                    if (e.data && isFunc(e.data.indexOf) && -1 != e.data.indexOf(n.id + ":")) {
                        var t, i;
                        switch (e.data.replace(/([^:]+):([\s\S]*)/, function() {
                            t = arguments[1],
                            i = arguments[2]
                        }),
                        t) {
                        case "IO_LOCALCONN_ONCHANGE_" + n.id:
                            n.onchange(i);
                            break;
                        case "IO_LOCALCONN_ONMESSAGE_" + n.id:
                            n.onmessage(i)
                        }
                    }
                }),
                proxy.postMessage(["newLocalConn(", this.cfg.key, ",", this.id, ")"].join(""))
            }
            ,
            merge(IO.LocalConn4.prototype, {
                onchange: function(e) {
                    this.cfg.onchange && this.cfg.onchange(e)
                },
                onmessage: function(e) {
                    this.cfg.onmessage && this.cfg.onmessage(e)
                },
                sendc: function(e) {
                    e && proxy.postMessage("IO_LOCALCONN_SEND_" + this.id + ":" + e)
                },
                close: function() {
                    proxy.postMessage("IO_LOCALCONN_CLOSE_" + this.id + ":now!")
                }
            })
        } else
            IO.LocalConn4 = function(e) {
                this.cfg = merge({
                    key: "",
                    ssl: !1,
                    onmessage: function() {},
                    onchange: function() {}
                }, e),
                IO.LocalConn4.flash = {
                    init: function() {}
                },
                IO.LocalConn4.prototype.sendc = function(e) {
                    this.onmessage(e)
                }
                ,
                this.onchange("master")
            }
            ,
            merge(IO.LocalConn4.prototype, {
                flashID: "localConnFlash",
                onchange: function(e) {
                    this.cfg.onchange && this.cfg.onchange(e)
                },
                onmessage: function(e) {
                    this.cfg.onmessage && this.cfg.onmessage(e)
                },
                sendc: function(e) {
                    e && this.constructor.flash.sendc(this.id, e)
                },
                close: function() {}
            }),
            IO.LocalConn4.flash = !1,
            IO.LocalConn4.objs = {},
            IO.LocalConn4.ready = function() {
                IO.LocalConn4.flash = document.localConnFlash || window.localConnFlash
            }
            ,
            IO.LocalConn4.onmessage = function(e, t) {
                this.objs[e].onmessage(t)
            }
            ,
            IO.LocalConn4.onchange = function(e, t) {
                this.objs[e].onchange(t)
            }
}();
;