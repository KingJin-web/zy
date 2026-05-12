const axios = require('axios');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

// ============================================
// 大象新闻积分脚本 - Token缓存版
// ============================================
// 
// 功能说明：
// 1. Token缓存机制 - 优先使用缓存token，失效后自动重新登录
// 2. 智能任务检测 - 自动检测任务完成情况，只做未完成的任务
// 3. 支持任务：
//    - 每日签到 (eventCode: 3)
//    - 使用时长 (eventCode: 24)
//    - 浏览内容 (eventCode: 26) - 最多15次
//    - 点赞文章 (eventCode: 11) - 最多8次
//    - 分享文章 (eventCode: 9) - 最多8次
//    - 微剧打卡签到 (兑吧 sign/component/doSign，9天抽奖)
//
// 环境变量配置： 手机号&密码&支付宝&姓名
// export dxxwhd="账号&密码"  # 单账号
// export dxxwhd="账号1&密码1@账号2&密码2"  # 多账号用@分隔
// export dxxwhd="账号1&密码1
// 账号2&密码2"  # 多账号也可用换行分隔
//
// 脚本配置（在脚本中修改）：
// ENABLE_NOTIFY = true     # 开启通知（默认false，需要青龙面板环境）
// ENABLE_CONCURRENT = true # 开启并发模式（默认false，多账号同时执行）
//
// ============================================

let dxxwhd = (process.env.dxxwhd) || "";
let dxxwhdArr = [];
let msg = '';

// ========== 配置项 ==========
// 通知配置 - 设置为true开启通知
const ENABLE_NOTIFY = false;  // 默认关闭，需要时改为true

// 并发模式 - 设置为true开启多账号并发执行
const ENABLE_CONCURRENT = false;  // 默认关闭，需要时改为true

// Token缓存文件路径
const TOKEN_CACHE_FILE = path.join(__dirname, 'dxxw_token_cache.json');

const maxReadCount = 15; // 每天最多阅读篇数
const maxLikeCount = 8; // 每天最多点赞篇数
const maxShareCount = 8; // 每天最多分享次数

// 微剧打卡签到（兑吧活动页）
const ENABLE_WEIJU_SIGN = true; // false可关闭微剧签到
const WEIJU_SIGN_OPERATING_ID = (process.env.dxxw_weiju_sign_id || '330057576068731').trim();
const WEIJU_WEB_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148';
const AXIOS_COMMON_OPTS = {
    timeout: 15000,
    maxBodyLength: Infinity,
    maxContentLength: Infinity
};

function addNotifyStr(str, is_log = true) {
    if (is_log) console.log(str);
    msg += `${str}\n`;
}

async function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function getRandom(min, max) {
    return Math.floor(Math.random() * (max - min)) + min;
}

const COMMON_UA = 'DXXW/5.10.2 (iPhone; iOS 26.1; Scale/3.00)';

// ========== 通知功能 ==========

// 发送通知
async function sendNotify(title, content) {
    if (!ENABLE_NOTIFY) {
        return;
    }
    
    console.log(`\n📢 通知: ${title}\n${content}`);
    
    // 如果有青龙面板的通知环境变量，使用青龙通知
    try {
        // 尝试加载青龙面板的通知模块
        const notify = require('./sendNotify');
        await notify.sendNotify(title, content);
    } catch (e) {
        // 如果没有青龙面板，只在控制台显示
        console.log(`(通知功能需要青龙面板环境)`);
    }
}

// ========== Token缓存管理 ==========

// 读取缓存的token
function loadTokenCache() {
    try {
        if (fs.existsSync(TOKEN_CACHE_FILE)) {
            const data = fs.readFileSync(TOKEN_CACHE_FILE, 'utf8');
            return JSON.parse(data);
        }
    } catch (e) {
        console.log(`读取token缓存失败: ${e.message}`);
    }
    return {};
}

// 保存token到缓存（同时缓存 alipay / realname，便于下次抽奖直接拿到提现信息）
function saveTokenCache(username, tokenData, extra = {}) {
    try {
        let cache = loadTokenCache();
        const old = cache[username] || {};
        cache[username] = {
            access_token: tokenData.access_token,
            refresh_token: tokenData.refresh_token,
            expires_in: tokenData.expires_in,
            token_type: tokenData.token_type,
            scope: tokenData.scope,
            saved_time: Date.now(),
            // 保留之前缓存里的 alipay/realname；新值优先
            alipay: extra.alipay || old.alipay || '',
            realname: extra.realname || old.realname || ''
        };
        fs.writeFileSync(TOKEN_CACHE_FILE, JSON.stringify(cache, null, 2), 'utf8');
        console.log(`✅ Token已缓存到文件`);
    } catch (e) {
        console.log(`保存token缓存失败: ${e.message}`);
    }
}

// 把 alipay / realname 单独写回缓存（环境变量里有就更新，没有就保留旧值）
function updateAlipayCache(username, alipay, realname) {
    if (!alipay && !realname) return;
    try {
        let cache = loadTokenCache();
        if (!cache[username]) return;
        if (alipay) cache[username].alipay = alipay;
        if (realname) cache[username].realname = realname;
        fs.writeFileSync(TOKEN_CACHE_FILE, JSON.stringify(cache, null, 2), 'utf8');
    } catch (e) { /* ignore */ }
}

// 从缓存读取支付宝信息（环境变量没填时回退用这个）
function getCachedAlipay(username) {
    const cache = loadTokenCache();
    if (cache[username]) {
        return { alipay: cache[username].alipay || '', realname: cache[username].realname || '' };
    }
    return { alipay: '', realname: '' };
}

// 获取缓存的token
function getCachedToken(username) {
    const cache = loadTokenCache();
    if (cache[username]) {
        console.log(`📦 找到缓存的token，尝试使用...`);
        return cache[username].access_token;
    }
    return null;
}

// 验证token是否有效
async function validateToken(token) {
    try {
        const options = {
            method: 'GET',
            url: 'https://integration.hntv.tv/integration/user/integration/info/',
            headers: {
                'Host': 'integration.hntv.tv',
                'Authorization': `Bearer ${token}`,
                'User-Agent': COMMON_UA,
                'Content-Type': 'application/json',
                'Accept': '*/*, application/json'
            }
        };
        const res = await axios.request(options);
        if (res.data && res.data.code === 0) {
            console.log(`✅ Token验证成功，可以使用`);
            return true;
        } else {
            console.log(`❌ Token验证失败: ${JSON.stringify(res.data)}`);
            return false;
        }
    } catch (e) {
        console.log(`❌ Token验证异常: ${e.response ? e.response.status : e.message}`);
        return false;
    }
}

// ========== 登录相关 ==========

async function login(username, password) {
    try {
        console.log(`🔐 开始登录账号: ${username}`);
        const encodedData = Buffer.from(password).toString('base64');
        const pwd1 = Buffer.from(`em${encodedData}`).toString('base64').replace(/=/g, '%3D');

        const options = {
            method: 'POST',
            url: 'https://pubmod.hntv.tv/mobile/uaa-app/oauth/token',
            headers: {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Host': 'pubmod.hntv.tv',
                'User-Agent': COMMON_UA,
                'tenant_id': '1',
                'Accept-Language': 'zh-Hans-CN;q=1',
                'Referer': 'https://pubmod.hntv.tv/app'
            },
            data: `grant_type=password&password=${pwd1}&username=%7B%22authenticationType%22%3A%22mobile%22%2C%22principal%22%3A%22${username}%22%7D`
        };

        const res = await axios.request(options);
        if (res.data && res.data.scope === 'read') {
            console.log(`✅ 登录成功！`);
            return res.data;
        } else {
            addNotifyStr(`[登录失败]: ${JSON.stringify(res.data)}`);
            return null;
        }
    } catch (e) {
        addNotifyStr(`[登录异常]: ${e.response ? JSON.stringify(e.response.data) : e.message}`);
        return null;
    }
}

// 获取有效的token（优先使用缓存，失效则重新登录）
async function getValidToken(username, password, extra = {}) {
    // 0. 把这次环境变量里读到的 alipay/realname 同步到缓存（哪怕缓存 token 还能用也写一次，方便后续读取）
    updateAlipayCache(username, extra.alipay, extra.realname);

    // 1. 尝试使用缓存的token
    let cachedToken = getCachedToken(username);
    if (cachedToken) {
        const isValid = await validateToken(cachedToken);
        if (isValid) {
            addNotifyStr(`✅ 使用缓存Token成功`);
            return cachedToken;
        } else {
            addNotifyStr(`⚠️ 缓存Token已失效，重新登录...`);
        }
    } else {
        console.log(`📭 未找到缓存Token，需要登录`);
    }

    // 2. Token失效或不存在，重新登录
    const loginData = await login(username, password);
    if (!loginData) {
        return null;
    }

    // 3. 保存新token到缓存（连带 alipay/realname 一起）
    saveTokenCache(username, loginData, extra);
    addNotifyStr(`✅ 新Token已保存到缓存`);

    return loginData.access_token;
}

// ========== 业务功能 ==========

async function getPointsInfo(token, isStart = true) {
    try {
        const options = {
            method: 'GET',
            url: 'https://integration.hntv.tv/integration/user/integration/info/',
            headers: {
                'Host': 'integration.hntv.tv',
                'Authorization': `Bearer ${token}`,
                'User-Agent': COMMON_UA,
                'Content-Type': 'application/json',
                'Accept': '*/*, application/json'
            }
        };
        const res = await axios.request(options);
        if (res.data && res.data.code === 0) {
            const result = res.data.result;
            const haveScore = result.haveScore || 0;
            const allScore = result.allScore || 0;
            const usedScore = result.usedScore || 0;
            
            if (isStart) {
                addNotifyStr(`ℹ️ 账号积分: 当前积分[${haveScore}] 总获得[${allScore}] 已使用[${usedScore}]`);
            } else {
                addNotifyStr(`ℹ️ 账号积分: 当前积分[${haveScore}]`);
            }
            return result;
        } else {
            console.log(`查询积分失败: ${JSON.stringify(res.data)}`);
            return null;
        }
    } catch (e) {
        console.log(`查询积分异常: ${e.message}`);
        return null;
    }
}

// 获取任务完成情况
async function getTaskStatus(token) {
    try {
        const options = {
            method: 'GET',
            url: 'https://integration.hntv.tv/integration/user/integration/info/',
            headers: {
                'Host': 'integration.hntv.tv',
                'Authorization': `Bearer ${token}`,
                'User-Agent': COMMON_UA,
                'Content-Type': 'application/json',
                'Accept': '*/*, application/json'
            }
        };
        const res = await axios.request(options);
        
        if (res.data && res.data.code === 0 && res.data.result.userIntegrationDailyAbtainDTOList) {
            const eventList = res.data.result.userIntegrationDailyAbtainDTOList;
            const taskStatus = {};
            
            eventList.forEach(event => {
                taskStatus[event.eventCode] = {
                    name: event.eventName,
                    completed: event.haveFinishedTimes || 0,
                    total: event.eventLimit || 0,
                    remaining: (event.eventLimit || 0) - (event.haveFinishedTimes || 0)
                };
            });
            
            console.log(`\n📋 今日任务完成情况:`);
            Object.keys(taskStatus).forEach(code => {
                const task = taskStatus[code];
                console.log(`  [${code}] ${task.name}: ${task.completed}/${task.total} (剩余${task.remaining}次)`);
            });
            
            return taskStatus;
        }
        return {};
    } catch (e) {
        console.log(`获取任务状态失败: ${e.message}`);
        return {};
    }
}

async function doTask(token, eventCode, articleId, taskName) {
    try {
        const timestamp = Date.now();
        const options = {
            method: 'POST',
            url: `https://integration.hntv.tv/integration/user/integration/add?t=${timestamp}&v=5.10.2`,
            headers: {
                'Host': 'integration.hntv.tv',
                'Authorization': `Bearer ${token}`,
                'User-Agent': COMMON_UA,
                'Content-Type': 'application/json'
            },
            data: {
                articleId: articleId.toString(),
                eventCode: eventCode.toString()
            }
        };
        const res = await axios.request(options);
        if (res.data && (res.data.code === 0 || res.data.success)) {
            addNotifyStr(`✅ [${taskName}] 获得积分: ${res.data.result ? res.data.result : '成功'}`);
            return true;
        } else {
            addNotifyStr(`❌ [${taskName}] 失败: ${res.data.msg || res.data.message || JSON.stringify(res.data)}`);
            return false;
        }
    } catch (e) {
        addNotifyStr(`❌ [${taskName}] 异常: ${e.response ? JSON.stringify(e.response.data) : e.message}`);
        return false;
    }
}

// 获取文章列表
async function getArticleList(token, pageNo = 1) {
    try {
        const timestamp = Date.now();
        const options = {
            method: 'GET',
            url: `https://pubmod.hntv.tv/mobile/cms/articles?t=${timestamp}&v=5.10.2&businessId=DXXWAPP_LY&channelId=1691274444750712834&commentVersion=v2&pageNo=${pageNo}&pageSize=15&tenantId=1&version=v3`,
            headers: {
                'Host': 'pubmod.hntv.tv',
                'Authorization': `Bearer ${token}`,
                'User-Agent': COMMON_UA,
                'tenant_id': '1'
            }
        };
        const res = await axios.request(options);
        if (res.data && res.data.code === 0) {
            // result是对象，包含content数组
            if (res.data.result && res.data.result.content) {
                console.log(`✅ 获取到 ${res.data.result.content.length} 篇文章`);
                return res.data.result.content;
            }
            return [];
        }
        return [];
    } catch (e) {
        console.log(`获取文章列表失败: ${e.message}`);
        return [];
    }
}

// 阅读统计上报
async function statArticle(token, articleId) {
    try {
        const timestamp = Date.now();
        await axios.get(`https://pubmod.hntv.tv/mobile/newcms/statistics/${articleId}?t=${timestamp}&v=5.10.2`, {
            headers: {
                'Host': 'pubmod.hntv.tv',
                'Authorization': `Bearer ${token}`,
                'User-Agent': COMMON_UA,
                'tenant_id': '1'
            }
        });
    } catch (e) { }
}

// 点赞/取消点赞操作
// type: DZ=点赞, QXC=取消点赞 (或者再发一次DZ也会取消)
async function doOperation(token, articleId, type) {
    try {
        const timestamp = Date.now();
        const options = {
            method: 'POST',
            url: `https://pubmod.hntv.tv/dx-bridge/operation?t=${timestamp}&v=5.10.2`,
            headers: {
                'Host': 'pubmod.hntv.tv',
                'Authorization': `Bearer ${token}`,
                'User-Agent': COMMON_UA,
                'tenant_id': '1',
                'Content-Type': 'application/json'
            },
            data: {
                applicationId: "1390195608019869697",
                objectId: articleId.toString(),
                objectInfo: "{}",
                operationType: type,
                objectType: "WZ",
                spm: "大象$##$主编精选$##$精选流$##$详情页"
            }
        };
        const res = await axios.request(options);
        if (res.data && (res.data.code === 0 || res.data.code === -5)) {
            return true;
        } else {
            console.log(`[操作 ${type}] 失败文章: ${articleId} 原因: ${res.data.msg || ''}`);
            return false;
        }
    } catch (e) {
        return false;
    }
}

// ========== 微剧打卡签到（兑吧） ==========

function escapeRegExp(str) {
    return String(str).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function parseDuibaTokenFromScript(tokenScript, tokenKey = '67666cft') {
    // 抓包前端真实逻辑：eval(res.token) 后取 window[key]
    const reg = new RegExp(`window\\['${escapeRegExp(tokenKey)}'\\]\\s*=\\s*\"([a-zA-Z0-9]+)\"`);
    const direct = tokenScript.match(reg);
    if (direct) {
        return direct[1];
    }

    try {
        const ctx = {
            window: {},
            Math,
            Date,
            String,
            Number,
            console: { log: () => {} }
        };
        ctx.window = ctx;
        ctx.eval = (code) => vm.runInContext(code, ctx, { timeout: 2000 });

        vm.createContext(ctx);
        vm.runInContext(tokenScript, ctx, { timeout: 5000 });

        const tk = ctx[tokenKey];
        if (typeof tk === 'string' && /^[a-z0-9]{5,32}$/i.test(tk)) {
            return tk;
        }

        return null;
    } catch (e) {
        return null;
    }
}

function parseDuibaTokenKeyFromPageHtml(pageHtml) {
    try {
        // 取包含“获取token”的script块
        const scripts = [];
        const reg = /<script[^>]*>([\s\S]*?)<\/script>/ig;
        let m;
        while ((m = reg.exec(pageHtml)) !== null) {
            scripts.push(m[1] || '');
        }

        // 优先含特定字样的脚本；否则用最大那块（兑吧把代码塞在最大的混淆 script 里）
        let tokenBlock = scripts.find(s => s.includes('获取token') || s.includes('ctoken/getToken') || s.includes('__8g8Q0kX1'));
        if (!tokenBlock) tokenBlock = scripts.slice().sort((a, b) => b.length - a.length)[0] || '';
        if (!tokenBlock) return null;

        const captured = [];
        const ctx = {
            window: {},
            Math,
            Date,
            String,
            Number,
            document: { getElementById: () => null, querySelector: () => null },
            console: { log: () => {} }
        };
        ctx.window = ctx;
        ctx.eval = (code) => {
            if (typeof code === 'string') captured.push(code);
            return undefined;
        };

        vm.createContext(ctx);
        try { vm.runInContext(tokenBlock, ctx, { timeout: 8000 }); } catch (_) {}

        // 在所有被 eval 的字符串里找 var key='xxxx'
        for (const code of captured) {
            const m = code.match(/var\s+key\s*=\s*['\"]([a-zA-Z0-9_]+)['\"]/);
            if (m) return m[1];
        }
        // 兜底：直接在 block 文本里找
        const direct = tokenBlock.match(/var\s+key\s*=\s*['\"]([a-zA-Z0-9_]+)['\"]/);
        if (direct) return direct[1];
        return null;
    } catch (e) {
        return null;
    }
}

async function getWeijuSignPageHtml(cookie, signOperatingId) {
    const res = await axios.get('https://90580-activity.dexfu.cn/sign/component/page', {
        params: {
            signOperatingId,
            from: 'login',
            spm: '90580.1.1.1'
        },
        headers: {
            'User-Agent': WEIJU_WEB_UA,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Referer': 'https://90580-activity.dexfu.cn/',
            'Cookie': cookie
        },
        timeout: 15000
    });

    return (typeof res.data === 'string') ? res.data : '';
}

function mergeSetCookie(cookieMap, setCookieArr = []) {
    const map = { ...cookieMap };
    for (const item of setCookieArr) {
        const kv = item.split(';')[0] || '';
        const idx = kv.indexOf('=');
        if (idx <= 0) continue;

        const k = kv.slice(0, idx).trim();
        const v = kv.slice(idx + 1).trim();

        if (!k) continue;
        if (v === '') {
            delete map[k];
        } else {
            map[k] = v;
        }
    }
    return map;
}

function cookieMapToString(cookieMap) {
    return Object.entries(cookieMap)
        .filter(([k, v]) => k && v !== undefined && v !== null && v !== '')
        .map(([k, v]) => `${k}=${v}`)
        .join('; ');
}

async function getWeijuSignCookie(token, signOperatingId) {
    const dbredirect = `https://90580-activity.dexfu.cn/sign/component/page?signOperatingId=${signOperatingId}`;
    const autoLoginUrlApi = `https://integration.hntv.tv/integration/p/duiba/autoLoginUrl?dbredirect=${encodeURIComponent(dbredirect)}`;

    const res = await axios.get(autoLoginUrlApi, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'User-Agent': WEIJU_WEB_UA,
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://static.hntv.tv',
            'Referer': 'https://static.hntv.tv/'
        },
        timeout: 15000
    });

    if (!(res.data && (res.data.code === 0 || res.data.success) && res.data.result)) {
        throw new Error(`获取兑吧自动登录地址失败: ${JSON.stringify(res.data)}`);
    }

    const autoLoginUrl = res.data.result;

    // 需要把整条重定向链上的cookie合并起来，不能只取第一跳
    const cookieMap = {};

    const step1 = await axios.get(autoLoginUrl, {
        headers: {
            'User-Agent': WEIJU_WEB_UA,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        },
        maxRedirects: 0,
        validateStatus: status => status >= 200 && status < 400,
        timeout: 15000
    });

    let merged = mergeSetCookie(cookieMap, step1.headers['set-cookie'] || []);
    let nextUrl = step1.headers.location || '';

    // 最多再追2跳，持续合并cookie
    for (let i = 0; i < 2 && nextUrl; i++) {
        const step = await axios.get(nextUrl, {
            headers: {
                'User-Agent': WEIJU_WEB_UA,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Cookie': cookieMapToString(merged)
            },
            maxRedirects: 0,
            validateStatus: status => status >= 200 && status < 400,
            timeout: 15000
        });

        merged = mergeSetCookie(merged, step.headers['set-cookie'] || []);
        nextUrl = step.headers.location || '';
    }

    const cookie = cookieMapToString(merged);
    if (!cookie) {
        throw new Error('未拿到兑吧cookie（合并后为空）');
    }

    return cookie;
}

async function getWeijuSignIndex(cookie, signOperatingId) {
    const res = await axios.get('https://90580-activity.dexfu.cn/sign/component/index', {
        params: {
            signOperatingId,
            preview: 'false',
            _: Date.now()
        },
        headers: {
            'User-Agent': WEIJU_WEB_UA,
            'Accept': 'application/json, text/plain, */*',
            'Referer': `https://90580-activity.dexfu.cn/sign/component/page?signOperatingId=${signOperatingId}&from=login&spm=90580.1.1.1`,
            'Cookie': cookie
        },
        timeout: 15000
    });

    if (!(res.data && res.data.success && res.data.data)) {
        throw new Error(`查询微剧签到状态失败: ${JSON.stringify(res.data)}`);
    }

    return res.data.data;
}

async function getWeijuCtoken(cookie, signOperatingId) {
    // 第一步：从活动页脚本解析当前期真实tokenKey（不是固定67666cft）
    const pageHtml = await getWeijuSignPageHtml(cookie, signOperatingId);
    const tokenKey = parseDuibaTokenKeyFromPageHtml(pageHtml) || '67666cft';

    const res = await axios.post(
        'https://90580-activity.dexfu.cn/chw/ctoken/getToken',
        `timestamp=${Date.now()}`,
        {
            headers: {
                'User-Agent': WEIJU_WEB_UA,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': '*/*',
                'Origin': 'https://90580-activity.dexfu.cn',
                'Referer': `https://90580-activity.dexfu.cn/sign/component/page?signOperatingId=${signOperatingId}&from=login&spm=90580.1.1.1`,
                'Cookie': cookie
            },
            timeout: 15000
        }
    );

    if (!(res.data && res.data.success && res.data.token)) {
        throw new Error(`获取微剧ctoken失败: ${JSON.stringify(res.data)}`);
    }

    const tk = parseDuibaTokenFromScript(res.data.token, tokenKey);
    if (!tk) {
        throw new Error(`解析ctoken脚本失败：未拿到 window[${tokenKey}]`);
    }

    return { token: tk, tokenKey };
}

// 9天抽奖触发：POST /sign/component/doJoin
// 返回：{ success:true, data:{ times, orderNum } }
async function doWeijuJoin(cookie, signOperatingId, ctoken) {
    const body = new URLSearchParams({
        signOperatingId: String(signOperatingId),
        token: ctoken
    }).toString();

    const res = await axios.post(
        `https://90580-activity.dexfu.cn/sign/component/doJoin?_=${Date.now()}`,
        body,
        {
            headers: {
                'User-Agent': WEIJU_WEB_UA,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json, text/plain, */*',
                'Origin': 'https://90580-activity.dexfu.cn',
                'Referer': `https://90580-activity.dexfu.cn/sign/component/page?signOperatingId=${signOperatingId}&from=login&spm=90580.1.1.1`,
                'Cookie': cookie
            },
            timeout: 15000
        }
    );
    return (res && typeof res.data !== 'undefined') ? res.data : null;
}

// 用 doJoin 返回的 orderNum 反查中奖记录，从 lottery.link 里抠出 recordId
async function getLotteryRecordId(cookie, signOperatingId, orderNum) {
    const res = await axios.get(
        `https://90580-activity.dexfu.cn/plugin/getOrderStatus`,
        {
            params: { orderId: orderNum, _: Date.now() },
            headers: {
                'User-Agent': WEIJU_WEB_UA,
                'Accept': 'application/json, text/plain, */*',
                'Referer': `https://90580-activity.dexfu.cn/sign/component/page?signOperatingId=${signOperatingId}&from=login&spm=90580.1.1.1`,
                'Cookie': cookie
            },
            timeout: 15000
        }
    );
    const data = res && res.data;
    if (!(data && data.success && data.lottery && data.lottery.link)) {
        throw new Error(`查询中奖记录失败: ${JSON.stringify(data)}`);
    }
    const m = String(data.lottery.link).match(/recordId=(\d+)/);
    if (!m) throw new Error(`lottery.link 里没找到 recordId: ${data.lottery.link}`);
    return {
        recordId: m[1],
        prizeTitle: data.lottery.title || '',
        prizeType: data.lottery.type || ''
    };
}

// 模拟用户从"中奖记录"页点进领奖页的行为：访问 /crecord/record 并打 click 埋点
async function warmupBeforeTakePrize(cookie) {
    // 1) 访问中奖记录页
    await axios.get('https://90580-activity.dexfu.cn/crecord/record?dbnewopen', {
        headers: {
            'User-Agent': WEIJU_WEB_UA,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Cookie': cookie
        },
        timeout: 15000,
        validateStatus: () => true
    });
    // 2) 拉一次 record 列表（兑吧前端会调）
    await axios.get(`https://90580-activity.dexfu.cn/crecord/getrecord?page=1&_=${Date.now()}`, {
        headers: {
            'User-Agent': WEIJU_WEB_UA,
            'Accept': 'application/json, text/plain, */*',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://90580-activity.dexfu.cn/crecord/record?dbnewopen',
            'Cookie': cookie
        },
        timeout: 15000,
        validateStatus: () => true
    });
    // 3) 打 click 埋点（这步可能是服务端校验"用户点过提现"的关键）
    await axios.get('https://90580-activity.dexfu.cn/log/click', {
        params: {
            dpm: '90580.26.0.1',
            domain: '//90580-activity.dexfu.cn',
            dcm: '102.214709196407064.0.0',
            appId: '90580'
        },
        headers: {
            'User-Agent': WEIJU_WEB_UA,
            'Accept': '*/*',
            'Referer': 'https://90580-activity.dexfu.cn/crecord/record?dbnewopen',
            'Cookie': cookie
        },
        timeout: 15000,
        validateStatus: () => true
    });
}

// 从 takePrize 页面 HTML 解析出 ctoken 用的 tokenKey（页面里有 var key="xxxxx"）
async function getTakePrizePageTokenKey(cookie, recordId) {
    const r = await axios.get(
        `https://90580-activity.dexfu.cn/activity/takePrizeNew?recordId=${recordId}&dpm=90580.26.0.1&dcm=102.214709196407064.0.0&dbnewopen`,
        {
            headers: {
                'User-Agent': WEIJU_WEB_UA,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Cookie': cookie
            },
            timeout: 15000
        }
    );
    const html = (typeof r.data === 'string') ? r.data : '';
    // 兑吧标准模板：每个 takePrize 页都会有一段含 "获取token" / "ctoken/getToken" 的 script，
    // 里头会 eval 一个"var key='xxxxx';..."字符串
    return parseDuibaTokenKeyFromPageHtml(html);
}

// 提现页专用 ctoken：POST /ctoken/getToken.do（注意路径跟签到那个不一样）
async function getTakePrizeCtoken(cookie, recordId) {
    // 1) 先去拿到本期 tokenKey（拿不到就用枚举 fallback）
    let tokenKey = null;
    try { tokenKey = await getTakePrizePageTokenKey(cookie, recordId); } catch (e) { /* fallthrough */ }

    const res = await axios.post(
        `https://90580-activity.dexfu.cn/ctoken/getToken.do`,
        '',
        {
            headers: {
                'User-Agent': WEIJU_WEB_UA,
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json',
                'Origin': 'https://90580-activity.dexfu.cn',
                'Referer': `https://90580-activity.dexfu.cn/activity/takePrizeNew?recordId=${recordId}&dpm=90580.26.0.1&dcm=102.214709196407064.0.0&dbnewopen`,
                'Cookie': cookie
            },
            timeout: 15000
        }
    );
    if (!(res.data && res.data.success && res.data.token)) {
        throw new Error(`获取领奖ctoken失败: ${JSON.stringify(res.data)}`);
    }

    // 2) 优先按精确 tokenKey 解析
    if (tokenKey) {
        const v = parseDuibaTokenFromScript(res.data.token, tokenKey);
        if (v) return v;
    }
    // 3) fallback：跑完后枚举像 token 的字符串
    const v2 = evalAndExtractDuibaToken(res.data.token);
    if (v2) return v2;
    throw new Error('解析领奖ctoken失败');
}

// 通用：把兑吧返回的 token 脚本跑一遍，扫所有看起来像 token 的字符串值（5~32位字母数字）
function evalAndExtractDuibaToken(tokenScript) {
    try {
        const ctx = {
            window: {},
            Math, Date, String, Number,
            console: { log: () => {} }
        };
        ctx.window = ctx;
        ctx.eval = (code) => vm.runInContext(code, ctx, { timeout: 2000 });

        vm.createContext(ctx);
        vm.runInContext(tokenScript, ctx, { timeout: 8000 });

        // 优先 window 上的字符串属性，跳过我们自己注入的内置对象
        const skip = new Set(['window', 'Math', 'Date', 'String', 'Number', 'console', 'eval']);
        const re = /^[a-z0-9]{5,32}$/i;
        for (const k of Object.keys(ctx)) {
            if (skip.has(k)) continue;
            const v = ctx[k];
            if (typeof v === 'string' && re.test(v)) return v;
        }
        return null;
    } catch (e) {
        return null;
    }
}

// 提现：POST /activity/doTakePrize
async function doTakePrize(cookie, recordId, alipay, realname, ctoken) {
    const body = new URLSearchParams({
        alipay,
        realname,
        recordId: String(recordId),
        token: ctoken
    }).toString();
    const res = await axios.post(
        `https://90580-activity.dexfu.cn/activity/doTakePrize`,
        body,
        {
            headers: {
                'User-Agent': WEIJU_WEB_UA,
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'Origin': 'https://90580-activity.dexfu.cn',
                'Referer': `https://90580-activity.dexfu.cn/activity/takePrizeNew?recordId=${recordId}&dpm=90580.26.0.1&dcm=102.214709196407064.0.0&dbnewopen`,
                'Cookie': cookie
            },
            timeout: 15000
        }
    );
    return res && res.data;
}

async function doWeijuSign(cookie, signOperatingId, ctoken) {
    const body = new URLSearchParams({
        signOperatingId: String(signOperatingId),
        token: ctoken
    }).toString();

    const res = await axios.post(
        `https://90580-activity.dexfu.cn/sign/component/doSign?_=${Date.now()}`,
        body,
        {
            headers: {
                'User-Agent': WEIJU_WEB_UA,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json, text/plain, */*',
                'Origin': 'https://90580-activity.dexfu.cn',
                'Referer': `https://90580-activity.dexfu.cn/sign/component/page?signOperatingId=${signOperatingId}&from=login&spm=90580.1.1.1`,
                'Cookie': cookie
            },
            timeout: 15000
        }
    );

    return (res && typeof res.data !== 'undefined') ? res.data : null;
}

// 抽奖+提现：在签到完成后调用。alipay/realname 任一为空就只抽奖、不提现；都为空则连抽奖都不做
async function doWeijuLotteryAndTakePrize(cookie, signOperatingId, indexData, alipay, realname) {
    // index.times 表示当前可抽奖次数；为 0 直接跳过
    const times = (indexData && typeof indexData.times === 'number') ? indexData.times : 0;
    // 不管有没有新抽奖机会，先扫一遍历史"待领奖"的奖品试着领（救之前失败的记录）
    try { await scanAndClaimPendingPrizes(cookie, alipay, realname); } catch (_) {}

    if (times <= 0) {
        addNotifyStr(`ℹ️ 微剧抽奖次数: 0，本次无新抽奖资格（不到9天）`);
        return;
    }
    if (!alipay || !realname) {
        addNotifyStr(`⏭️  抽奖剩余 ${times} 次，但未配置支付宝账号/姓名 → 跳过抽奖`);
        return;
    }

    addNotifyStr(`🎁 检测到 ${times} 次抽奖资格，开始抽奖...`);

    // 1) 取 ctoken（同签到那套 chw/ctoken/getToken）
    const ctokenInfo = await getWeijuCtoken(cookie, signOperatingId);
    let ctoken = ctokenInfo.token;

    // 2) doJoin 抽奖
    let joinRes;
    try {
        joinRes = await doWeijuJoin(cookie, signOperatingId, ctoken);
    } catch (e) {
        addNotifyStr(`⚠️ 抽奖请求异常，重新拉ctoken重试: ${e.message}`);
        ctoken = (await getWeijuCtoken(cookie, signOperatingId)).token;
        joinRes = await doWeijuJoin(cookie, signOperatingId, ctoken);
    }
    if (!(joinRes && joinRes.success && joinRes.data && joinRes.data.orderNum)) {
        addNotifyStr(`❌ 抽奖失败: ${JSON.stringify(joinRes)}`);
        return;
    }
    const orderNum = joinRes.data.orderNum;
    addNotifyStr(`✅ 抽奖完成，orderNum=${orderNum}`);

    // 3) 查中奖记录拿 recordId（兑吧延迟落库，最多重试3次）
    let recordInfo;
    for (let i = 0; i < 3; i++) {
        try {
            recordInfo = await getLotteryRecordId(cookie, signOperatingId, orderNum);
            if (recordInfo && recordInfo.recordId) break;
        } catch (e) {
            if (i === 2) {
                addNotifyStr(`❌ 查中奖记录失败: ${e.message}`);
                return;
            }
        }
        await wait(1500);
    }
    addNotifyStr(`🎯 中奖: ${recordInfo.prizeTitle}（${recordInfo.prizeType}），recordId=${recordInfo.recordId}`);

    // 4) 兑吧服务端要求：奖品要"在中奖记录里能查到"才能领（doJoin 后入库有延迟，最久能到几十秒）
    //    轮询 /crecord/getrecord 直到看到这个 recordId 出现且状态可领，再去领
    const ok = await waitUntilRecordReady(cookie, recordInfo.recordId, 30);
    if (!ok) {
        addNotifyStr(`⏭️  recordId=${recordInfo.recordId} 30秒内未在中奖记录里就绪，下次再试`);
        return;
    }

    // 5) 提现（含 ctoken + doTakePrize，最多重试 3 次）
    const finalRes = await tryClaimPrize(cookie, recordInfo.recordId, alipay, realname);
    if (finalRes && finalRes.success) {
        addNotifyStr(`💰 提现成功: ${finalRes.message || '领奖成功'}（recordId=${recordInfo.recordId}, alipay=${alipay}）`);
    } else {
        addNotifyStr(`❌ 提现失败: ${JSON.stringify(finalRes)}`);
    }
}

// 扫描所有"待领奖"的支付宝奖品并尝试领走（用于补救历史未领的）
async function scanAndClaimPendingPrizes(cookie, alipay, realname) {
    if (!alipay || !realname) return;
    let pageRes;
    try {
        pageRes = await axios.get(`https://90580-activity.dexfu.cn/crecord/getrecord?page=1&_=${Date.now()}`, {
            headers: {
                'User-Agent': WEIJU_WEB_UA,
                'Accept': 'application/json, text/plain, */*',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://90580-activity.dexfu.cn/crecord/record?dbnewopen',
                'Cookie': cookie
            },
            timeout: 15000
        });
    } catch (e) { return; }
    const records = (pageRes.data && pageRes.data.records) || [];
    const pending = records.filter(r => /待领奖/.test(String(r.statusText || '')) && /takePrizeNew/.test(String(r.url || '')));
    if (!pending.length) return;
    addNotifyStr(`🔎 发现 ${pending.length} 条待领奖品，尝试自动领取...`);
    for (const r of pending) {
        const m = String(r.url).match(/recordId=(\d+)/);
        if (!m) continue;
        const recId = m[1];
        const res = await tryClaimPrize(cookie, recId, alipay, realname);
        if (res && res.success) {
            addNotifyStr(`💰 历史奖品领取成功: ${r.title}（recordId=${recId}）`);
        } else {
            addNotifyStr(`⏭️  recordId=${recId} 暂不可领: ${(res && res.message) || '未知'}`);
        }
        await wait(2000);
    }
}

// 拉 /crecord/getrecord 看这条 recordId 是否已经入库且状态待领；最多 maxSec 秒
async function waitUntilRecordReady(cookie, recordId, maxSec = 30) {
    const deadline = Date.now() + maxSec * 1000;
    let tried = 0;
    while (Date.now() < deadline) {
        tried++;
        try {
            // warmup once at the start (record page + log/click 埋点)
            if (tried === 1) {
                try { await warmupBeforeTakePrize(cookie); } catch (_) {}
            }
            const r = await axios.get(`https://90580-activity.dexfu.cn/crecord/getrecord?page=1&_=${Date.now()}`, {
                headers: {
                    'User-Agent': WEIJU_WEB_UA,
                    'Accept': 'application/json, text/plain, */*',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': 'https://90580-activity.dexfu.cn/crecord/record?dbnewopen',
                    'Cookie': cookie
                },
                timeout: 15000
            });
            const records = (r.data && r.data.records) || [];
            const hit = records.find(it => String(it.url || '').includes(`recordId=${recordId}`));
            if (hit) return true;
        } catch (_) {}
        await wait(2000);
    }
    return false;
}

// 真正提现：拿 ctoken → POST /activity/doTakePrize；遇到 (24) 重试
async function tryClaimPrize(cookie, recordId, alipay, realname) {
    let lastRes = null;
    for (let i = 0; i < 3; i++) {
        let prizeCtoken;
        try {
            prizeCtoken = await getTakePrizeCtoken(cookie, recordId);
        } catch (e) {
            addNotifyStr(`⚠️ 领奖ctoken获取失败 (第${i + 1}次): ${e.message}`);
            await wait(3000);
            continue;
        }
        const res = await doTakePrize(cookie, recordId, alipay, realname, prizeCtoken);
        lastRes = res;
        if (res && res.success) return res;
        // 失败：log 一次，等会儿重试
        addNotifyStr(`⚠️ 提现第 ${i + 1} 次失败: ${JSON.stringify(res)} (token=${prizeCtoken})`);
        await wait(5000);
    }
    return lastRes;
}

async function doWeijuSignTask(token, alipay = '', realname = '') {
    if (!ENABLE_WEIJU_SIGN) {
        console.log('⏭️  微剧打卡签到已关闭');
        return;
    }

    const signOperatingId = WEIJU_SIGN_OPERATING_ID;

    try {
        addNotifyStr(`\n🎬 开始微剧打卡签到（9天抽奖）...`);

        const cookie = await getWeijuSignCookie(token, signOperatingId);

        const before = await getWeijuSignIndex(cookie, signOperatingId);
        const beforeTotal = before.totalCount || 0;
        const beforeTarget = before.targetCount || 0;

        addNotifyStr(`ℹ️ 微剧打卡进度: ${beforeTotal}/${beforeTarget}，标题: ${before.title || '未知活动'}`);

        // signResult=true 时表示今天已签：仍尝试一次抽奖（可能9天已满还没领）
        if (before.signResult === true) {
            addNotifyStr(`⏭️  微剧签到今日已完成`);
            try {
                await doWeijuLotteryAndTakePrize(cookie, signOperatingId, before, alipay, realname);
            } catch (e) {
                addNotifyStr(`❌ 抽奖/提现流程异常: ${e.message}`);
            }
            return;
        }

        const ctokenInfo = await getWeijuCtoken(cookie, signOperatingId);
        const ctoken = ctokenInfo.token;
        const tokenKey = ctokenInfo.tokenKey;
        addNotifyStr(`ℹ️ 微剧ctoken: ${ctoken} (key:${tokenKey})`);

        let signRes = null;
        let usedToken = ctoken;
        let usedKey = tokenKey;

        try {
            signRes = await doWeijuSign(cookie, signOperatingId, ctoken);
        } catch (e) {
            addNotifyStr(`⚠️ 微剧签到请求异常(token:${ctoken}): ${e.message}`);
            signRes = null;
        }

        // 如果返回为空，按抓包实际流程：重新拉一次ctoken再试一次
        if (!signRes || typeof signRes !== 'object') {
            addNotifyStr(`⚠️ 微剧签到首次返回空结果，重新获取ctoken重试一次`);
            const ctokenInfo2 = await getWeijuCtoken(cookie, signOperatingId);
            const ctoken2 = ctokenInfo2.token;
            usedToken = ctoken2;
            usedKey = ctokenInfo2.tokenKey;
            try {
                signRes = await doWeijuSign(cookie, signOperatingId, ctoken2);
            } catch (e) {
                addNotifyStr(`⚠️ 微剧签到重试异常(token:${ctoken2}): ${e.message}`);
                signRes = null;
            }
        }

        if (!(signRes && signRes.success && signRes.data)) {
            addNotifyStr(`❌ 微剧签到失败: ${JSON.stringify(signRes || { msg: 'doSign返回空或非JSON对象', token: usedToken, tokenKey: usedKey })}`);
            return;
        }

        const signResult = signRes.data.signResult;
        const orderNum = signRes.data.orderNum || '';

        // 100: 成功提交；可再查一次进度确认
        let afterIndex = null;
        if (signResult === 100 || signResult === 2 || signResult === 1) {
            afterIndex = await getWeijuSignIndex(cookie, signOperatingId);
            addNotifyStr(`✅ 微剧签到成功: 进度 ${afterIndex.totalCount || 0}/${afterIndex.targetCount || 0}（orderNum:${orderNum || '无'}，token:${usedToken || '未知'}，key:${usedKey || '未知'}）`);
        } else {
            addNotifyStr(`⚠️ 微剧签到返回异常状态: signResult=${signResult} 原始=${JSON.stringify(signRes.data)}`);
        }

        // 签完检查是否够9天有抽奖资格 → 抽奖+提现
        try {
            if (!afterIndex) afterIndex = await getWeijuSignIndex(cookie, signOperatingId);
            await doWeijuLotteryAndTakePrize(cookie, signOperatingId, afterIndex, alipay, realname);
        } catch (e) {
            addNotifyStr(`❌ 抽奖/提现流程异常: ${e.message}`);
        }
    } catch (e) {
        addNotifyStr(`❌ 微剧签到异常: ${e.message}`);
    }
}

// ========== 单个账号任务执行 ==========

async function executeAccount(accountInfo, index) {
    const username = accountInfo[0];
    const password = accountInfo[1];
    // 账号格式：账号&密码&支付宝账号&姓名（后两项可选；缺则不抽奖、不提现）
    let alipay = (accountInfo[2] || '').trim();
    let realname = (accountInfo[3] || '').trim();

    addNotifyStr(`\n==== 开始【第 ${index + 1} 个账号: ${username}】====`);

    // 使用新的token获取方法（优先缓存，失效则登录），同时把 alipay/realname 写入缓存
    const token = await getValidToken(username, password, { alipay, realname });
    if (!token) {
        addNotifyStr(`❌ 无法获取有效Token，跳过该账号`);
        return;
    }

    // 1. 查询初始积分和任务状态
    const startInfo = await getPointsInfo(token, true);
    const startScore = startInfo ? startInfo.haveScore : 0;
    const taskStatus = await getTaskStatus(token);

    // 1.5 微剧打卡签到 + 9天抽奖 + 提现（与主积分任务并行存在）
    // 环境变量没填 alipay/realname 时回退用缓存里的（之前填过保留下来的）
    if (!alipay || !realname) {
        const cached = getCachedAlipay(username);
        if (!alipay) alipay = cached.alipay;
        if (!realname) realname = cached.realname;
    }
    await doWeijuSignTask(token, alipay, realname);
    await wait(getRandom(1200, 2200));

    // 2. 每日签到 (eventCode: 3)
    if (taskStatus['3'] && taskStatus['3'].remaining > 0) {
        await doTask(token, 3, "1", "每日签到");
        await wait(getRandom(2000, 3000));
    } else {
        console.log(`⏭️  每日签到已完成，跳过`);
    }

    // 3. App使用时长 (eventCode: 24)
    if (taskStatus['24'] && taskStatus['24'].remaining > 0) {
        await doTask(token, 24, "1", "使用时长(5min)");
        await wait(getRandom(2000, 3000));
    } else {
        console.log(`⏭️  使用时长已完成，跳过`);
    }

    // 4. 计算需要完成的任务数量
    const needReadCount = taskStatus['26'] ? Math.min(taskStatus['26'].remaining, maxReadCount) : 0;  // 浏览内容
    const needLikeCount = taskStatus['11'] ? Math.min(taskStatus['11'].remaining, maxLikeCount) : 0;   // 点赞
    const needShareCount = taskStatus['9'] ? Math.min(taskStatus['9'].remaining, maxShareCount) : 0;   // 分享

    console.log(`\n📝 本次需要完成: 阅读[${needReadCount}] 点赞[${needLikeCount}] 分享[${needShareCount}]`);

    if (needReadCount === 0 && needLikeCount === 0 && needShareCount === 0) {
        console.log(`✅ 所有任务已完成，无需执行`);
        await getPointsInfo(token, false);
        return;
    }

    // 5. 获取文章列表进行阅读、点赞和分享
    let articles = [];
    let page = 1;
    const totalNeeded = Math.max(needReadCount, needLikeCount, needShareCount);
    console.log(`\n开始获取文章列表...`);
    
    // 获取更多页面的文章，避免重复
    const maxPages = 10; // 增加到10页
    while (articles.length < totalNeeded * 2 && page <= maxPages) {
        let list = await getArticleList(token, page);
        if (list.length > 0) {
            articles = articles.concat(list);
        } else {
            break; // 没有更多文章了
        }
        page++;
        await wait(1000);
    }

    // 去重：根据文章ID去重
    const uniqueArticles = [];
    const seenIds = new Set();
    for (let article of articles) {
        if (article && article.id && !seenIds.has(article.id)) {
            seenIds.add(article.id);
            uniqueArticles.push(article);
        }
    }
    
    articles = uniqueArticles;
    console.log(`✅ 共获取 ${articles.length} 篇不重复文章`);

    let readCount = 0;
    let likeCount = 0;
    let shareCount = 0;

    for (let j = 0; j < articles.length; j++) {
        if (readCount >= needReadCount && likeCount >= needLikeCount && shareCount >= needShareCount) break;

        let article = articles[j];
        let articleId = article.id;
        let title = article.title ? article.title.substring(0, 10) + '..' : articleId;

        console.log(`\n--- 处理文章 [${title}] ID:${articleId} ---`);

        // 模拟阅读 (eventCode: 26 浏览内容)
        if (readCount < needReadCount) {
            await statArticle(token, articleId);
            await wait(getRandom(5000, 8000)); // 增加等待时间，模拟真实阅读
            let readRes = await doTask(token, 26, articleId, "浏览内容");
            if (readRes) readCount++;
            await wait(getRandom(2000, 3000)); // 额外等待
        }

        // 模拟分享 (eventCode: 9)
        if (shareCount < needShareCount) {
            await wait(getRandom(1000, 2000));
            let shareRes = await doTask(token, 9, articleId, "分享文章");
            if (shareRes) shareCount++;
        }

        // 模拟点赞并取消 (eventCode: 11)
        if (likeCount < needLikeCount) {
            await wait(getRandom(1000, 2000));
            console.log(`  -> 尝试点赞...`);
            let opRes = await doOperation(token, articleId, 'DZ');
            if (opRes) {
                let likeRes = await doTask(token, 11, articleId, "点赞文章");
                if (likeRes) likeCount++;

                // 等待一会儿后取消点赞
                await wait(getRandom(2000, 3000));
                console.log(`  -> 尝试取消点赞...`);
                await doOperation(token, articleId, 'QXDZ');
            }
        }
    }

    console.log(`\n今日任务统计：阅读[${readCount}/${needReadCount}] 点赞[${likeCount}/${needLikeCount}] 分享[${shareCount}/${needShareCount}]`);

    // 6. 任务结束后再次查询积分
    const endInfo = await getPointsInfo(token, false);
    const endScore = endInfo ? endInfo.haveScore : 0;
    const earnedScore = endScore - startScore;
    if (earnedScore > 0) {
        addNotifyStr(`🎉 本次获得积分: +${earnedScore}`);
    }
}

// ========== 主程序 ==========

async function start() {
    if (!dxxwhd) {
        console.log(`未找到环境变量 dxxwhd，请设置。格式: 账号&密码`);
        return;
    }
    if (dxxwhd.indexOf('@') > -1) {
        dxxwhdArr = dxxwhd.split('@');
    } else if (dxxwhd.indexOf('\n') > -1) {
        dxxwhdArr = dxxwhd.split('\n');
    } else {
        dxxwhdArr = [dxxwhd];
    }

    console.log(`\n=================== 共找到 ${dxxwhdArr.length} 个账号 ===================`);
    console.log(`执行模式: ${ENABLE_CONCURRENT ? '并发模式 🚀' : '顺序模式 ⏭️'}`);

    const accounts = dxxwhdArr.map(item => item.split('&'));

    if (ENABLE_CONCURRENT) {
        // 并发模式：所有账号同时执行
        console.log(`\n🚀 开始并发执行所有账号任务...\n`);
        await Promise.all(accounts.map((account, index) => executeAccount(account, index)));
    } else {
        // 顺序模式：一个账号执行完再执行下一个
        for (let i = 0; i < accounts.length; i++) {
            await executeAccount(accounts[i], i);
        }
    }

    console.log(`\n🎉 所有账号任务执行完毕！`);
    
    // 发送通知
    if (ENABLE_NOTIFY && msg) {
        await sendNotify('大象新闻积分任务', msg);
    }
}

start();
