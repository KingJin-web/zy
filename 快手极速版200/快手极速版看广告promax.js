//const $ = new Env('快手极速版看广告promax免费');
// ksck   ck#salt#代理
//Task food,box,look
//代理格式 socks5://username:password@host:port
//代理推荐http://www.tianxingip.com/proxy/index/index/code/smallfawn.html
//代理推荐http://www.gzsk5.com/#/register?invitation=smallfawn


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

// 新增：获取环境变量
const KSLOW_REWARD_THRESHOLD = getEnvNumber("KSLOW_REWARD_THRESHOLD", 10);
const KSROUNDS = getEnvNumber("KSROUNDS", 35);
const KSCOIN_LIMIT = getEnvNumber("KSCOIN_LIMIT", 500000);
const KSLOW_REWARD_LIMIT = getEnvNumber("KSLOW_REWARD_LIMIT", 3);

// 获取要执行的任务列表
function getTasksToExecute() {
  const taskEnv = process.env.Task;
  if (!taskEnv) {
    console.log("未设置Task环境变量，将执行所有任务 (food, box, look)");
    return ["food", "box", "look"];
  }

  const tasks = taskEnv
    .split(",")
    .map((task) => task.trim().toLowerCase())
    .filter(Boolean);
  const validTasks = ["food", "box", "look"];
  const filteredTasks = tasks.filter((task) => validTasks.includes(task));

  if (filteredTasks.length === 0) {
    console.log("Task环境变量中没有有效任务，将执行所有任务 (food, box, look)");
    return ["food", "box", "look"];
  }

  console.log(
    "从Task环境变量中解析到要执行的任务: " + filteredTasks.join(", ")
  );
  return filteredTasks;
}

// 从 ksck, ksck1 到 ksck666 读取账号配置
function getAccountConfigsFromEnv() {
  const configs = [];
  const seenConfigs = new Set();

  if (process.env.ksck) {
    const ksckValue = process.env.ksck;
    const configStrings = ksckValue
      .split("&")
      .map((config) => config.trim())
      .filter(Boolean);
    configs.push(...configStrings);
  }

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

  const uniqueConfigs = [];
  for (const config of configs) {
    if (!seenConfigs.has(config)) {
      seenConfigs.add(config);
      uniqueConfigs.push(config);
    }
  }

  console.log(
    `从ksck及ksck1到ksck666环境变量中解析到 ${uniqueConfigs.length} 个唯一配置`
  );
  return uniqueConfigs;
}

const accountConfigs = getAccountConfigsFromEnv();
const accountCount = accountConfigs.length;
const tasksToExecute = getTasksToExecute();

console.log(
  "================================================================================"
);
console.log(
  "                                  ⭐ 快手至尊金币至尊普通版 ⭐                                "
);
console.log(
  "                            🏆 安全稳定 · 高效收益 · 尊贵体验 🏆                        "
);
console.log("================🎉 系统初始化完成，快手至尊金币版启动成功！🎉");
console.log("💎 检测到环境变量配置：" + accountCount + "个账号");
console.log("🎯 将执行以下任务：" + tasksToExecute.join(", "));
console.log(
  `🎯 配置参数：轮数=${KSROUNDS}, 金币上限=${KSCOIN_LIMIT}, 低奖励阈值=${KSLOW_REWARD_THRESHOLD}, 连续低奖励上限=${KSLOW_REWARD_LIMIT}`
);

if (accountCount > (process.env.MAX_CONCURRENCY || 999)) {
  console.log(
    "错误: 检测到 " +
      accountCount +
      " 个账号配置，最多只允许" +
      (process.env.MAX_CONCURRENCY || 999) +
      "个"
  );
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
    console.log("生成did失败: " + error.message);
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
      if (isDevMode) {
        //console.log("[调试] " + description + " 使用代理: " + proxyUrl);
      }
    } catch (proxyError) {
      console.log(
        "[错误] " +
          description +
          " 代理URL无效(" +
          proxyError.message +
          ")，尝试直连模式"
      );
      if (isDevMode) {
        console.log("[调试] 代理无效，自动切换到直连模式");
      }
    }
  } else {
    if (isDevMode) {
      console.log("[调试] 未配置代理，使用直连模式");
    }
  }

  if (isDevMode) {
    const method = finalOptions.method || "GET";
    //console.log("[调试] " + description + " -> " + method + " " + finalOptions.url);
  }

  try {
    // 配置 axios 请求选项
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
    if (error.response) {
      // 服务器返回了错误状态码
      return { response: error.response, body: null };
    } else if (error.request) {
      // 请求发送失败
      if (error.name === "AggregateError" && Array.isArray(error.errors)) {
        console.log(
          "[调试] " +
            description +
            " 请求错误: AggregateError\n" +
            error.errors
              .map((err, index) => "  [" + index + "] " + (err?.message || err))
              .join("\n")
        );
      } else {
        // console.log("[调试] " + description + " 请求错误: " + (error.message || String(error)));
      }
    } else {
      // 其他错误
      // console.log("[调试] " + description + " 请求错误: " + (error.message || String(error)));
    }

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
      msg: `✅ SOCKS5代理正常，成功访问 baidu.com，出口IP: ${baiduResult.origin}`,
      ip: baiduResult.origin,
    };
  }
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
    "账号[" + accountId + "] 获取基本信息"
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

// 文本居中对齐
function centerAlign(text, width) {
  text = String(text);
  if (text.length >= width) {
    return text.substring(0, width);
  }

  const padding = width - text.length;
  const leftPadding = Math.floor(padding / 2);
  const rightPadding = padding - leftPadding;

  return " ".repeat(leftPadding) + text + " ".repeat(rightPadding);
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
    this.nickname = nickname || remark || "账号" + index; // Use remark if provided, else nickname or default
    this.remark = remark; // Store remark for use in logging
    this.proxyUrl = proxyUrl;
    this.coinLimit = KSCOIN_LIMIT;
    this.coinExceeded = false;
    this.tasksToExecute = tasksToExecute;

    this.extractCookieInfo();

    this.headers = {
      Host: "nebula.kuaishou.com",
      Connection: "keep-alive",
      "User-Agent":
        "Mozilla/5.0 (Linux; Android 10; MI 8 Lite Build/QKQ1.190910.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.101 Mobile Safari/537.36",
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

    this.lowRewardStreak = 0;
    this.lowRewardThreshold = KSLOW_REWARD_THRESHOLD;
    this.lowRewardLimit = KSLOW_REWARD_LIMIT;
    this.stopAllTasks = false;

    this.taskLimitReached = {};
    this.tasksToExecute.forEach((taskKey) => {
      if (this.taskConfigs[taskKey]) {
        this.taskLimitReached[taskKey] = false;
      }
    });
  }

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
          console.log(
            `⚠️ 账号[${this.nickname}]${
              this.remark ? "（" + this.remark + "）" : ""
            } 金币已达 ${currentCoin}，超过 ${this.coinLimit} 阈值，将停止任务`
          );
          this.coinExceeded = true;
          this.stopAllTasks = true;
          return true;
        }
      }
      return false;
    } catch (error) {
      console.log(
        `账号[${this.nickname}]${
          this.remark ? "（" + this.remark + "）" : ""
        } 金币检查异常: ${error.message}`
      );
      return false;
    }
  }

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
        console.log(
          `账号[${this.nickname}]${
            this.remark ? "（" + this.remark + "）" : ""
          } cookie格式可能无 egid 或 did，但继续尝试...`
        );
      }
    } catch (error) {
      console.log(
        `账号[${this.nickname}]${
          this.remark ? "（" + this.remark + "）" : ""
        } 解析cookie失败: ${error.message}`
      );
    }
  }

  getTaskStats() {
    return this.taskStats;
  }

  printTaskStats() {
    console.log(
      `\n账号[${this.nickname}]${
        this.remark ? "（" + this.remark + "）" : ""
      } 任务执行统计:`
    );
    for (const [taskKey, stats] of Object.entries(this.taskStats)) {
      const taskName = this.taskConfigs[taskKey].name;
      console.log(
        `  ${taskName}: 成功${stats.success}次, 失败${stats.failed}次, 总奖励${stats.totalReward}金币`
      );
    }
  }

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
        console.log(
          `账号[${this.nickname}]${
            this.remark ? "（" + this.remark + "）" : ""
          } ${description} 异常: ${error.message}`
        );
      }

      attempts++;
      if (attempts < maxRetries) {
        console.log(
          `账号[${this.nickname}]${
            this.remark ? "（" + this.remark + "）" : ""
          } ${description} 失败，重试 ${attempts}/${maxRetries}`
        );
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }

    if (isDevMode && lastError) {
      //console.log("[调试] " + description + " 最终失败: " + lastError.message);
    }

    return null;
  }

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

      const encodedBody = Buffer.from(JSON.stringify(requestBody)).toString(
        "base64"
      );

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
      const url =
        "https://api.e.kuaishou.com" +
        adPath +
        "?" +
        querystring.stringify(finalQueryData);

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
        `账号[${this.nickname}]${
          this.remark ? "（" + this.remark + "）" : ""
        } 获取广告`
      );

      if (!result) {
        return null;
      }

      if (
        result.errorMsg === "OK" &&
        result.feeds &&
        result.feeds[0] &&
        result.feeds[0].ad
      ) {
        const caption =
          result.feeds[0].caption || result.feeds[0].ad?.caption || "";
        if (caption) {
          console.log(
            `✅ 账号[${this.nickname}]${
              this.remark ? "（" + this.remark + "）" : ""
            } 成功获取到广告信息：${caption}`
          );
        }

        const expTag = result.feeds[0].exp_tag || "";
        const llsid = expTag.split("/")[1]?.split("_")?.[0] || "";

        return {
          cid: result.feeds[0].ad.creativeId,
          llsid: llsid,
        };
      }

      if (isDevMode) {
        //console.log("[调试] getAdInfo 原始响应:", JSON.stringify(result));
      }

      return null;
    } catch (error) {
      console.log(error);

      console.log(
        `❌ 账号[${this.nickname}]${
          this.remark ? "（" + this.remark + "）" : ""
        } 获取广告异常: ${error.message}`
      );
      return null;
    }
  }

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
      const postData =
        "bizStr=" +
        encodeURIComponent(bizData) +
        "&cs=false&client_key=2ac2a76d&kuaishou.api_st=" +
        this.kuaishouApiSt;
      const urlData = this.queryParams + "&" + postData;

      const signResult = await this.requestSignService(
        {
          urlpath: this.taskReportPath,
          reqdata: urlData,
          api_client_salt: this.salt,
        },
        `账号[${this.nickname}]${
          this.remark ? "（" + this.remark + "）" : ""
        } 生成报告签名`
      );

      return {
        sig: signResult.sig,
        sig3: signResult.__NS_sig3,
        sigtoken: signResult.__NStokensig,
        post: postData,
      };
    } catch (error) {
      console.log(error);

      console.log(
        `❌ 账号[${this.nickname}]${
          this.remark ? "（" + this.remark + "）" : ""
        } 生成签名异常: ${error.message}`
      );
      return null;
    }
  }

  /* async generateSignature2(urlPath, urlData, salt, requestString) {
    const signResult = await this.requestSignService(
      {
        urlpath: urlPath,
        urldata: urlData,
        api_client_salt: salt,
        req_str: requestString,
      },
      `账号[${this.nickname}]${
        this.remark ? "（" + this.remark + "）" : ""
      } 生成广告签名`
    );

    if (!signResult) {
      return null;
    }

    return signResult.data || signResult;
  }*/

  async submitReport(sig, sig3, sigtoken, postData, taskKey, taskConfig) {
    try {
      const url =
        "https://api.e.kuaishou.com" +
        this.taskReportPath +
        "?" +
        (this.queryParams +
          "&sig=" +
          sig +
          "&__NS_sig3=" +
          sig3 +
          "&__NS_xfalcon=&__NStokensig=" +
          sigtoken);

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
        `账号[${this.nickname}]${
          this.remark ? "（" + this.remark + "）" : ""
        } 提交任务`
      );

      if (!result) {
        return {
          success: false,
          reward: 0,
        };
      }

      if (result.result === 1) {
        const reward = result.data?.neoAmount || 0;
        console.log(
          `💰 账号[${this.nickname}]${
            this.remark ? "（" + this.remark + "）" : ""
          } ${taskConfig.name}获得${reward}金币奖励！`
        );

        if (reward <= this.lowRewardThreshold) {
          this.lowRewardStreak++;
          this.did = generateKuaishouDid();
          console.log(
            `⚠️ 账号[${this.nickname}]${
              this.remark ? "（" + this.remark + "）" : ""
            } 金币奖励(${reward})低于阈值(${
              this.lowRewardThreshold
            })，模拟下载应用提升权重，当前连续低奖励次数：${
              this.lowRewardStreak
            }/${this.lowRewardLimit}`
          );
          if (this.lowRewardStreak >= this.lowRewardLimit) {
            console.log(
              `🏁 账号[${this.nickname}]${
                this.remark ? "（" + this.remark + "）" : ""
              } 连续${this.lowRewardLimit}次奖励≤${
                this.lowRewardThreshold
              }，停止全部任务`
            );
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
        console.log(
          `⚠️ 账号[${this.nickname}]${
            this.remark ? "（" + this.remark + "）" : ""
          } ${taskConfig.name} 已达上限`
        );
        this.taskLimitReached[taskKey] = true;
        return {
          success: false,
          reward: 0,
        };
      }

      console.log(
        `❌ 账号[${this.nickname}]${
          this.remark ? "（" + this.remark + "）" : ""
        } ${taskConfig.name} 奖励失败，result=${result.result} msg=${
          result.data || ""
        }`
      );

      if (isDevMode) {
        //console.log("[调试] submitReport 原始响应:", JSON.stringify(result));
      }

      return {
        success: false,
        reward: 0,
      };
    } catch (error) {
      console.log(
        `❌ 账号[${this.nickname}]${
          this.remark ? "（" + this.remark + "）" : ""
        } 提交任务异常: ${error.message}`
      );
      return {
        success: false,
        reward: 0,
      };
    }
  }
  async getSign(requestData) {
    try {
      const { response, body: result } = await sendRequest({
        method: "POST",
        url: "https://ks.smallfawn.top/encsign",
        body: JSON.stringify({
          data: requestData,
        }),
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (result.status) {
        return result.data;
      }
    } catch (error) {}
  }
  async requestSignService(requestData, description) {
    /*const cardKey = (process.env.ptkm || "").trim();
    if (!cardKey) {
      console.log(
        `❌ 账号[${this.nickname}]${
          this.remark ? "（" + this.remark + "）" : ""
        } 签名失败: 未提供卡密`
      );
      return null;
    }*/
    let returnData = {};

    let newreqdata = {
      path: requestData.urlpath,
      data: requestData.reqdata,
      salt: requestData.api_client_salt,
    };

    const { response, body: result } = await sendRequest(
      {
        method: "POST",
        url: "https://ks.smallfawn.top/nssig",
        headers: {
          "Content-Type": "application/json",
          "User-Agent": "Mozilla/5.0",
          //"X-Card-Key": cardKey,
        },
        body: JSON.stringify(newreqdata),
        timeout: 15000,
      },
      null,
      description + "（签名服务）"
    );

    /*if (!result) {
      if (response && [403, 405, 502].includes(response.statusCode)) {
        if (response.statusCode === 403) {
          console.log(
            `❌ 账号[${this.nickname}]${
              this.remark ? "（" + this.remark + "）" : ""
            } 签名失败: HTTP状态码 403 - 卡密过期，请检查或更换卡密`
          );
        } else {
          console.log(
            `❌ 账号[${this.nickname}]${
              this.remark ? "（" + this.remark + "）" : ""
            } 签名失败: HTTP状态码 ${response.statusCode}，自动停止脚本运行`
          );
        }
        process.exit(1);
      }
      console.log(
        `❌ 账号[${this.nickname}]${
          this.remark ? "（" + this.remark + "）" : ""
        } 签名失败: 无响应`
      );
      return null;
    }

    if (result.success && result.status === "queued" && result.queue_id) {
      const queueResult = await this.pollQueueStatus(result.queue_id);
      if (
        queueResult &&
        queueResult.success &&
        (queueResult.status === "completed" ||
          queueResult.status === "processed")
      ) {
        return queueResult;
      }
      console.log(
        `账号[${this.nickname}]${
          this.remark ? "（" + this.remark + "）" : ""
        } 签名失败: ${queueResult?.error || queueResult?.status || "未知"}`
      );
      return null;
    }

    if (
      result.success &&
      (!result.status ||
        result.status === "processed" ||
        result.status === "completed")
    ) {
      return result;
    }

    console.log(
      `账号[${this.nickname}]${
        this.remark ? "（" + this.remark + "）" : ""
      } 签名失败: ${result.error || result.message || result.status || "未知"}`
    );
    return null;*/
    if (result) {
      let __NS_sig3 = result.data.nssig3;
      let __NStokensig = result.data.nstokensig;
      Object.assign(returnData, {
        __NS_sig3,
        __NStokensig,
        sig: result.data.sig,
      });

      return returnData;
    }
  }

  /*async pollQueueStatus(queueId, maxTime = 30000, interval = 2000) {
    const startTime = Date.now();

    while (Date.now() - startTime < maxTime) {
      const { response, body: result } = await sendRequest(
        {
          method: "GET",
          url: queueStatusApiUrl + "?queue_id=" + encodeURIComponent(queueId),
          headers: {
            "User-Agent": "Mozilla/5.0",
          },
          timeout: 10000,
        },
        null,
        `账号[${this.nickname}]${
          this.remark ? "（" + this.remark + "）" : ""
        } 签名排队`
      );

      if (result?.success) {
        if (result.status === "completed" || result.status === "processed") {
          return result;
        }
        if (result.status === "failed") {
          return result;
        }
      }

      await new Promise((resolve) => setTimeout(resolve, interval));
    }

    return {
      success: false,
      status: "failed",
      error: "queue_timeout",
    };
  }*/

  async executeTask(taskKey) {
    const taskConfig = this.taskConfigs[taskKey];
    if (!taskConfig) {
      console.log(
        `❌ 账号[${this.nickname}]${
          this.remark ? "（" + this.remark + "）" : ""
        } 未知任务: ${taskKey}`
      );
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
      console.log(
        `🔍 账号[${this.nickname}]${
          this.remark ? "（" + this.remark + "）" : ""
        } ==>${
          taskConfig.name
        } ${generateRandomInteractionMessage()} ${Math.round(
          watchTime / 1000
        )} 秒`
      );
      await new Promise((resolve) => setTimeout(resolve, watchTime));

      const signature = await this.retryOperation(
        () =>
          this.generateSignature(adInfo.cid, adInfo.llsid, taskKey, taskConfig),
        `生成${taskConfig.name}签名`,
        3
      );
      if (!signature) {
        this.taskStats[taskKey].failed++;
        return false;
      }

      const submitResult = await this.retryOperation(
        () =>
          this.submitReport(
            signature.sig,
            signature.sig3,
            signature.sigtoken,
            signature.post,
            taskKey,
            taskConfig
          ),
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
      console.log(
        `❌ 账号[${this.nickname}]${
          this.remark ? "（" + this.remark + "）" : ""
        } 任务异常(${taskKey}): ${error.message}`
      );
      this.taskStats[taskKey].failed++;
      return false;
    }
  }

  async executeAllTasksByPriority() {
    const results = {};

    for (const taskKey of this.tasksToExecute) {
      if (this.stopAllTasks) {
        break;
      }

      if (!this.taskConfigs[taskKey]) {
        console.log(
          `⚠️ 账号[${this.nickname}]${
            this.remark ? "（" + this.remark + "）" : ""
          } 跳过未知任务: ${taskKey}`
        );
        continue;
      }

      console.log(
        `🚀 账号[${this.nickname}]${
          this.remark ? "（" + this.remark + "）" : ""
        } 开始任务：${this.taskConfigs[taskKey].name}`
      );
      results[taskKey] = await this.executeTask(taskKey);

      if (this.stopAllTasks) {
        break;
      }

      if (taskKey !== this.tasksToExecute[this.tasksToExecute.length - 1]) {
        const waitTime = Math.floor(Math.random() * 8000) + 7000;
        console.log(
          `⏱ 账号[${this.nickname}]${
            this.remark ? "（" + this.remark + "）" : ""
          } 下一个任务，随机等待 ${Math.round(waitTime / 1000)} 秒`
        );
        await new Promise((resolve) => setTimeout(resolve, waitTime));
      }
    }

    return results;
  }
}

function parseAccountConfig(configString) {
  const parts = String(configString || "")
    .trim()
    .split("#");
  if (parts.length < 2) {
    return null;
  }

  let remark = "";
  let cookie = "";
  let salt = "";
  let proxyUrl = null;

  if (parts.length === 2) {
    // Format: ck#salt
    cookie = parts[0];
    salt = parts[1];
  } else if (parts.length === 3) {
    // Format: remark#ck#salt or ck#salt#proxy
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
    // Format: remark#ck#salt#proxy
    remark = parts[0];
    cookie = parts[1];
    salt = parts.slice(2, parts.length - 1).join("#");
    proxyUrl = parts[parts.length - 1];
  }

  //cookie = cookie.replace("kpn=NEBULA", "kpn=KUAISHOU");

  if (proxyUrl) {
    if (proxyUrl.includes("|")) {
      console.log(`开始解析代理格式: ${proxyUrl}`);
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

function loadAccountsFromEnv() {
  const accountConfigs = getAccountConfigsFromEnv();
  const accounts = [];

  for (const configString of accountConfigs) {
    const accountConfig = parseAccountConfig(configString);
    if (accountConfig) {
      accounts.push(accountConfig);
    } else {
      console.log(`账号格式错误：${configString}`);
    }
  }

  accounts.forEach((account, index) => {
    account.index = index + 1;
  });

  return accounts;
}

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
        console.log(`并发执行异常（index=${index + 1}）：${error.message}`);
        results[index] = null;
      }
    }
  }

  const workers = Array.from(
    { length: Math.min(concurrency, items.length) },
    worker
  );
  await Promise.all(workers);

  return results;
}

async function processAccount(accountConfig) {
  if (accountConfig.proxyUrl) {
    console.log(
      `账号[${accountConfig.index}]${
        accountConfig.remark ? "（" + accountConfig.remark + "）" : ""
      } 🔌 测试代理连接中...`
    );
    const proxyTest = await testProxyConnectivity(
      accountConfig.proxyUrl,
      `账号[${accountConfig.index}]${
        accountConfig.remark ? "（" + accountConfig.remark + "）" : ""
      }`
    );
    console.log(
      `  - ${
        proxyTest.ok
          ? "✅ 代理验证通过，IP: " + proxyTest.ip
          : "❌ 代理验证失败"
      }: ${proxyTest.msg}`
    );

    if (proxyTest.ok && proxyTest.ip && proxyTest.ip !== "localhost") {
      if (usedProxies.has(proxyTest.ip)) {
        console.log(`\n⚠️ 存在相同代理IP（${proxyTest.ip}），请立即检查！`);
        process.exit(1);
      }
      usedProxies.add(proxyTest.ip);
    }
  } else {
    console.log(
      `账号[${accountConfig.index}]${
        accountConfig.remark ? "（" + accountConfig.remark + "）" : ""
      } 未配置代理，走直连`
    );
  }

  console.log(
    `账号[${accountConfig.index}]${
      accountConfig.remark ? "（" + accountConfig.remark + "）" : ""
    } 🔍 获取账号信息中...`
  );
  let initialAccountInfo = await getAccountBasicInfo(
    accountConfig.cookie,
    accountConfig.proxyUrl,
    accountConfig.index
  );
  let nickname = initialAccountInfo?.nickname || "账号" + accountConfig.index;

  if (initialAccountInfo) {
    const totalCoin =
      initialAccountInfo.totalCoin != null
        ? initialAccountInfo.totalCoin
        : "未知";
    const allCash =
      initialAccountInfo.allCash != null ? initialAccountInfo.allCash : "未知";
    console.log(
      `账号[${nickname}] ✅ 登录成功，💰 当前金币: ${totalCoin}，💸 当前余额: ${allCash}`
    );
  } else {
    console.log(`账号[${nickname}] ❌ 基本信息获取失败，继续执行`);
  }

  const adTask = new KuaishouAdTask({
    ...accountConfig,
    nickname: nickname,
    tasksToExecute: tasksToExecute,
  });

  await adTask.checkCoinLimit();
  if (adTask.coinExceeded) {
    console.log(
      `账号[${adTask.nickname}]${
        accountConfig.remark ? "（" + accountConfig.remark + "）" : ""
      } 初始金币已超过阈值，不执行任务`
    );

    const finalAccountInfo = await getAccountBasicInfo(
      accountConfig.cookie,
      accountConfig.proxyUrl,
      accountConfig.index
    );
    const initialCoin = initialAccountInfo?.totalCoin || 0;
    const finalCoin = finalAccountInfo?.totalCoin || 0;
    const coinChange = finalCoin - initialCoin;
    const initialCash = initialAccountInfo?.allCash || 0;
    const finalCash = finalAccountInfo?.allCash || 0;
    const cashChange = finalCash - initialCash;

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
      coinLimitExceeded: true,
    };
  }

  for (let round = 0; round < KSROUNDS; round++) {
    const waitTime = Math.floor(Math.random() * 8000) + 8000;
    console.log(
      `账号[${adTask.nickname}]${
        accountConfig.remark ? "（" + accountConfig.remark + "）" : ""
      } ⌛ 第${round + 1}轮，先随机等待 ${Math.round(waitTime / 1000)} 秒`
    );
    //await new Promise((resolve) => setTimeout(resolve, waitTime));

    console.log(
      `账号[${adTask.nickname}]${
        accountConfig.remark ? "（" + accountConfig.remark + "）" : ""
      } 🚀 开始第${round + 1}轮任务`
    );
    const roundResults = await adTask.executeAllTasksByPriority();

    if (Object.values(roundResults).some(Boolean)) {
      console.log(
        `账号[${adTask.nickname}]${
          accountConfig.remark ? "（" + accountConfig.remark + "）" : ""
        } ✅ 第${round + 1}轮执行完成`
      );
    } else {
      console.log(
        `账号[${adTask.nickname}]${
          accountConfig.remark ? "（" + accountConfig.remark + "）" : ""
        } ⚠️ 第${round + 1}轮没有成功任务`
      );
    }

    if (adTask.stopAllTasks) {
      console.log(
        `账号[${adTask.nickname}]${
          accountConfig.remark ? "（" + accountConfig.remark + "）" : ""
        } 🏁 达到停止条件，终止后续轮次`
      );
      break;
    }

    if (round < KSROUNDS - 1) {
      const nextWaitTime = Math.floor(Math.random() * 10000) + 10000;
      console.log(
        `账号[${adTask.nickname}]${
          accountConfig.remark ? "（" + accountConfig.remark + "）" : ""
        } ⌛ 等待 ${Math.round(nextWaitTime / 1000)} 秒进入下一轮`
      );
      await new Promise((resolve) => setTimeout(resolve, nextWaitTime));
    }
  }

  const finalAccountInfo = await getAccountBasicInfo(
    accountConfig.cookie,
    accountConfig.proxyUrl,
    accountConfig.index
  );
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

function printAccountsSummary(accountResults) {
  if (!accountResults.length) {
    console.log("\n没有可显示的账号信息。");
    return;
  }

  const totalInitialCoin = accountResults.reduce((sum, account) => {
    return sum + (parseInt(account.initialCoin) || 0);
  }, 0);

  const totalFinalCoin = accountResults.reduce((sum, account) => {
    return sum + (parseInt(account.finalCoin) || 0);
  }, 0);

  const totalCoinChange = totalFinalCoin - totalInitialCoin;

  const totalInitialCash = accountResults.reduce((sum, account) => {
    return sum + (parseFloat(account.initialCash) || 0);
  }, 0);

  const totalFinalCash = accountResults.reduce((sum, account) => {
    return sum + (parseFloat(account.finalCash) || 0);
  }, 0);

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

  const successRate =
    totalTasks > 0
      ? ((totalSuccessTasks / totalTasks) * 100).toFixed(1)
      : "0.0";
  const coinLimitExceededCount = accountResults.filter(
    (account) => account.coinLimitExceeded
  ).length;

  console.log("\n\n" + "=".repeat(80));
  console.log(
    "|" + centerAlign("      快手养号任务执行结果汇总表      ", 78) + "|"
  );
  console.log("=".repeat(80));
  console.log(
    "|" +
      ("总账号数: " + accountResults.length).padEnd(22) +
      ("超过金币阈值账号: " + coinLimitExceededCount).padEnd(22) +
      ("总任务数: " + totalTasks).padEnd(22) +
      ("任务成功率: " + successRate + "%").padEnd(10) +
      "|"
  );
  console.log(
    "|" +
      ("总金币变化: " + totalCoinChange).padEnd(26) +
      ("总金币奖励: " + totalReward).padEnd(26) +
      ("总余额变化: " + totalCashChange.toFixed(2)).padEnd(24) +
      "|"
  );
  console.log("-".repeat(80));

  const headers = [
    "序号",
    "备注",
    "账号昵称",
    "初始金币",
    "最终金币",
    "金币变化",
    "初始余额",
    "最终余额",
    "余额变化",
  ];
  const widths = [6, 16, 16, 12, 12, 12, 12, 12, 12];

  let headerRow = "|";
  headers.forEach((header, index) => {
    headerRow += centerAlign(header, widths[index]) + "|";
  });
  console.log(headerRow);

  let separatorRow = "|";
  widths.forEach((width) => {
    separatorRow += "-".repeat(width) + "|";
  });
  console.log(separatorRow);

  accountResults.forEach((account) => {
    let dataRow = "|";
    dataRow += centerAlign(account.index, widths[0]) + "|";
    dataRow += centerAlign(account.remark, widths[1]) + "|";

    const nicknameWithWarning =
      (account.nickname || "-") + (account.coinLimitExceeded ? " ⚠️" : "");
    dataRow +=
      centerAlign(nicknameWithWarning.substring(0, widths[2] - 2), widths[2]) +
      "|";
    dataRow += centerAlign(account.initialCoin, widths[3]) + "|";
    dataRow += centerAlign(account.finalCoin, widths[4]) + "|";

    const coinChangeStr =
      account.coinChange >= 0 ? "+" + account.coinChange : account.coinChange;
    dataRow += centerAlign(coinChangeStr, widths[5]) + "|";
    dataRow += centerAlign(account.initialCash, widths[6]) + "|";
    dataRow += centerAlign(account.finalCash, widths[7]) + "|";

    const cashChangeStr =
      account.cashChange >= 0
        ? "+" + account.cashChange.toFixed(2)
        : account.cashChange.toFixed(2);
    dataRow += centerAlign(cashChangeStr, widths[8]) + "|";

    console.log(dataRow);
  });

  console.log("=".repeat(80));
  console.log(
    "|" + centerAlign("      任务执行完成，请查看详细结果      ", 78) + "|"
  );
  console.log("=".repeat(80));
}

(async () => {
  const accounts = loadAccountsFromEnv();
  console.log(`共找到 ${accounts.length} 个有效账号`);

  if (!accounts.length) {
    process.exit(1);
  }

  const maxConcurrency = getEnvNumber("MAX_CONCURRENCY", 888);

  console.log(`\n防黑并发：${maxConcurrency}    防黑轮数：${KSROUNDS}\n`);

  const results = [];

  await concurrentExecute(accounts, maxConcurrency, async (account) => {
    console.log(
      `\n—— 🚀 开始账号[${account.index}]${
        account.remark ? "（" + account.remark + "）" : ""
      } ——`
    );

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
      console.log(
        `账号[${account.index}]${
          account.remark ? "（" + account.remark + "）" : ""
        } ❌ 执行异常：${error.message}`
      );
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

  console.log("\n全部完成。", "✅");
  console.log(
    "\n---------------------------------------------- 账号信息汇总 ----------------------------------------------"
  );

  printAccountsSummary(results);
})();
