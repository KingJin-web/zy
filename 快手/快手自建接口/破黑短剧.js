
const axios = require("axios");
console.log("自定义接口搭建教程 https://mp.weixin.qq.com/s/QCpnK8scCmG69lLm3xg9XA")
console.log("最低2.1代理，4.5家庭住宅 http://www.gzsk5.com/#/register?invitation=hnking2&shareid=516")
// ==============================================
// 快手普通版 · 纯短剧广告专用脚本
// 接口搭建教程
// 环境变量：ck  格式：备注#cookie#salt&...
// ==============================================

const COLOR = {
  RESET: "\x1b[0m",
  BRIGHT: "\x1b[1m",
  RED: "\x1b[31m",
  GREEN: "\x1b[32m",
  YELLOW: "\x1b[33m",
  BLUE: "\x1b[34m",
  MAGENTA: "\x1b[35m",
  CYAN: "\x1b[36m",
  GRAY: "\x1b[90m",
  BG_GREEN: "\x1b[42m",
  BG_YELLOW: "\x1b[43m",
  BG_RED: "\x1b[41m"
};

function colorLog(type, msg) {
  const colorMap = {
    success: `${COLOR.GREEN}✅${COLOR.RESET}`,
    info: `${COLOR.BLUE}ℹ️${COLOR.RESET}`,
    warn: `${COLOR.YELLOW}⚠️${COLOR.RESET}`,
    error: `${COLOR.RED}❌${COLOR.RESET}`,
    stop: `${COLOR.BG_RED}🚫${COLOR.RESET}`,
    pause: `${COLOR.BG_YELLOW}⏸️${COLOR.RESET}`,
    refresh: `${COLOR.CYAN}🔄${COLOR.RESET}`,
    coin: `${COLOR.MAGENTA}💰${COLOR.RESET}`,
    double: `${COLOR.BRIGHT}✨${COLOR.RESET}`
  };
  return `${colorMap[type] || ""} ${msg}`;
}

// ==============================================
// 签名配置
// ==============================================
const SIGN_API_KUAISHOU = process.env.kspt_api || "http://47.113.119.128:202";
const SIGN_API_NEBULA = process.env.ksjs_api || "http://47.113.119.128:201";

// 强制只执行短剧
const TASKS_TO_RUN = ["drama"];

const MAX_DRAMA = parseInt(process.env.KS_MAX_DRAMA) || 999999;
const MAX_CONCURRENT_ACCOUNTS = parseInt(process.env.KS_MAX_CONCURRENT) || 10;

const MIN_DELAY_SEC = 1;
const MAX_DELAY_SEC = 3;

function randomDelaySeconds() {
  return Math.floor(Math.random() * (MAX_DELAY_SEC - MIN_DELAY_SEC + 1) + MIN_DELAY_SEC);
}
function randomDelay() {
  return new Promise(resolve => setTimeout(resolve, randomDelaySeconds() * 1000));
}

const MAX_BUSY_INITIAL = 2;
const MAX_BUSY_APPEND = 3;
const APPEND_BUSY_BREAK_MS = 5 * 60 * 1000;
const MAX_SIGN_FAILURES = 3;

// ==============================================
// 平台配置（普通版）
// ==============================================
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
  }
};

function identifyPlatform(cookie) {
  return PLATFORM_CONFIG.KUAISHOU;
}

// ==============================================
// 设备参数
// ==============================================
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
    console.log(colorLog("success", "已加载自定义设备参数"));
  } catch (e) {
    console.log(colorLog("warn", `设备参数解析失败: ${e.message}`));
  }
}

// ==============================================
// 短剧广告参数
// ==============================================
const TASK_CONFIGS = {
  KUAISHOU: {
    drama: {
      name: "短剧广告",
      businessId: 7057,
      posId: 216266,
      pageId: 100014021,
      subPageId: 100014022,
      requestSceneType: 7,
      taskType: 2
    }
  }
};

// ==============================================
// 工具函数
// ==============================================
function createLogger(remark, platformDisplayName) {
  const prefix = `${COLOR.CYAN}[${new Date().toLocaleTimeString()}]${COLOR.RESET} ${COLOR.BRIGHT}[${remark}]${COLOR.RESET} ${COLOR.GRAY}[${platformDisplayName}]${COLOR.RESET}`;
  return {
    success: (msg) => console.log(`${prefix} ${colorLog("success", msg)}`),
    info: (msg) => console.log(`${prefix} ${colorLog("info", msg)}`),
    warn: (msg) => console.log(`${prefix} ${colorLog("warn", msg)}`),
    error: (msg) => console.log(`${prefix} ${colorLog("error", msg)}`),
    stop: (msg) => console.log(`${prefix} ${colorLog("stop", msg)}`),
    pause: (msg) => console.log(`${prefix} ${colorLog("pause", msg)}`),
    refresh: (msg) => console.log(`${prefix} ${colorLog("refresh", msg)}`),
    coin: (msg) => console.log(`${prefix} ${colorLog("coin", msg)}`),
    double: (msg) => console.log(`${prefix} ${colorLog("double", msg)}`),
    raw: (msg) => console.log(`${prefix} ${msg}`)
  };
}

function delay(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }
function genRequestId() { return Math.floor(Math.random() * 100000000000000000).toString(); }
function getCurrentTimestampMs() { return Date.now(); }
function getColdLaunchTimeMs() { return Date.now() - 30 * 1000; }

function javaUrlEncode(str) {
  if (!str) return "";
  return encodeURIComponent(str)
    .replace(/!/g, '%21')
    .replace(/'/g, '%27')
    .replace(/\(/g, '%28')
    .replace(/\)/g, '%29')
    .replace(/~/g, '%7E')
    .replace(/\*/g, '%2A');
}

function buildSortedParams(obj) {
  return Object.keys(obj).sort()
    .filter(k => obj[k] != null && obj[k] !== "")
    .map(k => `${javaUrlEncode(k)}=${javaUrlEncode(obj[k])}`)
    .join('&');
}

function getBase64NoWrap(obj) {
  return Buffer.from(JSON.stringify(obj)).toString('base64').replace(/=+$/, '');
}

// ==============================================
// 签名
// ==============================================
async function getNsSign(reqInfo, kpnType, remark, logObj) {
  const SIGN_API_URL = SIGN_API_KUAISHOU;
  try {
    const payload = { path: reqInfo.urlpath, data: reqInfo.reqdata, salt: reqInfo.salt };
    const resp = await axios.post(SIGN_API_URL + "/nssig", payload, {
      headers: { "Content-Type": "application/json" },
      timeout: 15000
    });
    if (resp.data?.data) {
      return {
        sig: resp.data.data.sig,
        nstokensig: resp.data.data.nstokensig,
        sig3: resp.data.data.nssig3,
        xfalcon: resp.data.data.nssig4 || ""
      };
    }
  } catch (e) {
    logObj.error(`签名失败: ${e.message}`);
  }
  return null;
}

// ==============================================
// 广告解析
// ==============================================
function getDramaAdInfo(feed) {
  try {
    const ad = feed.ad || feed.adInfo || feed;
    let extData = ad.extData || "{}";
    if (typeof extData === "string") extData = JSON.parse(extData);

    const award = extData.awardCoin || extData.coinAmount || 0;
    const duration = extData.materialTime || ad.materialTime || 50;

    return {
      coins: parseInt(award) || 0,
      duration
    };
  } catch (e) {
    return { coins: 0, duration: 50 };
  }
}

// ==============================================
// 短剧任务类
// ==============================================
class DramaAdTask {
  constructor(remark, cookie, salt) {
    this.remark = remark;
    this.cookie = cookie;
    this.salt = salt;

    this.platform = PLATFORM_CONFIG.KUAISHOU;
    this.kpn = "KUAISHOU";
    this.clientKey = "3c2cd3f3";
    this.reportClientKey = "3c2cd3f3";

    this.log = createLogger(remark, this.platform.displayName);
    this.commonQuery = {};
    this.parseCookie();

    this.totalCoins = 0;
    this.cid = "";
    this.adId = "";
    this.llsid = "";
    this.feedId = "";
    this.signFailCount = 0;

    this.h5ExtParams = Array.from({ length: 96 }, () =>
      Math.floor(Math.random() * 256).toString(16).padStart(2, "0")
    ).join("");
  }

  parseCookie() {
    const extract = (k) => {
      const m = this.cookie.match(new RegExp(`(^|;\\s*)${k}=([^;]+)`));
      return m ? m[2] : "";
    };
    this.ud = extract("ud") || extract("userId");
    this.did = extract("did");
    this.egid = extract("egid");
    this.api_st = extract("kuaishou.api_st");
    this.token = extract("token");
    this.appver = extract("appver") || deviceParamsUnified.appver;

    const now = Date.now();
    this.commonQuery = {
      ...deviceParamsUnified,
      appver: this.appver,
      ud: this.ud,
      did: this.did,
      egid: this.egid,
      kpn: this.kpn,
      did_gt: extract("did_gt") || (now - 60000).toString(),
      cold_launch_time_ms: (now - 30000).toString()
    };
  }

  async doRequest(urlPath, form) {
    const all = { ...this.commonQuery, ...form };
    const data = buildSortedParams(all);

    const sign = await getNsSign(
      { urlpath: urlPath, reqdata: data, salt: this.salt },
      this.kpn,
      this.remark,
      this.log
    );
    if (!sign) return { ok: false, signFailed: true };

    const qs = buildSortedParams({
      ...this.commonQuery,
      sig: sign.sig,
      __NS_sig3: sign.sig3,
      __NStokensig: sign.nstokensig
    });

    const url = `https://api.e.kuaishou.com${urlPath}?${qs}`;
    const body = buildSortedParams(form);

    try {
      const res = await axios.post(url, body, {
        headers: {
          Cookie: this.cookie,
          "Content-Type": "application/x-www-form-urlencoded",
          "User-Agent": "kwai-android",
          Host: "api.e.kuaishou.com"
        },
        timeout: 10000
      });
      return { ok: true, data: res.data };
    } catch (e) {
      this.log.error(`请求失败: ${e.message}`);
      return { ok: false };
    }
  }

  async getDramaAd(config) {
    for (let i = 0; i < 10; i++) {
      const form = {
        client_key: this.clientKey,
        business_id: config.businessId,
        pageId: config.pageId,
        subPageId: config.subPageId,
        request_scene_type: config.requestSceneType,
        os: "android",
        cs: "false"
      };

      const { ok, data, signFailed } = await this.doRequest("/rest/e/reward/mixed/ad", form);
      if (signFailed) {
        this.signFailCount++;
        if (this.signFailCount >= 3) { this.log.stop("签名失败超限"); return null; }
        continue;
      }
      if (!ok || data.result !== 1) continue;

      const ad = data.ads?.[0] || data.adList?.[0] || data.feeds?.[0];
      if (!ad) continue;

      this.cid = ad.cid || ad.creativeId || "";
      this.adId = ad.adId || ad.id || "";
      this.llsid = ad.llsid || "";
      this.feedId = ad.photoId || this.cid;

      const { coins, duration } = getDramaAdInfo(ad);
      this.log.success(`获取短剧广告 | 预计 ${coins} 金币 | 时长 ${duration}s`);
      return { coins, duration };
    }
    this.log.warn("未获取到短剧广告");
    return null;
  }

  async reportDrama(config, duration) {
    const now = Date.now();
    const watch = duration * 1000;

    const biz = {
      businessId: config.businessId,
      pageId: config.pageId,
      subPageId: config.subPageId,
      posId: config.posId,
      startTime: now - watch,
      endTime: now,
      mediaScene: "video",
      sessionId: `drama_${now}`,
      reportType: 0,
      neoInfos: [
        {
          creativeId: this.cid,
          adId: this.adId,
          llsid: this.llsid,
          feedId: this.feedId,
          watchAdTime: watch,
          materialTime: watch,
          requestSceneType: config.requestSceneType,
          taskType: config.taskType,
          watchStage: 0
        }
      ]
    };

    const form = {
      bizStr: JSON.stringify(biz),
      client_key: this.reportClientKey,
      os: "android",
      cs: "false"
    };

    const { ok, data } = await this.doRequest("/rest/r/ad/task/report", form);
    if (ok && data.result === 1) {
      const coin = data.data?.neoAmount || 0;
      this.totalCoins += coin;
      this.log.coin(`上报成功 +${coin} | 总计 ${this.totalCoins}`);
      return true;
    }
    this.log.error("上报失败");
    return false;
  }

  async run() {
    this.log.raw(`${COLOR.BG_GREEN}==== 开始短剧任务 ====${COLOR.RESET}`);
    const config = TASK_CONFIGS.KUAISHOU.drama;

    for (let i = 1; i <= MAX_DRAMA; i++) {
      const ad = await this.getDramaAd(config);
      if (!ad) { await delay(5000); continue; }

      this.log.info(`第 ${i} 轮 | 观看 ${ad.duration} 秒`);
      await delay(ad.duration * 1000 + Math.random() * 2000);

      await this.reportDrama(config, ad.duration);
      await randomDelay();
    }

    this.log.raw(`${COLOR.BG_GREEN}==== 任务结束 | 总计 ${this.totalCoins} 金币 ====${COLOR.RESET}`);
  }
}

// ==============================================
// 账号读取：从环境变量 ck 读取
// ==============================================
function getAccounts() {
  const ck = process.env.ck || "";
  return ck.split("&").filter(Boolean).map(line => {
    const [remark, cookie, salt] = line.split("#");
    return { remark, cookie, salt };
  });
}

// ==============================================
// 启动入口
// ==============================================
async function run() {
  const accounts = getAccounts();
  if (accounts.length === 0) {
    console.log(colorLog("error", "请配置环境变量：ck"));
    process.exit(1);
  }

  const set = new Set();
  for (const acc of accounts) {
    while (set.size >= MAX_CONCURRENT_ACCOUNTS) await Promise.race(set);
    const task = new DramaAdTask(acc.remark, acc.cookie, acc.salt).run().finally(() => set.delete(task));
    set.add(task);
  }
  await Promise.all(set);
}

run();

// 当前脚本来自于 http://script.345yun.cn 脚本库下载！
// 当前脚本来自于 http://2.345yun.cn 脚本库下载！
// 当前脚本来自于 http://2.345yun.cc 脚本库下载！
// 脚本库官方QQ群1群: 429274456
// 脚本库官方QQ群2群: 1077801222
// 脚本库官方QQ群3群: 433030897
// 脚本库中的所有脚本文件均来自热心网友上传和互联网收集。
// 脚本库仅提供文件上传和下载服务，不提供脚本文件的审核。
// 您在使用脚本库下载的脚本时自行检查判断风险。
// 所涉及到的 账号安全、数据泄露、设备故障、软件违规封禁、财产损失等问题及法律风险，与脚本库无关！均由开发者、上传者、使用者自行承担。