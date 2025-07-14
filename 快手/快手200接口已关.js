const $ = new Env("ks");
const ckName = "ks";
//-------------------- 一般不动变量区域 -------------------------------------
//const notify = $.isNode() ? require("./sendNotify") : "";
const ckName1 = "u";
const ckName2 = "cid";
const ckName3 = "sid";
const ckName4 = "phid";
const ckName5 = ckName + "enc";
const ckName6 = ckName + "sign";
const ckName7 = ckName + "boxenc";
const ckName8 = ckName + "boxsign";
let s = ''
let ur = ''
let q = ''
let url = ($.isNode() ? process.env[ckName1] : $.getdata(ckName1)) || '';//青龙地址
let qlid = ($.isNode() ? process.env[ckName2] : $.getdata(ckName2)) || '';//cid
let sid = ($.isNode() ? process.env[ckName3] : $.getdata(ckName3)) || '';//sid
let phid = ($.isNode() ? process.env[ckName4] : $.getdata(ckName4)) || '';//phid
const Notify = 0;		 //0为关闭通知,1为打开通知,默认为1
let debug = 0;           //Debug调试   0关闭  1开启
let envSplitor = ["@", "\n"]; //多账号分隔符
let ck = msg = '';       //let ck,msg
let host, hostname;
let userCookie = ($.isNode() ? process.env[ckName] : $.getdata(ckName)) || '';
let encdata = ($.isNode() ? process.env[ckName5] : $.getdata(ckName5)) || '';
let sign1 = ($.isNode() ? process.env[ckName6] : $.getdata(ckName6)) || '';
let boxencdata = ($.isNode() ? process.env[ckName7] : $.getdata(ckName7)) || '';
let boxsign = ($.isNode() ? process.env[ckName8] : $.getdata(ckName8)) || '';
let userList = [];
let userIdx = 0;
let userCount = 0;
let ts = Date.now();
let ts25 = ts - 25000;
const now = new Date();
const hour = now.getHours();
//---------------------- 自定义变量区域 -----------------------------------
//---------------------------------------------------------
async function start() {
    console.log('\n================== 获取ad ==================\n');
    taskall = [];
    for (let user of userList) {
        taskall.push(await user.cid(672));
        taskall.push(await user.cid(606));
    }
    await Promise.all(taskall);
}

class UserInfo {
    constructor(str) {
        this.index = ++userIdx;
        this.ck = str.split('#'); //单账号多变量分隔符
        this.headers = {
            Host: 'nebula.kuaishou.com',
            Connection: 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; MI 8 Lite Build/QKQ1.190910.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.101 Mobile Safari/537.36 Yoda/3.0.8-rc5 ksNebula/10.11.30.4945 OS_PRO_BIT/64 MAX_PHY_MEM/5724 AZPREFIX/az4 ICFO/0 StatusHT/29 TitleHT/44 NetType/LTE ISLP/0 ISDM/0 ISLB/0 locale/zh-cn evaSupported/false CT/0 ISLM/-1',
            Cookie: "kuaishou.api_st=" + this.ck[1].replace('kuaishou.api_st=', '') + ';client_key=2ac2a76d;',
            'content-type': 'application/json',
        };
        this.hostt = 'https://api.e.kuaishou.com'
        this.salt = this.ck[0]
        this.path = '/rest/r/ad/task/report'
        this.query = `mod=Xiaomi%28MI%208%20Lite%29&appver=12.11.10.9145&egid=${this.ck[3]}&did=${this.ck[4]}`
    }

    async sig3(cid, llsid, t, tt, name) {
        if (t === 672) {
            var post = `bizStr={"businessId":${t},"endTime":${ts25},"extParams":"","mediaScene":"${tt}","neoInfos":[{"creativeId":${cid},"extInfo":"","llsid":${llsid},"requestSceneType":7,"taskType":2,"watchExpId":"","watchStage":0},{"creativeId":${cid},"extInfo":"","llsid":${llsid},"requestSceneType":1,"taskType":3,"watchExpId":"","watchStage":0}],"pageId":11101,"posId":24067,"reportType":0,"sessionId":"","startTime":${ts},"subPageId":100026367}&cs=false&client_key=2ac2a76d`
        }
        if (t === 606) {
            var post = `bizStr={"businessId":${t},"endTime":${ts25},"extParams":"","mediaScene":"${tt}","neoInfos":[{"creativeId":${cid},"extInfo":"","llsid":${llsid},"requestSceneType":7,"taskType":2,"watchExpId":"","watchStage":0}],"pageId":11101,"posId":20346,"reportType":0,"sessionId":"","startTime":${ts},"subPageId":100024064}&cs=false&client_key=2ac2a76d`
        }
        try {
            let options = {
                method: "post",
                url: ``,
                headers: {},
                body: `query=${this.query}|post=${post}|salt=${this.salt}|path=${this.path}|`,
            };
            //console.log(options);
            let result = await httpRequest(options, name);
            //console.log(result);
            if (result) {
                let sig = result.Sig
                let sig3 = result.Sig3
                let sigtoken = result.NsSig
                if (t === 672) {
                    await this.ad(sig, sig3, sigtoken, post)
                }
                if (t === 606) {
                    await this.boxad(sig, sig3, sigtoken, post)
                }
            } else {
                DoubleLog(`账号[${this.index}]  接口失败 ❌ 了呢,原因${result}`);
                //console.log(result);
            }
        } catch (error) {
            console.log(error);
        }
    }
    async enc(t, name) { // 获取encdata加密
        try {
            let options = {
                method: "post",
                url: `http://:6666/getInfo`,
                headers: {
                    Connection: 'keep-alive',
                    'Content-Type': 'application/json'
                },
                body: `{"did":"${this.ck[4]}","uid":"${this.ck[2]}"}`,
                //json: true
            };
            //console.log(options);
            let result = await httpRequest(options, name);
            if (result.code == 200) {
                let encData = result.adwtf
                let sign = result.adsign
                let boxencData = result.boxadwtf
                let boxsign = result.boxadsign
                await this.gettokenenc(encData, sign, boxencData, boxsign)
            } else {
                DoubleLog(`账号[${this.index}]  获取加密enc失败 ❌请联系开发者查看加密接口`);
                console.log(result);
            }
        } catch (error) {
            console.log(error);
        }
    }
    async cid(t, name) { // 获取ad
    if (encdata === '') {
            console.log(`未创建encData加密,开始创建encData加密`)
            await this.enc()
            process.exit()
        }
        if (t === 672) {
            var encData = encdata
            var sign = sign1
        }
        if (t === 606) {
            var encData = boxencdata
            var sign = boxsign
        }
        try {
            let options = {
                method: "post",
                url: `https://api.e.kuaishou.cn/rest/e/reward/mixed/ad`,
                headers: {
                    'Host': 'api.e.kuaishou.com',
                    'Connection': 'keep-alive',
                    'User-Agent': 'kwai-android aegon/3.56.0',
                    'Accept-Language': 'zh-cn',
                    'Cookie': "kuaishou.api_st=" + this.ck[1].replace('kuaishou.api_st=', ''),
                },
                form: {
                    encData: encData,
                    sign: sign,
                    client_key: '2ac2a76d'
                }
            };
            //console.log(options);
            let result = await httpRequest(options, name);
            //console.log(result);
            if (result.errorMsg == 'OK') {
                let s = result.feeds[0].exp_tag;
                let parts = s.split('/');
                let ss = parts[1];
                let f = ss.split('_')[1];
                f = ss.split('_')[0].split('/')[1];
                f = ss.split('_')[0];
                let cid = result.feeds[0].ad.creativeId
                let llsid = f
                let tp = result.feedType
                console.log(tp)
                if (tp === 0) {
                    let tt = 'video'
                    await this.sig3(cid, llsid, t, tt)
                }
            } else {
                console.log(`账号[${this.index}]  获取cid失败 ❌ 了呢,原因${result.errorMsg}`);
                console.log(result);
            }
        } catch (error) {
            console.log(error);
        }
    }

    async boxad(sig, sig3, sigtoken, post, name) { // boxad奖励
        try {
            let options = {
                method: "post",
                url: `https://api.e.kuaishou.com/rest/r/ad/task/report?${this.query}&sig=${sig}&__NS_sig3=${sig3}&__NS_xfalcon=&__NStokensig=${sigtoken}`,
                headers: {
                    "Host": "api.e.kuaishou.cn",
                    "User-Agent": "kwai-android aegon/3.56.0",
                    "Cookie": "kuaishou.api_st=" + this.ck[1].replace('kuaishou.api_st=', ''),
                    "page-code": "NEW_TASK_CENTER",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-Client-Info": "model=V2049A;os=Android;nqe-score=33;network=WIFI;",
                },
                body: post
            };
            //console.log(options);
            let result = await httpRequest(options, name);
            //console.log(result);
            if (result.result == 1) {
                console.log(`账号[${this.index}]  ${result.data.neoAmount} ${result.data.toastExt} ${result.data.taskNeoDetail}`);
            } else {
                DoubleLog(`账号[${this.index}]  奖励失败 ❌ 了呢,原因${result.result}`);
                console.log(result);
            }
        } catch (error) {
            console.log(error);
        }
    }
    async ad(sig, sig3, sigtoken, post, name) { // ad奖励
        try {
            let options = {
                method: "post",
                url: `https://api.e.kuaishou.com/rest/r/ad/task/report?${this.query}&sig=${sig}&__NS_sig3=${sig3}&__NS_xfalcon=&__NStokensig=${sigtoken}`,
                headers: {
                    "Host": "api.e.kuaishou.cn",
                    "User-Agent": "kwai-android aegon/3.56.0",
                    "Cookie": "kuaishou.api_st=" + this.ck[1].replace('kuaishou.api_st=', ''),
                    "page-code": "NEW_TASK_CENTER",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-Client-Info": "model=V2049A;os=Android;nqe-score=33;network=WIFI;",
                },
                body: post
            };
            //console.log(options);
            let result = await httpRequest(options, name);
            //console.log(result);
            if (result.result == 1) {
                console.log(`账号[${this.index}]  ${result.data.neoAmount} ${result.data.toastExt} ${result.data.taskNeoDetail}`);
            } else {
                DoubleLog(`账号[${this.index}]  奖励失败 ❌ 了呢,原因${result.result}`);
                console.log(result);
            }
        } catch (error) {
            console.log(error);
        }
    }
 async gettokenenc(encData, sign, boxencData, boxsign, name) { // 获取token
        try {
            let options = {
                method: "Get",
                url: `http://${url}/open/auth/token?client_id=${qlid}&client_secret=${sid}`,
            };
            let result = await httpRequest(options, name);
            if (result.code == 200) {
                console.log('✅获取青龙token成功✅')
                //DoubleLog(`账号[${this.index}]  Token: ${result.data.token}`);
                let qltk = `${result.data.token_type} ${result.data.token}`
                await this.enccj(qltk, encData, sign, boxencData, boxsign)
                //console.log(qltk)
            } else {
                DoubleLog(`账号[${this.index}]  获取token失败 ❌ 了呢,原因${result.msg}`);
                console.log(result);
            }
        } catch (error) {
            console.log(error);
        }
    }
    async enccj(qltk, encData, sign, boxencData, boxsign, name) { // enc创建
        try {
            let options = {
                method: "post",
                url: `http://${url}/open/envs?`,
                headers: {
                    Authorization: qltk,
                    Connection: 'keep-alive',
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
                },
                body: `[{"value":"${encData}","name":"${ckName5}"}]`,
            };
            //console.log(options);
            let result = await httpRequest(options, name);
            //console.log(result);
            if (result.code == 200) {
                console.log(`✅${ckName5}变量添加成功✅`)
                await this.signcj(qltk, encData, sign, boxencData, boxsign)
            } else {
                DoubleLog(`账号[${this.index}]  变量添加失败 ❌ 了呢,原因${result.message}`);
                console.log(result);
                process.exit();
            }
        } catch (error) {
            console.log(error);
        }
    }
    async signcj(qltk, encData, sign, boxencData, boxsign, name) { // sign创建
        try {
            let options = {
                method: "post",
                url: `http://${url}/open/envs?`,
                headers: {
                    Authorization: qltk,
                    Connection: 'keep-alive',
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
                },
                body: `[{"value":"${sign}","name":"${ckName6}"}]`,
            };
            //console.log(options);
            let result = await httpRequest(options, name);
            //console.log(result);
            if (result.code == 200) {
                console.log(`✅${ckName6}变量添加成功✅`)
                await this.boxenccj(qltk, encData, sign, boxencData, boxsign)
            } else {
                DoubleLog(`账号[${this.index}]  变量添加失败 ❌ 了呢,原因${result.message}`);
                console.log(result);
                process.exit();
            }
        } catch (error) {
            console.log(error);
        }
    }
    async boxenccj(qltk, encData, sign, boxencData, boxsign, name) { // boxenc创建
        try {
            let options = {
                method: "post",
                url: `http://${url}/open/envs?`,
                headers: {
                    Authorization: qltk,
                    Connection: 'keep-alive',
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
                },
                body: `[{"value":"${boxencData}","name":"${ckName7}"}]`,
            };
            //console.log(options);
            let result = await httpRequest(options, name);
            //console.log(result);
            if (result.code == 200) {
                console.log(`✅${ckName7}变量添加成功✅`)
                await this.boxsigncj(qltk, encData, sign, boxencData, boxsign)
            } else {
                DoubleLog(`账号[${this.index}]  变量添加失败 ❌ 了呢,原因${result.message}`);
                console.log(result);
                process.exit();
            }
        } catch (error) {
            console.log(error);
        }
    }
    async boxsigncj(qltk, encData, sign, boxencData, boxsign, name) { // boxsign创建
        try {
            let options = {
                method: "post",
                url: `http://${url}/open/envs?`,
                headers: {
                    Authorization: qltk,
                    Connection: 'keep-alive',
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
                },
                body: `[{"value":"${boxsign}","name":"${ckName8}"}]`,
            };
            //console.log(options);
            let result = await httpRequest(options, name);
            //console.log(result);
            if (result.code == 200) {
                console.log(`✅${ckName8}变量添加成功✅`)
            } else {
                DoubleLog(`账号[${this.index}]  变量添加失败 ❌ 了呢,原因${result.message}`);
                console.log(result);
                process.exit();
            }
        } catch (error) {
            console.log(error);
        }
    }
    async gettoken(r, name) { // 获取token
        try {
            let options = {
                method: "Get",
                url: `http://${url}/open/auth/token?client_id=${qlid}&client_secret=${sid}`,
            };
            //console.log(options);
            let result = await httpRequest(options, name);
            //console.log(result);
            if (result.code == 200) {
                console.log('✅获取青龙token成功✅')
                //DoubleLog(`账号[${this.index}]  Token: ${result.data.token}`);
                let qltk = `${result.data.token_type} ${result.data.token}`
                //await wait(1)
                await this.cx(qltk, r)
                await this.envcx(qltk, r)
                //console.log(qltk)
            } else {
                DoubleLog(`账号[${this.index}]  获取token失败 ❌ 了呢,原因${result.msg}`);
                console.log(result);
            }
        } catch (error) {
            console.log(error);
        }
    }
    async gettoken1(j, name) { // 获取token
        try {
            let options = {
                method: "Get",
                url: `http://${url}/open/auth/token?client_id=${qlid}&client_secret=${sid}`,
            };
            //console.log(options);
            let result = await httpRequest(options, name);
            //console.log(result);
            if (result.code == 200) {
                console.log('✅获取青龙token成功✅')
                //DoubleLog(`账号[${this.index}]  Token: ${result.data.token}`);
                let qltk = `${result.data.token_type} ${result.data.token}`
                //await wait(1)
                await this.cx1(qltk, j)
            } else {
                DoubleLog(`账号[${this.index}]  获取token失败 ❌ 了呢,原因${result.msg}`);
                console.log(result);
            }
        } catch (error) {
            console.log(error);
        }
    }
    async cx(qltk, r, name) { // 查询
        try {
            let options = {
                method: "Get",
                url: `http://${url}/open/crons?searchValue=&page=1&size=50&filters=\{\}&queryString=\{"filters":null,"sorts":null,"filterRelation":"and"\}&t=1733311819417`,
                headers: {
                    Authorization: qltk,
                    'Accept': 'application/json',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                    'Content-Type': 'application/json;charset=UTF-8',
                    'Proxy-Connection': 'keep-alive',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.200',
                    'content-type': 'application/json'
                }
            };
            //console.log(options);
            let result = await httpRequest(options, name);
            //console.log(result);
            if (result.code == 200) {
                console.log('✅获取数据成功✅')
                //DoubleLog(`账号[${this.index}]  Token: ${result.data[25].value}`);
                this.iid = []
                //this.gid = []
                this.tid = []
                for (let i = 0; i < result.data.data.length; i++) {
                    let tid = result.data.data[i].name
                    //let gid = result.data[i].value
                    let iid = result.data.data[i].id
                    //this.gid.push(gid)
                    this.tid.push(tid)
                    this.iid.push(iid)
                    //console.log(tid)
                    if (r === 6001) {
                        if (tid == $.name) {
                            console.log(iid)
                            await this.sc(qltk, iid)
                        }
                    }
                    if (r === 500) {
                        if (tid == $.name) {
                            console.log(iid)
                            await this.sc(qltk, iid)
                        }
                    }
                    if (r === 'INVALID_REQUEST') {
                        if (tid == $.name) {
                            console.log(iid)
                            await this.sc(qltk, iid)
                        }
                    }
                }
            } else {
                DoubleLog(`账号[${this.index}]  获取数据失败 ❌ 了呢,原因${result.msg}`);
                console.log(result);
            }
        } catch (error) {
            console.log(error);
        }
    }
    async envcx(qltk, r, name) { // 变量查询
        try {
            let options = {
                method: "Get",
                url: `http://${url}/open/envs?`,
                headers: {
                    Authorization: qltk,
                    'Accept': 'application/json',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                    'Content-Type': 'application/json;charset=UTF-8',
                    'Proxy-Connection': 'keep-alive',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.200',
                    'content-type': 'application/json'
                }
            };
            //console.log(options);
            let result = await httpRequest(options, name);
            //console.log(result);
            if (result.code == 200) {
                console.log('✅获取数据成功✅')
                //DoubleLog(`账号[${this.index}]  Token: ${result.data[25].value}`);
                this.iid = []
                //this.gid = []
                this.tid = []
                for (let i = 0; i < result.data.length; i++) {
                    var tid = result.data[i].name
                    //let gid = result.data[i].value
                    let iid = result.data[i].id
                    //this.gid.push(gid)
                    this.tid.push(tid)
                    this.iid.push(iid)
                    //console.log(tid)
                    if (r === 6001) {
                        if (tid == ckName) {
                            console.log(iid)
                            await this.envjy(qltk, iid)
                        }
                    }
                    if (r === 500) {
                        if (tid == ckName) {
                            console.log(iid)
                            await this.envjy(qltk, iid)
                        }
                    }
                    if (r === 'INVALID_REQUEST') {
                        if (tid == ckName) {
                            console.log(iid)
                            await this.envjy(qltk, iid)
                        }
                    }
                }
            } else {
                DoubleLog(`账号[${this.index}]  获取数据失败 ❌ 了呢,原因${result.msg}`);
                console.log(result);
            }
        } catch (error) {
            console.log(error);
        }
    }
    async envcx1(qltk, j, name) { // 变量查询
        try {
            let options = {
                method: "Get",
                url: `http://${url}/open/envs?`,
                headers: {
                    Authorization: qltk,
                    'Accept': 'application/json',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                    'Content-Type': 'application/json;charset=UTF-8',
                    'Proxy-Connection': 'keep-alive',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.200',
                    'content-type': 'application/json'
                }
            };
            //console.log(options);
            let result = await httpRequest(options, name);
            //console.log(result);
            if (result.code == 200) {
                console.log('✅获取数据成功✅')
                //DoubleLog(`账号[${this.index}]  Token: ${result.data[25].value}`);
                this.iid = []
                //this.gid = []
                this.tid = []
                for (let i = 0; i < result.data.length; i++) {
                    var tid = result.data[i].name
                    //let gid = result.data[i].value
                    let iid = result.data[i].id
                    //this.gid.push(gid)
                    this.tid.push(tid)
                    this.iid.push(iid)
                    //console.log(tid)
                }
                if (j > 0) {
                    if (tid === ckName) {
                        console.log('环境变量已存在')
                        process.exit();
                    } else {
                        console.log('未找到变量开始添加')
                        await this.envcj(qltk)
                    }
                }
            } else {
                DoubleLog(`账号[${this.index}]  获取数据失败 ❌ 了呢,原因${result.msg}`);
                console.log(result);
            }
        } catch (error) {
            console.log(error);
        }
    }
    async envcj(qltk, r, name) { // 变量查询
        try {
            let options = {
                method: "post",
                url: `http://${url}/open/envs?`,
                headers: {
                    Authorization: qltk,
                    Connection: 'keep-alive',
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
                },
                body: `[{"value":"${this.ck[0]}#${this.ck[1]}#${this.ck[2]}#${this.ck[3]}#${this.ck[4]}","name":"${ckName}","remarks":"${$.name}"}]`,
            };
            //console.log(options);
            let result = await httpRequest(options, name);
            //console.log(result);
            if (result.code == 200) {
                console.log('✅变量添加成功✅')
                await this.zh('转换')
            } else {
                DoubleLog(`账号[${this.index}]  变量添加失败 ❌ 了呢,原因${result.message}`);
                console.log(result);
                process.exit();
            }
        } catch (error) {
            console.log(error);
        }
    }
    async cx1(qltk, j, name) { // 查询
        try {
            let options = {
                method: "Get",
                url: `http://${url}/open/crons?searchValue=&page=1&size=50&filters=\{\}&queryString=\{"filters":null,"sorts":null,"filterRelation":"and"\}&t=1733311819417`,
                headers: {
                    Authorization: qltk,
                    'Accept': 'application/json',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                    'Content-Type': 'application/json;charset=UTF-8',
                    'Proxy-Connection': 'keep-alive',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.200',
                    'content-type': 'application/json'
                }
            };
            //console.log(options);
            let result = await httpRequest(options, name);
            //console.log(result);
            if (result.code == 200) {
                console.log('✅获取数据成功✅')
                //DoubleLog(`账号[${this.index}]  Token: ${result.data[25].value}`);
                this.iid = []
                //this.gid = []
                this.tid = []
                for (let i = 0; i < result.data.data.length; i++) {
                    let tid = result.data.data[i].name
                    //let gid = result.data[i].value
                    let iid = result.data.data[i].id
                    //this.gid.push(gid)
                    this.tid.push(tid)
                    this.iid.push(iid)
                    //console.log(tid)
                    if (j > 0) {
                        await this.envcx1(qltk, j)
                    }
                    if (j === 0) {
                        if (tid == $.name) {
                            //console.log(iid)
                            await this.jy(qltk, iid)
                        }
                    }
                }
            } else {
                DoubleLog(`账号[${this.index}]  获取数据失败 ❌ 了呢,原因${result.msg}`);
                console.log(result);
            }
        } catch (error) {
            console.log(error);
        }
    }
    async jy(qltk, iid, name) { // 禁用任务
        try {
            let options = {
                method: "put",
                url: `http://${url}/open/crons/disable?t=1733302456179`,
                headers: {
                    Authorization: qltk,
                    'Proxy-Connection': 'keep-alive',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.200',
                    'content-type': 'application/json'
                },
                body: `[${iid}]`
            };
            //console.log(options);
            let result = await httpRequest(options, name);
            //console.log(result);
            if (result.code == 200) {
                console.log('✅禁用成功✅')
            } else {
                DoubleLog(`账号[${this.index}]  禁用失败 ❌ 了呢,原因${result.msg}`);
                console.log(result);
            }
        } catch (error) {
            console.log(error);
        }
    }

    async envjy(qltk, iid, name) { // 变量禁用
        try {
            let options = {
                method: "put",
                url: `http://${url}/open/envs/disable?t=1733357332759`,
                headers: {
                    Authorization: qltk,
                    'Proxy-Connection': 'keep-alive',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.200',
                    'content-type': 'application/json'
                },
                body: `[${iid}]`
            };
            //console.log(options);
            let result = await httpRequest(options, name);
            //console.log(result);
            if (result.code == 200) {
                console.log('✅禁用ck成功✅')
                process.exit();
            } else {
                DoubleLog(`账号[${this.index}]  禁用ck失败 ❌ 了呢,原因${result.msg}`);
                console.log(result);
            }
        } catch (error) {
            console.log(error);
        }
    }
    async sc(qltk, iid, name) { // 删除任务
        try {
            let options = {
                method: "DELETE",
                url: `http://${url}/open/crons?t=1733315670577`,
                headers: {
                    Authorization: qltk,
                    'Proxy-Connection': 'keep-alive',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.200',
                    'content-type': 'application/json'
                },
                body: `[${iid}]`
            };
            //console.log(options);
            let result = await httpRequest(options, name);
            //console.log(result);
            if (result.code == 200) {
                console.log('✅删除任务成功✅')
            } else {
                DoubleLog(`账号[${this.index}]  删除任务失败 ❌ 了呢,原因${result.msg}`);
                console.log(result);
            }
        } catch (error) {
            console.log(error);
        }
    }

}

!(async () => {
    if (!(await checkEnv())) return;
    if (userList.length > 0) {
        await start();
    }
    await SendMsg(msg);
})()
    .catch((e) => console.log(e))
    .finally(() => $.done());


// #region ********************************************************  固定代码  ********************************************************
function rr() { //随机数
    return Math.floor(Math.random() * (10 - 8 + 1)) + 8;
}
function base64decode(data) {
    let a = Buffer.from(data, 'base64').toString('utf-8')
    return a
}
// 变量检查与处理
async function checkEnv() {
    if (userCookie) {
        // console.log(userCookie);
        let e = envSplitor[0];
        for (let o of envSplitor)
            if (userCookie.indexOf(o) > -1) {
                e = o;
                break;
            }
        for (let n of userCookie.split(e)) n && userList.push(new UserInfo(n));
        userCount = userList.length;
    } else {
        console.log("未找到CK");
        return;
    }
    return console.log(`共找到${userCount}个账号`), true;//true == !0
}
// =========================================== 不懂不要动 =========================================================
// 网络请求 (get, post等)
async function httpRequest(options, name) { var request = require("request"); return new Promise((resolve) => { if (!name) { let tmp = arguments.callee.toString(); let re = /function\s*(\w*)/i; let matches = re.exec(tmp); name = matches[1] } if (debug) { console.log(`\n【debug】===============这是${name}请求信息===============`); console.log(options) } request(options, function (error, response) { if (error) throw new Error(error); let data = response.body; try { if (debug) { console.log(`\n\n【debug】===============这是${name}返回数据==============`); console.log(data) } if (typeof data == "string") { if (isJsonString(data)) { let result = JSON.parse(data); if (debug) { console.log(`\n【debug】=============这是${name}json解析后数据============`); console.log(result) } resolve(result) } else { let result = data; resolve(result) } function isJsonString(str) { if (typeof str == "string") { try { if (typeof JSON.parse(str) == "object") { return true } } catch (e) { return false } } return false } } else { let result = data; resolve(result) } } catch (e) { console.log(error, response); console.log(`\n ${name}失败了!请稍后尝试!!`) } finally { resolve() } }) }) }
// 等待 X 秒
function wait(n) { return new Promise(function (resolve) { setTimeout(resolve, n * 1000) }) }
// 双平台log输出
function DoubleLog(data) { if ($.isNode()) { if (data) { console.log(`${data}`); msg += `\n${data}` } } else { console.log(`${data}`); msg += `\n${data}` } }
// 发送消息
async function SendMsg(message) { if (!message) return; if (Notify > 0) { if ($.isNode()) { var notify = require("./sendNotify"); await notify.sendNotify($.name, message) } else { $.msg($.name, '', message) } } else { console.log(message) } }
// 完整 Env
function Env(t, e) { "undefined" != typeof process && JSON.stringify(process.env).indexOf("GITHUB") > -1 && process.exit(0); class s { constructor(t) { this.env = t } send(t, e = "GET") { t = "string" == typeof t ? { url: t } : t; let s = this.get; return "POST" === e && (s = this.post), new Promise((e, i) => { s.call(this, t, (t, s, r) => { t ? i(t) : e(s) }) }) } get(t) { return this.send.call(this.env, t) } post(t) { return this.send.call(this.env, t, "POST") } } return new class { constructor(t, e) { this.name = t, this.http = new s(this), this.data = null, this.dataFile = "box.dat", this.logs = [], this.isMute = !1, this.isNeedRewrite = !1, this.logSeparator = "\n", this.startTime = (new Date).getTime(), Object.assign(this, e), this.log("", `🔔${this.name}, 开始!`) } isNode() { return "undefined" != typeof module && !!module.exports } isQuanX() { return "undefined" != typeof $task } isSurge() { return "undefined" != typeof $httpClient && "undefined" == typeof $loon } isLoon() { return "undefined" != typeof $loon } toObj(t, e = null) { try { return JSON.parse(t) } catch { return e } } toStr(t, e = null) { try { return JSON.stringify(t) } catch { return e } } getjson(t, e) { let s = e; const i = this.getdata(t); if (i) try { s = JSON.parse(this.getdata(t)) } catch { } return s } setjson(t, e) { try { return this.setdata(JSON.stringify(t), e) } catch { return !1 } } getScript(t) { return new Promise(e => { this.get({ url: t }, (t, s, i) => e(i)) }) } runScript(t, e) { return new Promise(s => { let i = this.getdata("@chavy_boxjs_userCfgs.httpapi"); i = i ? i.replace(/\n/g, "").trim() : i; let r = this.getdata("@chavy_boxjs_userCfgs.httpapi_timeout"); r = r ? 1 * r : 20, r = e && e.timeout ? e.timeout : r; const [o, h] = i.split("@"), n = { url: `http://${h}/v1/scripting/evaluate`, body: { script_text: t, mock_type: "cron", timeout: r }, headers: { "X-Key": o, Accept: "*/*" } }; this.post(n, (t, e, i) => s(i)) }).catch(t => this.logErr(t)) } loaddata() { if (!this.isNode()) return {}; { this.fs = this.fs ? this.fs : require("fs"), this.path = this.path ? this.path : require("path"); const t = this.path.resolve(this.dataFile), e = this.path.resolve(process.cwd(), this.dataFile), s = this.fs.existsSync(t), i = !s && this.fs.existsSync(e); if (!s && !i) return {}; { const i = s ? t : e; try { return JSON.parse(this.fs.readFileSync(i)) } catch (t) { return {} } } } } writedata() { if (this.isNode()) { this.fs = this.fs ? this.fs : require("fs"), this.path = this.path ? this.path : require("path"); const t = this.path.resolve(this.dataFile), e = this.path.resolve(process.cwd(), this.dataFile), s = this.fs.existsSync(t), i = !s && this.fs.existsSync(e), r = JSON.stringify(this.data); s ? this.fs.writeFileSync(t, r) : i ? this.fs.writeFileSync(e, r) : this.fs.writeFileSync(t, r) } } lodash_get(t, e, s) { const i = e.replace(/\[(\d+)\]/g, ".$1").split("."); let r = t; for (const t of i) if (r = Object(r)[t], void 0 === r) return s; return r } lodash_set(t, e, s) { return Object(t) !== t ? t : (Array.isArray(e) || (e = e.toString().match(/[^.[\]]+/g) || []), e.slice(0, -1).reduce((t, s, i) => Object(t[s]) === t[s] ? t[s] : t[s] = Math.abs(e[i + 1]) >> 0 == +e[i + 1] ? [] : {}, t)[e[e.length - 1]] = s, t) } getdata(t) { let e = this.getval(t); if (/^@/.test(t)) { const [, s, i] = /^@(.*?)\.(.*?)$/.exec(t), r = s ? this.getval(s) : ""; if (r) try { const t = JSON.parse(r); e = t ? this.lodash_get(t, i, "") : e } catch (t) { e = "" } } return e } setdata(t, e) { let s = !1; if (/^@/.test(e)) { const [, i, r] = /^@(.*?)\.(.*?)$/.exec(e), o = this.getval(i), h = i ? "null" === o ? null : o || "{}" : "{}"; try { const e = JSON.parse(h); this.lodash_set(e, r, t), s = this.setval(JSON.stringify(e), i) } catch (e) { const o = {}; this.lodash_set(o, r, t), s = this.setval(JSON.stringify(o), i) } } else s = this.setval(t, e); return s } getval(t) { return this.isSurge() || this.isLoon() ? $persistentStore.read(t) : this.isQuanX() ? $prefs.valueForKey(t) : this.isNode() ? (this.data = this.loaddata(), this.data[t]) : this.data && this.data[t] || null } setval(t, e) { return this.isSurge() || this.isLoon() ? $persistentStore.write(t, e) : this.isQuanX() ? $prefs.setValueForKey(t, e) : this.isNode() ? (this.data = this.loaddata(), this.data[e] = t, this.writedata(), !0) : this.data && this.data[e] || null } initGotEnv(t) { this.got = this.got ? this.got : require("got"), this.cktough = this.cktough ? this.cktough : require("tough-cookie"), this.ckjar = this.ckjar ? this.ckjar : new this.cktough.CookieJar, t && (t.headers = t.headers ? t.headers : {}, void 0 === t.headers.Cookie && void 0 === t.cookieJar && (t.cookieJar = this.ckjar)) } get(t, e = (() => { })) { t.headers && (delete t.headers["Content-Type"], delete t.headers["Content-Length"]), this.isSurge() || this.isLoon() ? (this.isSurge() && this.isNeedRewrite && (t.headers = t.headers || {}, Object.assign(t.headers, { "X-Surge-Skip-Scripting": !1 })), $httpClient.get(t, (t, s, i) => { !t && s && (s.body = i, s.statusCode = s.status), e(t, s, i) })) : this.isQuanX() ? (this.isNeedRewrite && (t.opts = t.opts || {}, Object.assign(t.opts, { hints: !1 })), $task.fetch(t).then(t => { const { statusCode: s, statusCode: i, headers: r, body: o } = t; e(null, { status: s, statusCode: i, headers: r, body: o }, o) }, t => e(t))) : this.isNode() && (this.initGotEnv(t), this.got(t).on("redirect", (t, e) => { try { if (t.headers["set-cookie"]) { const s = t.headers["set-cookie"].map(this.cktough.Cookie.parse).toString(); s && this.ckjar.setCookieSync(s, null), e.cookieJar = this.ckjar } } catch (t) { this.logErr(t) } }).then(t => { const { statusCode: s, statusCode: i, headers: r, body: o } = t; e(null, { status: s, statusCode: i, headers: r, body: o }, o) }, t => { const { message: s, response: i } = t; e(s, i, i && i.body) })) } post(t, e = (() => { })) { if (t.body && t.headers && !t.headers["Content-Type"] && (t.headers["Content-Type"] = "application/x-www-form-urlencoded"), t.headers && delete t.headers["Content-Length"], this.isSurge() || this.isLoon()) this.isSurge() && this.isNeedRewrite && (t.headers = t.headers || {}, Object.assign(t.headers, { "X-Surge-Skip-Scripting": !1 })), $httpClient.post(t, (t, s, i) => { !t && s && (s.body = i, s.statusCode = s.status), e(t, s, i) }); else if (this.isQuanX()) t.method = "POST", this.isNeedRewrite && (t.opts = t.opts || {}, Object.assign(t.opts, { hints: !1 })), $task.fetch(t).then(t => { const { statusCode: s, statusCode: i, headers: r, body: o } = t; e(null, { status: s, statusCode: i, headers: r, body: o }, o) }, t => e(t)); else if (this.isNode()) { this.initGotEnv(t); const { url: s, ...i } = t; this.got.post(s, i).then(t => { const { statusCode: s, statusCode: i, headers: r, body: o } = t; e(null, { status: s, statusCode: i, headers: r, body: o }, o) }, t => { const { message: s, response: i } = t; e(s, i, i && i.body) }) } } time(t, e = null) { const s = e ? new Date(e) : new Date; let i = { "M+": s.getMonth() + 1, "d+": s.getDate(), "H+": s.getHours(), "m+": s.getMinutes(), "s+": s.getSeconds(), "q+": Math.floor((s.getMonth() + 3) / 3), S: s.getMilliseconds() }; /(y+)/.test(t) && (t = t.replace(RegExp.$1, (s.getFullYear() + "").substr(4 - RegExp.$1.length))); for (let e in i) new RegExp("(" + e + ")").test(t) && (t = t.replace(RegExp.$1, 1 == RegExp.$1.length ? i[e] : ("00" + i[e]).substr(("" + i[e]).length))); return t } msg(e = t, s = "", i = "", r) { const o = t => { if (!t) return t; if ("string" == typeof t) return this.isLoon() ? t : this.isQuanX() ? { "open-url": t } : this.isSurge() ? { url: t } : void 0; if ("object" == typeof t) { if (this.isLoon()) { let e = t.openUrl || t.url || t["open-url"], s = t.mediaUrl || t["media-url"]; return { openUrl: e, mediaUrl: s } } if (this.isQuanX()) { let e = t["open-url"] || t.url || t.openUrl, s = t["media-url"] || t.mediaUrl; return { "open-url": e, "media-url": s } } if (this.isSurge()) { let e = t.url || t.openUrl || t["open-url"]; return { url: e } } } }; if (this.isMute || (this.isSurge() || this.isLoon() ? $notification.post(e, s, i, o(r)) : this.isQuanX() && $notify(e, s, i, o(r))), !this.isMuteLog) { let t = ["", "==============📣系统通知📣=============="]; t.push(e), s && t.push(s), i && t.push(i), console.log(t.join("\n")), this.logs = this.logs.concat(t) } } log(...t) { t.length > 0 && (this.logs = [...this.logs, ...t]), console.log(t.join(this.logSeparator)) } logErr(t, e) { const s = !this.isSurge() && !this.isQuanX() && !this.isLoon(); s ? this.log("", `❗️${this.name}, 错误!`, t.stack) : this.log("", `❗️${this.name}, 错误!`, t) } wait(t) { return new Promise(e => setTimeout(e, t)) } done(t = {}) { const e = (new Date).getTime(), s = (e - this.startTime) / 1e3; this.log("", `🔔${this.name}, 结束! 🕛 ${s} 秒`), this.log(), (this.isSurge() || this.isQuanX() || this.isLoon()) && $done(t) } }(t, e) }