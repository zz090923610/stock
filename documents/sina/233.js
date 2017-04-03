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