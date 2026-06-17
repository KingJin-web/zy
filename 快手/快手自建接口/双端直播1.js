const axios = require("axios");
const axios = require("axios");
console.log("自定义接口搭建教程 https://mp.weixin.qq.com/s/QCpnK8scCmG69lLm3xg9XA")
console.log("最低2.1代理，4.5家庭住宅 http://www.gzsk5.com/#/register?invitation=hnking2&shareid=516")
// ==============================================
// 签名服务地址（可通过环境变量覆盖）
// ==============================================
const SIGN_API_KUAISHOU = process.env.kspt_api || "http://119.29.213.95:7779";
const SIGN_API_NEBULA = process.env.ksjs_api || "http://119.29.213.95:7778";

const DEFAULT_TASKS_STR = process.env.KS_DEFAULT_TASKS || "live,lives";
const TASKS_TO_RUN = DEFAULT_TASKS_STR.split(",").map(s => s.trim()).filter(Boolean);

const MAX_LIVES = parseInt(process.env.KS_MAX_LIVES) || 999999;
const MAX_CONCURRENT_ACCOUNTS = parseInt(process.env.KS_MAX_CONCURRENT) || 66;

// 间隔 1-3 秒
const MIN_DELAY_SEC = 1;
const MAX_DELAY_SEC = 3;

function randomDelaySeconds() {
    return Math.floor(Math.random() * (MAX_DELAY_SEC - MIN_DELAY_SEC + 1) + MIN_DELAY_SEC);
}
function randomDelay() {
    const seconds = randomDelaySeconds();
    return new Promise(resolve => setTimeout(resolve, seconds * 1000));
}

// 繁忙/签名相关常量
const MAX_BUSY_INITIAL = 2;      // 初始任务繁忙2次后停止该任务
const MAX_BUSY_APPEND = 3;       // 追加任务繁忙3次后休息5分钟再继续
const APPEND_BUSY_BREAK_MS = 5 * 60 * 1000; // 5分钟
const MAX_SIGN_FAILURES = 3;     // 签名失败3次后停止该账号

// ==================== 平台配置与双端识别 ====================
const PLATFORM_CONFIG = {
    KUAISHOU: {
        name: "KS",
        host: "encourage.kuaishou.com",
        appId: "kuaishou",
        packageName: "com.smile.gifmaker",
        appName: "快手",
        displayName: "普通版",
        kpn: "KUAISHOU",
        adClientKey: "3c2cd3f3",
        reportClientKey: "3c2cd3f3"
    },
    NEBULA: {
        name: "JSB",
        host: "nebula.kuaishou.com",
        appId: "kuaishou_nebula",
        packageName: "com.kuaishou.nebula",
        appName: "快手极速版",
        displayName: "极速版",
        kpn: "NEBULA",
        adClientKey: "2ac2a76d",
        reportClientKey: "2ac2a76d"
    }
};

function identifyPlatform(cookie) {
    const match = cookie.match(/kpn=([^;]+)/);
    const kpn = match ? match[1].toUpperCase() : "KUAISHOU";
    return kpn === "NEBULA" ? PLATFORM_CONFIG.NEBULA : PLATFORM_CONFIG.KUAISHOU;
}

// ==================== 统一设备参数（基础模板） ====================
const DEFAULT_DEVICE_PARAMS_UNIFIED = {
    earphoneMode: "1",
    mod: "OnePlus(PKX110)",
    appver: "14.3.30.11384",
    isp: "CMCC",
    language: "zh-cn",
    did_tag: "0",
    thermal: "10000",
    net: "5G",
    kcv: "1620",
    app: "0",
    kpf: "ANDROID_PHONE",
    bottom_navigation: "true",
    ver: "14.3",
    android_os: "0",
    oDid: "ANDROID_adb1e1653dd085be",
    boardPlatform: "sun",
    newOc: "ANDROID_OPPO__LXCPA_CPA_ZGYXZRGSKSKJ_249561%2C1",
    androidApiLevel: "36",
    slh: "0",
    country_code: "cn",
    nbh: "0",
    hotfix_ver: "",
    keyconfig_state: "2",
    cdid_tag: "2",
    sys: "ANDROID_16",
    max_memory: "256",
    oc: "ANDROID_OPPO__LXCPA_CPA_ZGYXZRGSKSKJ_249561%2C1",
    sh: "2640",
    deviceBit: "4",
    browseType: "3",
    ddpi: "476",
    socName: "Qualcomm%20Snapdragon%208750",
    is_background: "0",
    c: "ANDROID_OPPO__LXCPA_CPA_ZGYXZRGSKSKJ_249561%2C1",
    sw: "1216",
    ftt: "",
    abi: "arm64",
    userRecoBit: "0",
    device_abi: "arm64",
    icaver: "1",
    totalMemory: "15107",
    grant_browse_type: "AUTHORIZED",
    iuid: "",
    rdid: "ANDROID_7bc831446e31ac0a",
    sbh: "135",
    darkMode: "false"
};

let deviceParamsUnified = { ...DEFAULT_DEVICE_PARAMS_UNIFIED };
if (process.env.KS_DEVICE_PARAMS_UNIFIED) {
    try {
        const custom = JSON.parse(process.env.KS_DEVICE_PARAMS_UNIFIED);
        deviceParamsUnified = { ...deviceParamsUnified, ...custom };
        console.log("✅ 已加载自定义统一设备参数");
    } catch(e) { console.warn("⚠️ KS_DEVICE_PARAMS_UNIFIED 解析失败"); }
}

// ==================== 任务配置（普通版与极速版区分） ====================
const TASK_CONFIGS = {
    KUAISHOU: {
        live: { name: "直播广告", businessId: 101, posId: 5226, pageId: 100014023, subPageId: 100014024, requestSceneType: 1, taskType: 1 },
        lives: { name: "直播广告[追加]", businessId: 101, posId: 5226, pageId: 100014023, subPageId: 100014024, requestSceneType: 7, taskType: 2 }
    },
    NEBULA: {
        live: { name: "直播广告", businessId: 75, posId: 2318, pageId: 100012060, subPageId: 100012061, requestSceneType: 1, taskType: 1 },
        lives: { name: "直播广告[追加]", businessId: 75, posId: 2318, pageId: 100012060, subPageId: 100012061, requestSceneType: 7, taskType: 2 }
    }
};

if (process.env.KS_TASK_CONFIG) {
    try {
        const customTasks = JSON.parse(process.env.KS_TASK_CONFIG);
        Object.assign(TASK_CONFIGS.KUAISHOU, customTasks.KUAISHOU || {});
        Object.assign(TASK_CONFIGS.NEBULA, customTasks.NEBULA || {});
        console.log("✅ 已加载自定义任务配置");
    } catch(e) {}
}

function createLogger(remark, platformDisplayName) {
    const prefix = `[${remark}][${platformDisplayName}]`;
    return (msg) => console.log(`${prefix} ${msg}`);
}

function delay(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }
function genRequestId() { return Math.floor(Math.random() * 100000000000000000).toString(); }
function getCurrentTimestampMs() { return Date.now(); }
function getColdLaunchTimeMs() { return Date.now() - 30 * 1000; }

function javaUrlEncode(str) {
    if (str === null || str === undefined) return "";
    let encoded = encodeURIComponent(str);
    return encoded.replace(/!/g, '%21').replace(/'/g, '%27').replace(/\(/g, '%28').replace(/\)/g, '%29').replace(/~/g, '%7E').replace(/\*/g, '%2A');
}

function buildSortedParams(obj) {
    const keys = Object.keys(obj).sort();
    const parts = [];
    for (let key of keys) {
        if (obj[key] !== undefined && obj[key] !== null && obj[key] !== "") {
            parts.push(`${javaUrlEncode(key)}=${javaUrlEncode(obj[key])}`);
        }
    }
    return parts.join('&');
}

function getBase64NoWrap(obj) {
    return Buffer.from(JSON.stringify(obj)).toString('base64').replace(/=+$/, '');
}

async function getNsSign(reqInfo, kpnType, remark, logFn) {
    const SIGN_API_URL = kpnType === "NEBULA" ? SIGN_API_NEBULA : SIGN_API_KUAISHOU;
    try {
        const payload = { path: reqInfo.urlpath, data: reqInfo.reqdata, salt: reqInfo.salt };
        const resp = await axios.post(SIGN_API_URL + "/nssig", payload, { headers: { "Content-Type": "application/json" }, timeout: 15000 });
        if (resp.data && resp.data.data) {
            return { sig: resp.data.data.sig, nstokensig: resp.data.data.nstokensig, sig3: resp.data.data.nssig3, xfalcon: resp.data.data.nssig4 || resp.data.data.xfalcon || "" };
        }
        logFn(`❌ 签名服务无响应: ${resp.data?.message || '未知错误'}`);
        return null;
    } catch (e) {
        logFn(`❌ 签名服务异常: ${e.message}`);
        return null;
    }
}

// ==================== 解析 liveInspireAwardInfo 实现翻倍 ====================
function getExpectedCoins(feed) {
    try {
        let inspireInfo = null;
        const ad = feed.ad || feed.adInfo || {};
        if (feed.liveInspireAwardInfo) inspireInfo = feed.liveInspireAwardInfo;
        else if (ad.liveInspireAwardInfo) inspireInfo = ad.liveInspireAwardInfo;
        else if (feed.adExtInfo && feed.adExtInfo.liveInspireAwardInfo) inspireInfo = feed.adExtInfo.liveInspireAwardInfo;
        
        if (inspireInfo && inspireInfo.enableLiveInspireAwardCoinMultiple === true) {
            const multipliedAmount = inspireInfo.liveInspireAwardCoinAmount;
            const multiple = inspireInfo.liveInspireAwardCoinMultiple;
            const baseCoin = inspireInfo.liveInspireAwardCoinCount;
            if (multipliedAmount && multipliedAmount > 0) {
                return { coins: multipliedAmount, multiple: multiple, baseCoin: baseCoin };
            }
        }
        
        let extData = ad.extData || ad.adExtInfo || "{}";
        if (typeof extData === "string") extData = JSON.parse(extData);
        const awardCoin = extData.awardCoin || extData.coinAmount;
        if (awardCoin) {
            return { coins: parseInt(awardCoin) || 0, multiple: 1, baseCoin: parseInt(awardCoin) };
        }
        return { coins: 0, multiple: 1, baseCoin: 0 };
    } catch (e) {
        return { coins: 0, multiple: 1, baseCoin: 0 };
    }
}

function getMaterialTime(feed) {
    try {
        const ad = feed.ad || feed.adInfo || {};
        let extData = ad.extData || ad.adExtInfo || "{}";
        if (typeof extData === "string") extData = JSON.parse(extData);
        if (extData.materialTime) return parseInt(extData.materialTime);
        if (ad.materialTime) return parseInt(ad.materialTime);
        if (feed.materialTime) return parseInt(feed.materialTime);
        return 30;
    } catch (e) {
        return 30;
    }
}

class LiveAdTask {
    constructor(remark, cookie, salt) {
        this.remark = remark;
        this.cookie = cookie;
        this.salt = salt;
        
        this.platform = identifyPlatform(cookie);
        this.kpn = this.platform.kpn;
        this.clientKey = this.platform.adClientKey;
        this.reportClientKey = this.platform.reportClientKey;
        
        this.log = createLogger(remark, this.platform.displayName);
        
        this.commonQuery = {};
        this.parseCookie();
        this.totalCoins = 0;
        this.adCreativeId = "";
        this.adId = "";
        this.llsid = "";
        this.feedId = "";
        this.appendCount = 0;
        this.h5ExtParams = Array.from({length: 96}, () => Math.floor(Math.random() * 256).toString(16).padStart(2, '0')).join('');
        
        this.signFailCount = 0;
    }

    parseCookie() {
        const extract = (key) => {
            const match = this.cookie.match(new RegExp(`(?:^|;\\s*)${key}=([^;]+)`));
            return match ? match[1] : '';
        };
        this.ud = extract("ud") || extract("userId") || "5488265105";
        this.did = extract("did") || "ANDROID_69242cf0063156fb";
        this.egid = extract("egid") || "DFPDE403E8A579BEFAFC60555A643E4BF281B64D188636A0157CBEE7B9D55016";
        this.api_st = extract("kuaishou.api_st");
        this.token = extract("token");
        
        let cookieAppver = extract("appver");
        this.appver = cookieAppver && cookieAppver.trim() !== "" ? cookieAppver : deviceParamsUnified.appver;
        this.log(`📱 使用appver: ${this.appver} (来源: ${cookieAppver ? "cookie" : "默认"})`);
        
        const nowMs = getCurrentTimestampMs();
        const did_gt = extract("did_gt") || (nowMs - 60000).toString();
        const coldLaunch = getColdLaunchTimeMs();

        this.commonQuery = { ...deviceParamsUnified };
        this.commonQuery.appver = this.appver;
        this.commonQuery.ud = this.ud;
        this.commonQuery.did = this.did;
        this.commonQuery.egid = this.egid;
        this.commonQuery.kpn = this.kpn;
        this.commonQuery.did_gt = did_gt;
        this.commonQuery.cold_launch_time_ms = coldLaunch.toString();

        const rdidFromCookie = extract("rdid");
        if (rdidFromCookie) this.commonQuery.rdid = rdidFromCookie;
        const oDidFromCookie = extract("oDid");
        if (oDidFromCookie) this.commonQuery.oDid = oDidFromCookie;
    }

    getNeoParamsBase64(config) {
        const obj = {
            pageId: config.pageId, subPageId: config.subPageId, posId: 0, businessId: config.businessId,
            extParams: this.h5ExtParams,
            customData: { exitInfo: { toastDesc: null, toastImgUrl: null } },
            pendantType: 1, displayType: 1, singlePageId: 100011291, singleSubPageId: 100011292,
            channel: 0, countdownReport: true, themeType: 0, mixedAd: false, fullMixed: false,
            autoReport: true, fromTaskCenter: true, searchInspireSchemeInfo: null, amount: 0, slideNeoInfo: null
        };
        return getBase64NoWrap(obj);
    }

    async doRequest(urlPath, formObj, pageCode, title, extraHeaders = {}) {
        const allParams = { ...this.commonQuery, ...formObj };
        const sortedData = buildSortedParams(allParams);
        const sign = await getNsSign({ urlpath: urlPath, reqdata: sortedData, salt: this.salt }, this.kpn, this.remark, this.log);
        if (!sign) {
            this.log("❌ 签名服务异常，本次请求签名失败");
            return { ok: false, signFailed: true };
        }
        const queryWithSign = buildSortedParams({
            ...this.commonQuery, sig: sign.sig, __NS_sig3: sign.sig3, __NS_xfalcon: sign.xfalcon, __NStokensig: sign.nstokensig
        });
        const fullUrl = `https://api.e.kuaishou.com${urlPath}?${queryWithSign}`;
        const bodyStr = buildSortedParams(formObj);
        
        try {
            const headers = {
                "Cookie": this.cookie, "User-Agent": "kwai-android aegon/4.41.0",
                "Content-Type": "application/x-www-form-urlencoded", "X-REQUESTID": genRequestId(),
                "page-code": pageCode, "X-Client-Info": "model=23013RK75C;os=Android;nqe-score=32;network=5G;signal-strength=1;",
                "Host": "api.e.kuaishou.com", "Connection": "keep-alive",
                ...extraHeaders
            };
            const resp = await axios.post(fullUrl, bodyStr, { headers, timeout: 10000 });
            return { ok: true, data: resp.data, signFailed: false };
        } catch (e) {
            this.log(`❌ ${title} 异常: ${e.message}`);
            return { ok: false, signFailed: false };
        }
    }

    handleSignFailure() {
        this.signFailCount++;
        this.log(`⚠️ 签名失败 (${this.signFailCount}/${MAX_SIGN_FAILURES})`);
        if (this.signFailCount >= MAX_SIGN_FAILURES) {
            this.log(`🚫 连续 ${MAX_SIGN_FAILURES} 次签名失败，停止该账号所有任务`);
            return true;
        }
        return false;
    }

    // 强制翻页：固定请求 maxPages 次，忽略 pcursor 的 "no_more" 或空值
    async getAdTask(config, isAppend) {
        const maxRetries = 3;
        const maxPages = 8;   // 强制翻页次数（固定请求8次）
        const urlPath = (this.kpn === "NEBULA") ? "/rest/nebula/fanstop/earnCoin" : "/rest/n/fanstop/earnCoin";
        
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            let pcursor = "";
            
            for (let page = 1; page <= maxPages; page++) {
                const formObj = {
                    awardType: "2", pcursor: pcursor, refreshTimes: "1", recoReportContext: "",
                    neoParams: this.getNeoParamsBase64(config), requestSceneType: String(config.requestSceneType),
                    videoModelCrowdTag: "", os: "android", cs: "false", client_key: this.clientKey,
                    "kuaishou.api_st": this.api_st, uQaTag: "1%23%23DP%3Anull%23ecBl%3A00%23ecPp%3A--%23cmNt%3A11"
                };
                if (this.token) formObj.token = this.token;
                const { ok, data: res, signFailed } = await this.doRequest(urlPath, formObj, "LIVE_WATCH", `获取${config.name}流`);
                
                if (signFailed) {
                    if (this.handleSignFailure()) return null;
                    else return null;
                }
                if (!ok || !res) return null;
                
                // 尝试在返回结果中寻找有效广告
                if (res.result === 1 && res.feeds && res.feeds.length > 0) {
                    let targetFeed = null, creativeId = null;
                    for (let feed of res.feeds) {
                        let cid = feed.creativeId || (feed.ad && feed.ad.creativeId) || (feed.adInfo && feed.adInfo.creativeId);
                        if (cid) { targetFeed = feed; creativeId = cid; break; }
                    }
                    if (targetFeed) {
                        const adObj = targetFeed.ad || targetFeed.adInfo || {};
                        this.adId = adObj.adId || adObj.sourceId || adObj.id || "";
                        this.adCreativeId = creativeId;
                        this.llsid = targetFeed.llsid || "";
                        if (!this.llsid && adObj) this.llsid = adObj.llsid || "";
                        
                        let liveStreamId = null;
                        let inspireTaskId = "";
                        let adExtInfo = "";
                        let jingleBellId = "";
                        let neoParamsBase64 = "";
                        let neoExtParams = "";
                        
                        try {
                            let extDataStr = "";
                            if (adObj.extData) extDataStr = adObj.extData;
                            else if (targetFeed.extData) extDataStr = targetFeed.extData;
                            if (extDataStr) {
                                const extData = JSON.parse(extDataStr);
                                liveStreamId = extData.liveStreamId;
                                inspireTaskId = extData.inspireTaskId || extData.taskId || "";
                                jingleBellId = extData.jingleBellId || "";
                                adExtInfo = extDataStr;
                            }
                        } catch(e) {}
                        
                        if (this.kpn === "NEBULA") {
                            try {
                                if (adObj.adExtInfo && typeof adObj.adExtInfo === 'string' && !adObj.adExtInfo.startsWith('{')) {
                                    adExtInfo = adObj.adExtInfo;
                                } else if (targetFeed.adExtInfo && typeof targetFeed.adExtInfo === 'string' && !targetFeed.adExtInfo.startsWith('{')) {
                                    adExtInfo = targetFeed.adExtInfo;
                                } else if (adObj.adDataV2 && adObj.adDataV2.inspireAdInfo && adObj.adDataV2.inspireAdInfo.adExtInfo) {
                                    adExtInfo = adObj.adDataV2.inspireAdInfo.adExtInfo;
                                }
                                if (adObj.adDataV2 && adObj.adDataV2.inspireAdInfo && adObj.adDataV2.inspireAdInfo.neoParams) {
                                    neoParamsBase64 = adObj.adDataV2.inspireAdInfo.neoParams;
                                    const neoParamsObj = JSON.parse(Buffer.from(neoParamsBase64, 'base64').toString('utf8'));
                                    neoExtParams = neoParamsObj.extParams || "";
                                }
                            } catch(e) {}
                        }
                        
                        this.feedId = liveStreamId ? String(liveStreamId) : (targetFeed.photoId || "未知feedId");
                        const { coins: expectedCoins, multiple, baseCoin } = getExpectedCoins(targetFeed);
                        const materialTime = getMaterialTime(targetFeed);
                        
                        if (multiple > 1) {
                            this.log(`✨ 触发翻倍奖励！基础 ${baseCoin} 金币 × ${multiple} 倍 = ${expectedCoins} 金币`);
                        }
                        // 找到广告立即返回，不继续翻页
                        return { 
                            creativeId: this.adCreativeId, 
                            feedId: this.feedId, 
                            llsid: this.llsid, 
                            adExtInfo, 
                            materialTime, 
                            inspireTaskId, 
                            adId: this.adId, 
                            jingleBellId,
                            expectedCoins,
                            multiple,
                            neoParamsBase64,
                            neoExtParams
                        };
                    }
                }
                
                // 强制翻页：无论返回的 pcursor 是什么，都取返回值作为下一页的 pcursor（若无效则置空）
                const nextCursor = res?.pcursor;
                pcursor = (nextCursor && nextCursor !== "") ? nextCursor : "";
                // 翻页间隔（随机 1-3 秒）
                await randomDelay();
            }
            
            // 强制翻页 maxPages 次后未找到广告，尝试外层重试
            if (attempt < maxRetries) {
                this.log(`⚠️ 第 ${attempt} 次刷新广告池失败（已强制翻页 ${maxPages} 次），${maxRetries - attempt} 秒后重试...`);
                await randomDelay();
            }
        }
        return null;
    }

    async startTask(adTask, config) {
        const formObj = {
            pageId: "0", subPageId: "0", neoStatus: "1",
            neoParams: (this.kpn === "NEBULA" && adTask.neoParamsBase64) ? adTask.neoParamsBase64 : this.getNeoParamsBase64(config),
            h5NeoParams: this.getNeoParamsBase64(config),
            liveStreamId: adTask.feedId,
            feedId: adTask.feedId,
            llsid: adTask.llsid,
            creativeId: adTask.creativeId,
            taskType: String(config.taskType),
            videoModelCrowdTag: "",
            os: "android",
            cs: "false",
            client_key: this.clientKey,
            "kuaishou.api_st": this.api_st,
            uQaTag: "1%23%23DP%3Anull%23ecBl%3A00%23ecPp%3A--%23cmNt%3A11"
        };
        if (this.token) formObj.token = this.token;
        const { ok, data: res, signFailed } = await this.doRequest("/rest/r/neo/summary", formObj, "LIVE_WATCH", "初始化观看");
        if (signFailed) {
            if (this.handleSignFailure()) throw new Error("ACCOUNT_STOP");
            return false;
        }
        if (ok && res && res.result === 1) {
            if (this.kpn === "NEBULA" && res.data && (res.data.taskFinished || res.data.currentTaskFinished)) {
                this.log(`⚠️ 当天任务已完成，跳过上报`);
                return false;
            }
            return true;
        }
        return false;
    }

    async reportTask(adTask, watchDuration, config) {
        const nowMs = Date.now();
        const startTime = nowMs - watchDuration * 1000;
        const endTime = nowMs;
        const sessionId = `adNeo-${this.ud}-${config.subPageId}-${startTime}`;

        if (this.kpn === "NEBULA") {
            const extInfoObj = {
                businessId: config.businessId,
                extParams: adTask.neoExtParams || "",
                pageId: config.pageId,
                subPageId: config.subPageId
            };
            const bizStrObj = {
                businessId: config.businessId,
                endTime: endTime,
                extParams: this.h5ExtParams,
                mediaScene: "live",
                neoInfos: [{
                    creativeId: Number(this.adCreativeId),
                    extInfo: getBase64NoWrap(extInfoObj),
                    feedId: adTask.feedId,
                    llsid: Number(adTask.llsid),
                    adExtInfo: adTask.adExtInfo || "",
                    materialTime: 0,
                    watchAdTime: 30000,
                    requestSceneType: config.requestSceneType,
                    taskType: config.taskType,
                    watchExpId: "",
                    watchStage: 0
                }],
                pageId: config.pageId,
                posId: config.posId,
                reportType: 0,
                sessionId: sessionId,
                startTime: startTime,
                subPageId: config.subPageId
            };
            const formObj = {
                bizStr: JSON.stringify(bizStrObj),
                cs: "false",
                client_key: this.reportClientKey,
                videoModelCrowdTag: "",
                os: "android",
                "kuaishou.api_st": this.api_st,
                uQaTag: "1%23%23DP%3Anull%23ecBl%3A00%23ecPp%3A--%23cmNt%3A11"
            };
            if (this.token) formObj.token = this.token;
            const { ok, data: res, signFailed } = await this.doRequest("/rest/r/ad/task/report", formObj, "LIVE_WATCH", "上报任务");
            if (signFailed) {
                if (this.handleSignFailure()) throw new Error("ACCOUNT_STOP");
                return { success: false, amount: 0, busy: false, signFailed: true };
            }
            if (!ok) return { success: false, amount: 0, busy: false };
            if (res.result === 1) {
                const amount = res.data?.neoAmount || 0;
                return { success: true, amount, busy: false };
            } else {
                const msg = res.error_msg || "";
                const isBusy = (res.result === -1 && (msg.includes("忙") || msg.includes("frequency") || msg.includes("限流"))) ||
                               msg.includes("内部系统繁忙") || msg.includes("系统繁忙") || res.result === 500;
                return { success: false, amount: 0, busy: isBusy };
            }
        } else {
            const extInfoObj = {
                businessId: config.businessId,
                extParams: "",
                pageId: config.pageId,
                subPageId: config.subPageId,
                posId: config.posId,
                adId: this.adId,
                creativeId: this.adCreativeId,
                feedId: adTask.feedId,
                inspireTaskId: String(adTask.inspireTaskId || ""),
                jingleBellId: adTask.jingleBellId || "",
                materialTime: adTask.materialTime,
                watchAdTime: adTask.materialTime
            };
            const bizStrObj = {
                businessId: config.businessId,
                endTime: endTime,
                extParams: "",
                mediaScene: "live",
                neoInfos: [{
                    adId: this.adId,
                    creativeId: this.adCreativeId,
                    extInfo: getBase64NoWrap(extInfoObj),
                    feedId: adTask.feedId,
                    llsid: adTask.llsid,
                    adExtInfo: adTask.adExtInfo || "",
                    inflow: true,
                    materialTime: adTask.materialTime,
                    watchAdTime: adTask.materialTime,
                    requestSceneType: config.requestSceneType,
                    taskType: config.taskType,
                    watchExpId: "",
                    watchStage: 0,
                    inspireTaskId: String(adTask.inspireTaskId || "")
                }],
                pageId: config.pageId,
                posId: config.posId,
                reportType: 0,
                sessionId: sessionId,
                startTime: startTime,
                subPageId: config.subPageId
            };
            const formObj = {
                bizStr: JSON.stringify(bizStrObj),
                cs: "false",
                client_key: this.reportClientKey,
                videoModelCrowdTag: "",
                os: "android",
                "kuaishou.api_st": this.api_st,
                uQaTag: "1%23%23DP%3Anull%23ecBl%3A00%23ecPp%3A--%23cmNt%3A11"
            };
            if (this.token) formObj.token = this.token;
            const { ok, data: res, signFailed } = await this.doRequest("/rest/r/ad/task/report", formObj, "LIVE_WATCH", "上报任务");
            if (signFailed) {
                if (this.handleSignFailure()) throw new Error("ACCOUNT_STOP");
                return { success: false, amount: 0, busy: false, signFailed: true };
            }
            if (!ok) return { success: false, amount: 0, busy: false };
            if (res.result === 1) {
                const amount = res.data?.neoAmount || 0;
                return { success: true, amount, busy: false };
            } else {
                const msg = res.error_msg || "";
                const isBusy = (res.result === -1 && (msg.includes("忙") || msg.includes("frequency") || msg.includes("限流"))) ||
                               msg.includes("内部系统繁忙") || msg.includes("系统繁忙") || res.result === 500;
                if (isBusy) {
                    this.log(`⚠️ 上报内部繁忙: ${msg || 'code '+res.result}`);
                } else {
                    this.log(`❌ 上报失败: ${msg || '未知错误'} (${res.result})`);
                }
                return { success: false, amount: 0, busy: isBusy };
            }
        }
    }

    async runInitial(config) {
        try {
            let adTask = null;
            for (let refresh = 1; refresh <= 99; refresh++) {
                adTask = await this.getAdTask(config, false);
                if (adTask) {
                    if (refresh > 1) {
                        this.log(`✅ 第${refresh}次刷新广告池成功，获取到广告`);
                    }
                    break;
                }
                if (refresh < 99) {
                    const waitSec = randomDelaySeconds();
                    this.log(`⚠️ 第${refresh}次刷新广告池失败，等待 ${waitSec} 秒后重试...`);
                    await delay(waitSec * 1000);
                }
            }
            
            if (!adTask) {
                this.log(`❌ 初始广告获取失败（已刷新99次广告池均失败），停止任务`);
                return false;
            }
            
            let busyCount = 0;
            while (busyCount < MAX_BUSY_INITIAL) {
                const expected = adTask.expectedCoins;
                this.log(`初始 预计 ${expected} 金币`);
                
                const baseWatch = adTask.materialTime;
                const watchSec = baseWatch + Math.random() * 2;
                this.log(`观看初始 ${watchSec.toFixed(1)} 秒...`);
                await delay(watchSec * 1000);
                
                const initOk = await this.startTask(adTask, config);
                if (!initOk) {
                    this.log(`❌ 初始化观看失败，停止任务`);
                    return false;
                }
                
                const { success, amount, busy } = await this.reportTask(adTask, adTask.materialTime, config);
                if (success && amount > 0) {
                    this.totalCoins += amount;
                    this.log(`初始 ${amount} 金币 | 累计 ${this.totalCoins}`);
                    return true;
                } else if (busy) {
                    busyCount++;
                    this.log(`⚠️ 初始上报繁忙 (${busyCount}/${MAX_BUSY_INITIAL})`);
                    if (busyCount >= MAX_BUSY_INITIAL) {
                        this.log(`❌ 连续 ${MAX_BUSY_INITIAL} 次内部繁忙，停止初始任务`);
                        return false;
                    }
                    const intervalSec = randomDelaySeconds();
                    this.log(`重试间隔 ${intervalSec.toFixed(1)} 秒...`);
                    await delay(intervalSec * 1000);
                    continue;
                } else {
                    this.log(`❌ 初始上报失败（非繁忙），停止任务`);
                    return false;
                }
            }
            return false;
        } catch (error) {
            if (error.message === "ACCOUNT_STOP") {
                this.log(`🚫 账号因连续签名失败已停止`);
                return false;
            }
            throw error;
        }
    }

    async runAppend(config) {
        this.appendCount = 0;
        let consecutiveFailures = 0;
        let busyCount = 0;
        const MAX_AD_FAILURES = 99;

        try {
            for (let i = 1; i <= MAX_LIVES; i++) {
                const adTask = await this.getAdTask(config, true);
                if (!adTask) {
                    consecutiveFailures++;
                    this.log(`❌ 获取追加广告失败（刷新广告池第 ${consecutiveFailures}/${MAX_AD_FAILURES} 次失败）`);
                    if (consecutiveFailures >= MAX_AD_FAILURES) {
                        this.log(`❌ 连续 ${MAX_AD_FAILURES} 次刷新广告池失败，停止追加任务`);
                        break;
                    }
                    const intervalSec = randomDelaySeconds();
                    this.log(`追加间隔 ${intervalSec.toFixed(1)} 秒...`);
                    await delay(intervalSec * 1000);
                    continue;
                }
                consecutiveFailures = 0;
                
                const expected = adTask.expectedCoins;
                this.log(`追加 预计 ${expected} 金币`);
                
                const baseWatch = adTask.materialTime;
                const watchSec = baseWatch + Math.random() * 2;
                await delay(watchSec * 1000);
                
                const initOk = await this.startTask(adTask, config);
                if (!initOk) {
                    this.log(`❌ 初始化观看失败，本次追加无效，等待间隔后继续`);
                    const intervalSec = randomDelaySeconds();
                    this.log(`追加间隔 ${intervalSec.toFixed(1)} 秒...`);
                    await delay(intervalSec * 1000);
                    continue;
                }
                
                const { success, amount, busy } = await this.reportTask(adTask, adTask.materialTime, config);
                if (busy) {
                    busyCount++;
                    this.log(`⚠️ 追加上报繁忙 (${busyCount}/${MAX_BUSY_APPEND})`);
                    if (busyCount >= MAX_BUSY_APPEND) {
                        this.log(`⏸️ 连续 ${MAX_BUSY_APPEND} 次繁忙，休息5分钟...`);
                        await delay(APPEND_BUSY_BREAK_MS);
                        busyCount = 0;
                        this.log(`🔄 休息结束，继续追加任务`);
                    }
                    const intervalSec = randomDelaySeconds();
                    this.log(`追加间隔 ${intervalSec.toFixed(1)} 秒...`);
                    await delay(intervalSec * 1000);
                    continue;
                }
                busyCount = 0;
                
                if (success && amount > 0) {
                    this.totalCoins += amount;
                    this.appendCount++;
                    this.log(`追加(${this.appendCount}) ${amount} 金币 | 累计 ${this.totalCoins}`);
                    this.log(`追加计数 (第 ${this.appendCount}/${MAX_LIVES} 次)`);  // 文案修改
                }
                
                const intervalSec = randomDelaySeconds();
                this.log(`追加间隔 ${intervalSec.toFixed(1)} 秒...`);
                await delay(intervalSec * 1000);
            }
        } catch (error) {
            if (error.message === "ACCOUNT_STOP") {
                this.log(`🚫 账号因连续签名失败已停止`);
                return;
            }
            throw error;
        }
    }

    async run() {
        this.log(`==== 开始执行 (${this.platform.displayName}) ====`);
        const platformKey = this.kpn === "NEBULA" ? "NEBULA" : "KUAISHOU";
        const configs = TASK_CONFIGS[platformKey];
        
        for (let idx = 0; idx < TASKS_TO_RUN.length; idx++) {
            const taskKey = TASKS_TO_RUN[idx];
            const config = configs[taskKey];
            if (!config) continue;
            
            if (taskKey === "live") {
                const success = await this.runInitial(config);
                if (!success) {
                    this.log(`初始任务失败，跳过后续追加任务`);
                    break;
                }
                if (idx < TASKS_TO_RUN.length - 1 && TASKS_TO_RUN[idx+1] === "lives") {
                    const intervalSec = randomDelaySeconds();
                    this.log(`追加间隔 ${intervalSec.toFixed(1)} 秒...`);
                    await delay(intervalSec * 1000);
                }
            } else if (taskKey === "lives") {
                await this.runAppend(config);
            }
        }
        this.log(`==== 结束，累计获得 ${this.totalCoins} 金币 ====\n`);
    }
}

// ==================== 并发控制 ====================
async function runWithConcurrency(tasks, concurrency) {
    const results = [];
    const executing = new Set();
    for (const task of tasks) {
        const p = Promise.resolve().then(() => task());
        results.push(p);
        executing.add(p);
        const clean = () => executing.delete(p);
        p.then(clean).catch(clean);
        if (executing.size >= concurrency) {
            await Promise.race(executing);
        }
    }
    return Promise.all(results);
}

// ==================== 主入口 ====================
(async () => {
    console.log(`🌸 快手广告脚本（双端自动识别 | 间隔1-3秒 | 签名失败3次停号 | 初始繁忙2次停任务 | 追加繁忙3次休息5分 | 强制翻页忽略no_more | 翻页日志静默）🌸\n`);
    const envKsck = process.env.ksck;
    if (!envKsck) { console.log("❌ 环境变量 ksck 未设置"); process.exit(1); }
    const rawAccounts = envKsck.split("&").filter(Boolean);
    const accounts = [];
    for (const line of rawAccounts) {
        const parts = line.trim().split("#");
        if (parts.length < 3) {
            console.log(`⚠️ 账号格式错误: ${line}`);
            continue;
        }
        accounts.push(new LiveAdTask(parts[0], parts[1], parts[2]));
    }
    if (accounts.length === 0) {
        console.log("❌ 没有有效的账号，退出");
        process.exit(1);
    }
    console.log(`📊 共加载 ${accounts.length} 个账号，并发数限制 ${MAX_CONCURRENT_ACCOUNTS}\n`);
    await runWithConcurrency(accounts.map(acc => () => acc.run()), MAX_CONCURRENT_ACCOUNTS);
    console.log("\n✅ 所有账号执行结束");
})();