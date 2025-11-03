//本程序为js脚本！运行前请先安装好axios依赖和socks-proxy-agent依赖

//最新可用！免费版开源版/2025.11.03

//变量名称: ksck   变量值格式: ck#salt#代理

//代理格式说明: socks5://代理账号:代理密码@代理ip:代理端口号

//完整变量值示例: ck#salt#sock5://代理账号:代理密码@代理ip:代理端口号

//多账号运行请新建多个变量！变量名称: ksck1  变量名称: ksck2  变量名称: ksck3

//345站长已优化版之快手本我只用免费的！拒绝做韭菜被收割！

const qs = require("querystring");
const axios = require("axios");

const querystring = require("querystring");
const { SocksProxyAgent } = require("socks-proxy-agent");

// 生成随机交互消息
function generateRandomInteractionMessage() {
  const messages = [
    "正在观看广告",
    "认真观看中...",
    "浏览广告内容",
    "模拟用户行为",
    "观看视频广告",
    "保持活跃状态",
    "广告浏览中",
    "正常观看时长",
  ];
  return messages[Math.floor(Math.random() * messages.length)];
}

// 开发模式和环境变量检测
const isDevMode =
  process.env.DEV_MODE === "1" || process.env.DEV_MODE === "true";

// 获取环境变量值，带默认值
function getEnvNumber(envKey, defaultValue) {
  const value = parseInt(process.env[envKey], 10);
  return isNaN(value) ? defaultValue : value;
}

// 环境变量配置
const KSLOW_REWARD_THRESHOLD = getEnvNumber("KSLOW_REWARD_THRESHOLD", 10); // 低奖励阈值
const KSROUNDS = getEnvNumber("KSROUNDS", 35); // 任务轮数
const KSCOIN_LIMIT = getEnvNumber("KSCOIN_LIMIT", 500000); // 金币上限
const KSLOW_REWARD_LIMIT = getEnvNumber("KSLOW_REWARD_LIMIT", 3); // 连续低奖励上限

// 获取要执行的任务列表
function getTasksToExecute() {
  const taskEnv = process.env.Task;
  if (!taskEnv) {
    console.log("📝 未设置Task环境变量，将执行所有任务 (food, box, look)");
    return ["food", "box", "look"];
  }

  const tasks = taskEnv
    .split(",")
    .map((task) => task.trim().toLowerCase())
    .filter(Boolean);
  const validTasks = ["food", "box", "look"];
  const filteredTasks = tasks.filter((task) => validTasks.includes(task));

  if (filteredTasks.length === 0) {
    console.log("📝 Task环境变量中没有有效任务，将执行所有任务 (food, box, look)");
    return ["food", "box", "look"];
  }

  console.log("🎯 从Task环境变量中解析到要执行的任务: " + filteredTasks.join(", "));
  return filteredTasks;
}

// 从 ksck, ksck1 到 ksck666 读取账号配置
function getAccountConfigsFromEnv() {
  const configs = [];
  const seenConfigs = new Set();

  // 读取ksck主配置
  if (process.env.ksck) {
    const ksckValue = process.env.ksck;
    const configStrings = ksckValue
      .split("&")
      .map((config) => config.trim())
      .filter(Boolean);
    configs.push(...configStrings);
  }

  // 读取ksck1到ksck666配置
  for (let i = 1; i <= 666; i++) {
    const ksckKey = `ksck${i}`;
    if (process.env[ksckKey]) {
      const ksckValue = process.env[ksckKey];
      const configStrings = ksckValue
        .split("&")
        .map((config) => config.trim())
        .filter(Boolean);
      configs.push(...configStrings);
    }
  }

  // 去重处理
  const uniqueConfigs = [];
  for (const config of configs) {
    if (!seenConfigs.has(config)) {
      seenConfigs.add(config);
      uniqueConfigs.push(config);
    }
  }

  console.log(`📊 从环境变量中解析到 ${uniqueConfigs.length} 个唯一配置`);
  return uniqueConfigs;
}

const accountConfigs = getAccountConfigsFromEnv();
const accountCount = accountConfigs.length;
const tasksToExecute = getTasksToExecute();

// 美化打印：简洁的启动信息
console.log("\n" + "=".repeat(50));
console.log("🚀 快手免费金币版 - 启动成功");
console.log("🚀 当前脚本来自于http://script.345yun.cn脚本库下载");
console.log("=".repeat(50));
console.log(`📱 账号数量: ${accountCount}个`);
console.log(`🎯 执行任务: ${tasksToExecute.join(", ")}`);
console.log(`⚙️ 配置参数: 轮数=${KSROUNDS}, 金币上限=${KSCOIN_LIMIT}`);
console.log("=".repeat(50) + "\n");

if (accountCount > (process.env.MAX_CONCURRENCY || 999)) {
  console.log(`❌ 错误: 检测到 ${accountCount} 个账号配置，最多只允许${process.env.MAX_CONCURRENCY || 999}个`);
  process.exit(1);
}

// 生成快手设备ID
function generateKuaishouDid() {
  try {
    const generateRandomHexString = (length) => {
      const hexChars = "0123456789abcdef";
      let result = "";
      for (let i = 0; i < length; i++) {
        result += hexChars.charAt(Math.floor(Math.random() * hexChars.length));
      }
      return result;
    };

    const randomId = generateRandomHexString(16);
    const deviceId = "ANDROID_" + randomId;
    return deviceId;
  } catch (error) {
    console.log("❌ 生成did失败: " + error.message);
    const timestamp = Date.now().toString(16).toUpperCase();
    return "ANDROID_" + timestamp.substring(0, 16);
  }
}

// 发送网络请求
async function sendRequest(
  requestOptions,
  proxyUrl = null,
  description = "Unknown Request"
) {
  const finalOptions = { ...requestOptions };

  // 配置代理
  let agent = null;
  if (proxyUrl) {
    try {
      agent = new SocksProxyAgent(proxyUrl);
    } catch (proxyError) {
      console.log(`❌ ${description} 代理URL无效，尝试直连模式`);
    }
  }

  try {
    const axiosConfig = {
      method: finalOptions.method || "GET",
      url: finalOptions.url,
      headers: finalOptions.headers || {},
      data: finalOptions.body || finalOptions.form,
      timeout: finalOptions.timeout || 30000,
      ...(agent && {
        httpAgent: agent,
        httpsAgent: agent,
      }),
    };

    const response = await axios(axiosConfig);
    return { response: response, body: response.data };
  } catch (error) {
    return { response: null, body: null };
  }
}

// 测试代理连通性
async function testProxyConnectivity(proxyUrl, description = "代理连通性检测") {
  if (!proxyUrl) {
    return {
      ok: true,
      msg: "✅ 未配置代理（直连模式）",
      ip: "localhost",
    };
  }

  const { response: baiduResponse, body: baiduResult } = await sendRequest(
    {
      method: "GET",
      url: "https://httpbin.org/ip",
      headers: {
        "User-Agent": "ProxyTester/1.0",
      },
      timeout: 8000,
    },
    proxyUrl,
    description + " → baidu.com"
  );
  
  if (baiduResult) {
    return {
      ok: true,
      msg: `✅ SOCKS5代理正常，出口IP: ${baiduResult.origin}`,
      ip: baiduResult.origin,
    };
  }
  
  return {
    ok: false,
    msg: "❌ 代理连接失败",
    ip: null
  };
}

const usedProxies = new Set();

// 获取账号基本信息
async function getAccountBasicInfo(cookie, proxyUrl, accountId = "?") {
  const url =
    "https://nebula.kuaishou.com/rest/n/nebula/activity/earn/overview/basicInfo?source=bottom_guide_first";

  const { body: result } = await sendRequest(
    {
      method: "GET",
      url: url,
      headers: {
        Host: "nebula.kuaishou.com",
        "User-Agent": "kwai-android aegon/3.56.0",
        Cookie: cookie,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      timeout: 12000,
    },
    proxyUrl,
    "获取账号基本信息"
  );

  if (result && result.result === 1 && result.data) {
    return {
      nickname: result.data.userData?.nickname || null,
      totalCoin: result.data.totalCoin ?? null,
      allCash: result.data.allCash ?? null,
    };
  }

  return null;
}

// 快手广告任务类
class KuaishouAdTask {
  constructor({
    index,
    salt,
    cookie,
    nickname = "",
    proxyUrl = null,
    tasksToExecute = ["food", "box", "look"],
    remark = "",
  }) {
    this.index = index;
    this.salt = salt;
    this.cookie = cookie;
    this.nickname = nickname || remark || "账号" + index;
    this.remark = remark;
    this.proxyUrl = proxyUrl;
    this.coinLimit = KSCOIN_LIMIT;
    this.coinExceeded = false;
    this.tasksToExecute = tasksToExecute;

    this.extractCookieInfo();

    // 请求头配置
    this.headers = {
      Host: "nebula.kuaishou.com",
      Connection: "keep-alive",
      "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Lite Build/QKQ1.190910.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.101 Mobile Safari/537.36",
      Cookie: this.cookie,
      "content-type": "application/json",
    };

    this.taskReportPath = "/rest/r/ad/task/report";
    this.startTime = Date.now();
    this.endTime = this.startTime - 30000;
    this.queryParams =
      "mod=Xiaomi(MI 11)&appver=" +
      this.appver +
      "&egid=" +
      this.egid +
      "&did=" +
      this.did;

    // 任务配置
    this.taskConfigs = {
      box: {
        name: "宝箱广告",
        businessId: 606,
        posId: 20346,
        subPageId: 100024064,
        requestSceneType: 1,
        taskType: 1,
      },
      look: {
        name: "看广告得金币",
        businessId: 672,
        posId: 24067,
        subPageId: 100026367,
        requestSceneType: 1,
        taskType: 1,
      },
      food: {
        name: "饭补广告",
        businessId: 9362,
        posId: 24067,
        subPageId: 100026367,
        requestSceneType: 7,
        taskType: 2,
      },
    };

    // 任务统计
    this.taskStats = {};
    this.tasksToExecute.forEach((taskKey) => {
      if (this.taskConfigs[taskKey]) {
        this.taskStats[taskKey] = {
          success: 0,
          failed: 0,
          totalReward: 0,
        };
      }
    });

    // 低奖励控制
    this.lowRewardStreak = 0;
    this.lowRewardThreshold = KSLOW_REWARD_THRESHOLD;
    this.lowRewardLimit = KSLOW_REWARD_LIMIT;
    this.stopAllTasks = false;

    // 任务上限标记
    this.taskLimitReached = {};
    this.tasksToExecute.forEach((taskKey) => {
      if (this.taskConfigs[taskKey]) {
        this.taskLimitReached[taskKey] = false;
      }
    });
  }

  // 检查金币上限
  async checkCoinLimit() {
    try {
      const accountInfo = await getAccountBasicInfo(
        this.cookie,
        this.proxyUrl,
        this.index
      );
      if (accountInfo && accountInfo.totalCoin) {
        const currentCoin = parseInt(accountInfo.totalCoin);
        if (currentCoin >= this.coinLimit) {
          console.log(`💰 ${this.getAccountDisplayName()} 金币已达 ${currentCoin}，超过阈值 ${this.coinLimit}，停止任务`);
          this.coinExceeded = true;
          this.stopAllTasks = true;
          return true;
        }
      }
      return false;
    } catch (error) {
      console.log(`❌ ${this.getAccountDisplayName()} 金币检查异常: ${error.message}`);
      return false;
    }
  }

  // 获取账号显示名称
  getAccountDisplayName() {
    return `账号[${this.nickname}]${this.remark ? "(" + this.remark + ")" : ""}`;
  }

  // 从cookie中提取信息
  extractCookieInfo() {
    try {
      const egidMatch = this.cookie.match(/egid=([^;]+)/);
      const didMatch = this.cookie.match(/did=([^;]+)/);
      const userIdMatch = this.cookie.match(/userId=([^;]+)/);
      const apiStMatch = this.cookie.match(/kuaishou\.api_st=([^;]+)/);
      const appverMatch = this.cookie.match(/appver=([^;]+)/);

      this.egid = egidMatch ? egidMatch[1] : "";
      this.did = didMatch ? didMatch[1] : "";
      this.userId = userIdMatch ? userIdMatch[1] : "";
      this.kuaishouApiSt = apiStMatch ? apiStMatch[1] : "";
      this.appver = appverMatch ? appverMatch[1] : "13.7.20.10468";

      if (!this.egid || !this.did) {
        console.log(`⚠️ ${this.getAccountDisplayName()} cookie格式可能无egid或did，继续尝试...`);
      }
    } catch (error) {
      console.log(`❌ ${this.getAccountDisplayName()} 解析cookie失败: ${error.message}`);
    }
  }

  getTaskStats() {
    return this.taskStats;
  }

  // 打印任务统计
  printTaskStats() {
    console.log(`\n📊 ${this.getAccountDisplayName()} 任务统计:`);
    for (const [taskKey, stats] of Object.entries(this.taskStats)) {
      const taskName = this.taskConfigs[taskKey].name;
      console.log(`   ${taskName}: 成功${stats.success}次, 失败${stats.failed}次, 奖励${stats.totalReward}金币`);
    }
  }

  // 重试操作
  async retryOperation(operation, description, maxRetries = 3, delay = 2000) {
    let attempts = 0;
    let lastError = null;

    while (attempts < maxRetries) {
      try {
        const result = await operation();
        if (result) {
          return result;
        }
        lastError = new Error(description + " 返回空结果");
      } catch (error) {
        lastError = error;
      }

      attempts++;
      if (attempts < maxRetries) {
        console.log(`🔄 ${this.getAccountDisplayName()} ${description} 失败，重试 ${attempts}/${maxRetries}`);
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }

    return null;
  }

  // 获取广告信息
  async getAdInfo(taskConfig) {
    try {
      const adPath = "/rest/e/reward/mixed/ad";
      const formData = {
        encData: "|encData|",
        sign: "|sign|",
        cs: "false",
        client_key: "2ac2a76d",
        videoModelCrowdTag: "1_23",
        os: "android",
        "kuaishou.api_st": this.kuaishouApiSt,
        uQaTag: "1##swLdgl:99#ecPp:-9#cmNt:-0#cmHs:-3#cmMnsl:-0",
      };

      const queryData = {
        earphoneMode: "1",
        mod: "Xiaomi(23116PN5BC)",
        appver: this.appver,
        isp: "CUCC",
        language: "zh-cn",
        ud: this.userId,
        did_tag: "0",
        net: "WIFI",
        kcv: "1599",
        app: "0",
        kpf: "ANDROID_PHONE",
        ver: "11.6",
        android_os: "0",
        boardPlatform: "pineapple",
        kpn: "NEBULA",
        androidApiLevel: "35",
        country_code: "cn",
        sys: "ANDROID_15",
        sw: "1080",
        sh: "2400",
        abi: "arm64",
        userRecoBit: "0",
      };

      const requestBody = {
        appInfo: {
          appId: "kuaishou_nebula",
          name: "快手极速版",
          packageName: "com.kuaishou.nebula",
          version: this.appver,
          versionCode: -1,
        },
        deviceInfo: {
          osType: 1,
          osVersion: "15",
          deviceId: this.did,
          screenSize: {
            width: 1080,
            height: 2249,
          },
          ftt: "",
        },
        userInfo: {
          userId: this.userId,
          age: 0,
          gender: "",
        },
        impInfo: [
          {
            pageId: 11101,
            subPageId: taskConfig.subPageId,
            action: 0,
            browseType: 3,
            impExtData: "{}",
            mediaExtData: "{}",
          },
        ],
      };

      const encodedBody = Buffer.from(JSON.stringify(requestBody)).toString("base64");
      let encsign = await this.getSign(encodedBody);

      formData.encData = encsign.encdata;
      formData.sign = encsign.sign;

      let nesig = await this.requestSignService({
        urlpath: adPath,
        reqdata: qs.stringify(formData) + "&" + qs.stringify(queryData),
        api_client_salt: this.salt,
      });

      const finalQueryData = {
        ...queryData,
        sig: nesig.sig,
        __NS_sig3: nesig.__NS_sig3,
        __NS_xfalcon: "",
        __NStokensig: nesig.__NStokensig,
      };
      
      const url = "https://api.e.kuaishou.com" + adPath + "?" + querystring.stringify(finalQueryData);

      const { response, body: result } = await sendRequest(
        {
          method: "POST",
          url: url,
          headers: {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            Host: "api.e.kuaishou.com",
            "User-Agent": "kwai-android aegon/3.56.0",
            Cookie: "kuaishou_api_st=" + this.kuaishouApiSt,
          },
          form: formData,
          timeout: 12000,
        },
        this.proxyUrl,
        `${this.getAccountDisplayName()} 获取广告`
      );

      if (!result) {
        return null;
      }

      if (result.errorMsg === "OK" && result.feeds && result.feeds[0] && result.feeds[0].ad) {
        const caption = result.feeds[0].caption || result.feeds[0].ad?.caption || "";
        if (caption) {
          console.log(`✅ ${this.getAccountDisplayName()} 成功获取广告：${caption}`);
        }

        const expTag = result.feeds[0].exp_tag || "";
        const llsid = expTag.split("/")[1]?.split("_")?.[0] || "";

        return {
          cid: result.feeds[0].ad.creativeId,
          llsid: llsid,
        };
      }

      return null;
    } catch (error) {
      console.log(`❌ ${this.getAccountDisplayName()} 获取广告异常: ${error.message}`);
      return null;
    }
  }

  // 生成签名
  async generateSignature(creativeId, llsid, taskKey, taskConfig) {
    try {
      const bizData = JSON.stringify({
        businessId: taskConfig.businessId,
        endTime: this.endTime,
        extParams: "",
        mediaScene: "video",
        neoInfos: [
          {
            creativeId: creativeId,
            extInfo: "",
            llsid: llsid,
            requestSceneType: taskConfig.requestSceneType,
            taskType: taskConfig.taskType,
            watchExpId: "",
            watchStage: 0,
          },
        ],
        pageId: 11101,
        posId: taskConfig.posId,
        reportType: 0,
        sessionId: "",
        startTime: this.startTime,
        subPageId: taskConfig.subPageId,
      });
      
      const postData = "bizStr=" + encodeURIComponent(bizData) + "&cs=false&client_key=2ac2a76d&kuaishou.api_st=" + this.kuaishouApiSt;
      const urlData = this.queryParams + "&" + postData;

      const signResult = await this.requestSignService(
        {
          urlpath: this.taskReportPath,
          reqdata: urlData,
          api_client_salt: this.salt,
        },
        `${this.getAccountDisplayName()} 生成报告签名`
      );

      return {
        sig: signResult.sig,
        sig3: signResult.__NS_sig3,
        sigtoken: signResult.__NStokensig,
        post: postData,
      };
    } catch (error) {
      console.log(`❌ ${this.getAccountDisplayName()} 生成签名异常: ${error.message}`);
      return null;
    }
  }

  // 获取签名
  async getSign(requestData) {
    try {
      const { response, body: result } = await sendRequest({
        method: "POST",
        url: "http://ks.345yun.cn/ks.php",
        body: JSON.stringify({
          data: requestData,
        }),
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (result && result.status) {
        return result.data;
      }
    } catch (error) {
      console.log(`❌ ${this.getAccountDisplayName()} 获取签名失败: ${error.message}`);
    }
  }

  // 请求签名服务
  async requestSignService(requestData, description) {
    let returnData = {};

    let newreqdata = {
      path: requestData.urlpath,
      data: requestData.reqdata,
      salt: requestData.api_client_salt,
    };

    const { response, body: result } = await sendRequest(
      {
        method: "POST",
        url: "http://ks.345yun.cn/ks.php",
        headers: {
          "Content-Type": "application/json",
          "User-Agent": "Mozilla/5.0",
        },
        body: JSON.stringify(newreqdata),
        timeout: 15000,
      },
      null,
      description
    );

    if (result && result.status) {
      let __NS_sig3 = result.data.nssig3;
      let __NStokensig = result.data.nstokensig;
      Object.assign(returnData, {
        __NS_sig3,
        __NStokensig,
        sig: result.data.sig,
      });

      return returnData;
    }
    
    return null;
  }

  // 提交报告
  async submitReport(sig, sig3, sigtoken, postData, taskKey, taskConfig) {
    try {
      const url = "https://api.e.kuaishou.com" + this.taskReportPath + "?" + (this.queryParams + "&sig=" + sig + "&__NS_sig3=" + sig3 + "&__NS_xfalcon=&__NStokensig=" + sigtoken);

      const { response, body: result } = await sendRequest(
        {
          method: "POST",
          url: url,
          headers: {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            Host: "api.e.kuaishou.cn",
            "User-Agent": "kwai-android aegon/3.56.0",
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: postData,
          timeout: 12000,
        },
        this.proxyUrl,
        `${this.getAccountDisplayName()} 提交任务`
      );

      if (!result) {
        return {
          success: false,
          reward: 0,
        };
      }

      if (result.result === 1) {
        const reward = result.data?.neoAmount || 0;
        console.log(`💰 ${this.getAccountDisplayName()} ${taskConfig.name}获得${reward}金币奖励！`);

        if (reward <= this.lowRewardThreshold) {
          this.lowRewardStreak++;
          this.did = generateKuaishouDid();
          console.log(`⚠️ ${this.getAccountDisplayName()} 金币奖励(${reward})低于阈值，当前连续低奖励次数：${this.lowRewardStreak}/${this.lowRewardLimit}`);
          
          if (this.lowRewardStreak >= this.lowRewardLimit) {
            console.log(`🏁 ${this.getAccountDisplayName()} 连续${this.lowRewardLimit}次低奖励，停止全部任务`);
            this.stopAllTasks = true;
          }
        } else {
          this.lowRewardStreak = 0;
        }

        return {
          success: true,
          reward: reward,
        };
      }

      if ([20107, 20108, 1003, 415].includes(result.result)) {
        console.log(`⚠️ ${this.getAccountDisplayName()} ${taskConfig.name} 已达上限`);
        this.taskLimitReached[taskKey] = true;
        return {
          success: false,
          reward: 0,
        };
      }

      console.log(`❌ ${this.getAccountDisplayName()} ${taskConfig.name} 奖励失败`);
      return {
        success: false,
        reward: 0,
      };
    } catch (error) {
      console.log(`❌ ${this.getAccountDisplayName()} 提交任务异常: ${error.message}`);
      return {
        success: false,
        reward: 0,
      };
    }
  }

  // 执行单个任务
  async executeTask(taskKey) {
    const taskConfig = this.taskConfigs[taskKey];
    if (!taskConfig) {
      console.log(`❌ ${this.getAccountDisplayName()} 未知任务: ${taskKey}`);
      return false;
    }

    if (this.taskLimitReached[taskKey]) {
      return false;
    }

    try {
      const adInfo = await this.retryOperation(
        () => this.getAdInfo(taskConfig),
        `获取${taskConfig.name}信息`,
        3
      );
      if (!adInfo) {
        this.taskStats[taskKey].failed++;
        return false;
      }

      const watchTime = Math.floor(Math.random() * 10000) + 30000;
      console.log(`👀 ${this.getAccountDisplayName()} ${taskConfig.name} ${generateRandomInteractionMessage()} ${Math.round(watchTime / 1000)}秒`);
      await new Promise((resolve) => setTimeout(resolve, watchTime));

      const signature = await this.retryOperation(
        () => this.generateSignature(adInfo.cid, adInfo.llsid, taskKey, taskConfig),
        `生成${taskConfig.name}签名`,
        3
      );
      if (!signature) {
        this.taskStats[taskKey].failed++;
        return false;
      }

      const submitResult = await this.retryOperation(
        () => this.submitReport(signature.sig, signature.sig3, signature.sigtoken, signature.post, taskKey, taskConfig),
        `提交${taskConfig.name}报告`,
        3
      );

      if (submitResult?.success) {
        this.taskStats[taskKey].success++;
        this.taskStats[taskKey].totalReward += submitResult.reward || 0;
        return true;
      }

      this.taskStats[taskKey].failed++;
      return false;
    } catch (error) {
      console.log(`❌ ${this.getAccountDisplayName()} 任务异常(${taskKey}): ${error.message}`);
      this.taskStats[taskKey].failed++;
      return false;
    }
  }

  // 按优先级执行所有任务
  async executeAllTasksByPriority() {
    const results = {};

    for (const taskKey of this.tasksToExecute) {
      if (this.stopAllTasks) {
        break;
      }

      if (!this.taskConfigs[taskKey]) {
        console.log(`⚠️ ${this.getAccountDisplayName()} 跳过未知任务: ${taskKey}`);
        continue;
      }

      console.log(`🚀 ${this.getAccountDisplayName()} 开始任务：${this.taskConfigs[taskKey].name}`);
      results[taskKey] = await this.executeTask(taskKey);

      if (this.stopAllTasks) {
        break;
      }

      if (taskKey !== this.tasksToExecute[this.tasksToExecute.length - 1]) {
        const waitTime = Math.floor(Math.random() * 8000) + 7000;
        console.log(`⏱ ${this.getAccountDisplayName()} 等待 ${Math.round(waitTime / 1000)}秒进入下一任务`);
        await new Promise((resolve) => setTimeout(resolve, waitTime));
      }
    }

    return results;
  }
}

// 解析账号配置
function parseAccountConfig(configString) {
  const parts = String(configString || "").trim().split("#");
  if (parts.length < 2) {
    return null;
  }

  let remark = "";
  let cookie = "";
  let salt = "";
  let proxyUrl = null;

  if (parts.length === 2) {
    // 格式: ck#salt
    cookie = parts[0];
    salt = parts[1];
  } else if (parts.length === 3) {
    // 格式: remark#ck#salt 或 ck#salt#proxy
    if (/socks5:\/\//i.test(parts[2])) {
      cookie = parts[0];
      salt = parts[1];
      proxyUrl = parts[2];
    } else {
      remark = parts[0];
      cookie = parts[1];
      salt = parts[2];
    }
  } else if (parts.length >= 4) {
    // 格式: remark#ck#salt#proxy
    remark = parts[0];
    cookie = parts[1];
    salt = parts.slice(2, parts.length - 1).join("#");
    proxyUrl = parts[parts.length - 1];
  }

  if (proxyUrl) {
    if (proxyUrl.includes("|")) {
      console.log(`🔧 解析代理格式: ${proxyUrl}`);
      const proxyParts = proxyUrl.split("|");
      if (proxyParts.length >= 2) {
        const [ip, port, username, password] = proxyParts;
        proxyUrl = `socks5://${username}:${password}@${ip}:${port}`;
      } else {
        proxyUrl = null;
        console.log(`⚠️ 代理字段格式错误，忽略：${proxyUrl}`);
      }
    } else if (!/^socks5:\/\//i.test(proxyUrl)) {
      console.log(`⚠️ 代理字段不是 socks5:// URL，忽略：${proxyUrl}`);
      proxyUrl = null;
    }
  }

  return {
    remark: remark || "",
    salt: salt,
    cookie: cookie,
    proxyUrl: proxyUrl,
  };
}

// 从环境变量加载账号
function loadAccountsFromEnv() {
  const accountConfigs = getAccountConfigsFromEnv();
  const accounts = [];

  for (const configString of accountConfigs) {
    const accountConfig = parseAccountConfig(configString);
    if (accountConfig) {
      accounts.push(accountConfig);
    } else {
      console.log(`❌ 账号格式错误：${configString}`);
    }
  }

  accounts.forEach((account, index) => {
    account.index = index + 1;
  });

  return accounts;
}

// 并发执行
async function concurrentExecute(items, concurrency, processor) {
  const results = new Array(items.length);
  let currentIndex = 0;

  async function worker() {
    while (true) {
      const index = currentIndex++;
      if (index >= items.length) {
        return;
      }

      const item = items[index];
      try {
        results[index] = await processor(item, index);
      } catch (error) {
        console.log(`❌ 并发执行异常（index=${index + 1}）：${error.message}`);
        results[index] = null;
      }
    }
  }

  const workers = Array.from({ length: Math.min(concurrency, items.length) }, worker);
  await Promise.all(workers);

  return results;
}

// 处理单个账号
async function processAccount(accountConfig) {
  const getAccountDisplayName = () => {
    return `账号[${accountConfig.index}]${accountConfig.remark ? "(" + accountConfig.remark + ")" : ""}`;
  };

  if (accountConfig.proxyUrl) {
    console.log(`🔌 ${getAccountDisplayName()} 测试代理连接中...`);
    const proxyTest = await testProxyConnectivity(accountConfig.proxyUrl, getAccountDisplayName());
    console.log(`   ${proxyTest.ok ? "✅" : "❌"} ${proxyTest.msg}`);
  } else {
    console.log(`🌐 ${getAccountDisplayName()} 未配置代理，使用直连`);
  }

  console.log(`🔍 ${getAccountDisplayName()} 获取账号信息中...`);
  let initialAccountInfo = await getAccountBasicInfo(accountConfig.cookie, accountConfig.proxyUrl, accountConfig.index);
  let nickname = initialAccountInfo?.nickname || "账号" + accountConfig.index;

  if (initialAccountInfo) {
    const totalCoin = initialAccountInfo.totalCoin != null ? initialAccountInfo.totalCoin : "未知";
    const allCash = initialAccountInfo.allCash != null ? initialAccountInfo.allCash : "未知";
    console.log(`✅ ${getAccountDisplayName()} 登录成功，金币: ${totalCoin}，余额: ${allCash}`);
  } else {
    console.log(`❌ ${getAccountDisplayName()} 基本信息获取失败，继续执行`);
  }

  const adTask = new KuaishouAdTask({
    ...accountConfig,
    nickname: nickname,
    tasksToExecute: tasksToExecute,
  });

  await adTask.checkCoinLimit();
  if (adTask.coinExceeded) {
    console.log(`💰 ${getAccountDisplayName()} 初始金币已超过阈值，不执行任务`);
    return {
      index: accountConfig.index,
      remark: accountConfig.remark || "无备注",
      nickname: nickname,
      initialCoin: initialAccountInfo?.totalCoin || 0,
      finalCoin: initialAccountInfo?.totalCoin || 0,
      coinChange: 0,
      initialCash: initialAccountInfo?.allCash || 0,
      finalCash: initialAccountInfo?.allCash || 0,
      cashChange: 0,
      stats: adTask.getTaskStats(),
      coinLimitExceeded: true,
    };
  }

  for (let round = 0; round < KSROUNDS; round++) {
    const waitTime = Math.floor(Math.random() * 8000) + 8000;
    console.log(`⏱ ${getAccountDisplayName()} 第${round + 1}轮，等待 ${Math.round(waitTime / 1000)}秒`);
    
    console.log(`🚀 ${getAccountDisplayName()} 开始第${round + 1}轮任务`);
    const roundResults = await adTask.executeAllTasksByPriority();

    if (Object.values(roundResults).some(Boolean)) {
      console.log(`✅ ${getAccountDisplayName()} 第${round + 1}轮执行完成`);
    } else {
      console.log(`⚠️ ${getAccountDisplayName()} 第${round + 1}轮没有成功任务`);
    }

    if (adTask.stopAllTasks) {
      console.log(`🏁 ${getAccountDisplayName()} 达到停止条件，终止后续轮次`);
      break;
    }

    if (round < KSROUNDS - 1) {
      const nextWaitTime = Math.floor(Math.random() * 10000) + 10000;
      console.log(`⏱ ${getAccountDisplayName()} 等待 ${Math.round(nextWaitTime / 1000)}秒进入下一轮`);
      await new Promise((resolve) => setTimeout(resolve, nextWaitTime));
    }
  }

  const finalAccountInfo = await getAccountBasicInfo(accountConfig.cookie, accountConfig.proxyUrl, accountConfig.index);
  const initialCoin = initialAccountInfo?.totalCoin || 0;
  const finalCoin = finalAccountInfo?.totalCoin || 0;
  const coinChange = finalCoin - initialCoin;
  const initialCash = initialAccountInfo?.allCash || 0;
  const finalCash = finalAccountInfo?.allCash || 0;
  const cashChange = finalCash - initialCash;

  adTask.printTaskStats();

  return {
    index: accountConfig.index,
    remark: accountConfig.remark || "无备注",
    nickname: nickname,
    initialCoin: initialCoin,
    finalCoin: finalCoin,
    coinChange: coinChange,
    initialCash: initialCash,
    finalCash: finalCash,
    cashChange: cashChange,
    stats: adTask.getTaskStats(),
    coinLimitExceeded: adTask.coinExceeded,
  };
}

// 美化打印：简洁的结果汇总
function printAccountsSummary(accountResults) {
  if (!accountResults.length) {
    console.log("\n❌ 没有可显示的账号信息。");
    return;
  }

  // 计算统计数据
  const totalInitialCoin = accountResults.reduce((sum, account) => sum + (parseInt(account.initialCoin) || 0), 0);
  const totalFinalCoin = accountResults.reduce((sum, account) => sum + (parseInt(account.finalCoin) || 0), 0);
  const totalCoinChange = totalFinalCoin - totalInitialCoin;

  const totalInitialCash = accountResults.reduce((sum, account) => sum + (parseFloat(account.initialCash) || 0), 0);
  const totalFinalCash = accountResults.reduce((sum, account) => sum + (parseFloat(account.finalCash) || 0), 0);
  const totalCashChange = totalFinalCash - totalInitialCash;

  let totalTasks = 0;
  let totalSuccessTasks = 0;
  let totalReward = 0;

  accountResults.forEach((account) => {
    if (account.stats) {
      Object.values(account.stats).forEach((stat) => {
        totalTasks += stat.success + stat.failed;
        totalSuccessTasks += stat.success;
        totalReward += stat.totalReward;
      });
    }
  });

  const successRate = totalTasks > 0 ? ((totalSuccessTasks / totalTasks) * 100).toFixed(1) : "0.0";
  const coinLimitExceededCount = accountResults.filter((account) => account.coinLimitExceeded).length;

  // 美化输出
  console.log("\n" + "=".repeat(60));
  console.log("📊 任务执行结果汇总");
  console.log("=".repeat(60));
  console.log(`👥 总账号数: ${accountResults.length}`);
  console.log(`💰 超过金币阈值: ${coinLimitExceededCount}个`);
  console.log(`📈 总任务数: ${totalTasks} (成功率: ${successRate}%)`);
  console.log(`🎯 总金币变化: ${totalCoinChange >= 0 ? '+' : ''}${totalCoinChange}`);
  console.log(`🏆 总金币奖励: ${totalReward}`);
  console.log(`💵 总余额变化: ${totalCashChange >= 0 ? '+' : ''}${totalCashChange.toFixed(2)}`);
  console.log("-".repeat(60));

  // 账号详情表格
  console.log("\n📋 账号详情:");
  console.log("序号".padEnd(6) + "备注".padEnd(16) + "昵称".padEnd(20) + "金币变化".padEnd(12) + "余额变化");
  console.log("-".repeat(60));

  accountResults.forEach((account) => {
    const coinChangeStr = account.coinChange >= 0 ? `+${account.coinChange}` : `${account.coinChange}`;
    const cashChangeStr = account.cashChange >= 0 ? `+${account.cashChange.toFixed(2)}` : `${account.cashChange.toFixed(2)}`;
    const status = account.coinLimitExceeded ? " ⚠️" : "";
    
    console.log(
      `${account.index}`.padEnd(6) +
      `${account.remark}`.substring(0, 14).padEnd(16) +
      `${account.nickname}${status}`.substring(0, 18).padEnd(20) +
      coinChangeStr.padEnd(12) +
      cashChangeStr
    );
  });

  console.log("=".repeat(60));
  console.log("✅ 任务执行完成");
  console.log("=".repeat(60));
}

// 主函数
(async () => {
  const accounts = loadAccountsFromEnv();
  console.log(`📊 共找到 ${accounts.length} 个有效账号`);

  if (!accounts.length) {
    console.log("❌ 没有找到有效账号，程序退出");
    process.exit(1);
  }

  const maxConcurrency = getEnvNumber("MAX_CONCURRENCY", 888);
  console.log(`\n⚡ 并发数: ${maxConcurrency}    轮数: ${KSROUNDS}\n`);

  const results = [];

  await concurrentExecute(accounts, maxConcurrency, async (account) => {
    console.log(`\n── 🚀 开始处理 ${account.index}号账号${account.remark ? "(" + account.remark + ")" : ""} ──`);

    try {
      const result = await processAccount(account);
      results.push({
        index: account.index,
        remark: account.remark || "无备注",
        nickname: result?.nickname || `账号${account.index}`,
        initialCoin: result?.initialCoin || 0,
        finalCoin: result?.finalCoin || 0,
        coinChange: result?.coinChange || 0,
        initialCash: result?.initialCash || 0,
        finalCash: result?.finalCash || 0,
        cashChange: result?.cashChange || 0,
        stats: result?.stats || {},
        coinLimitExceeded: result?.coinLimitExceeded || false,
      });
    } catch (error) {
      console.log(`❌ 账号[${account.index}] 执行异常：${error.message}`);
      results.push({
        index: account.index,
        remark: account.remark || "无备注",
        nickname: `账号${account.index}`,
        initialCoin: 0,
        finalCoin: 0,
        coinChange: 0,
        initialCash: 0,
        finalCash: 0,
        cashChange: 0,
        error: error.message,
      });
    }
  });

  results.sort((a, b) => a.index - b.index);

  console.log("\n🎉 全部任务完成!");
  printAccountsSummary(results);
})();