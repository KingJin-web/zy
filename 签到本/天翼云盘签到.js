/**
 * 变量名：CLOUD_189
 * 值：手机号#密码，多账号，直接换行或者重新弄一个变量，格式一样。 
 *  需要安装的依赖 cloud189-sdk
 * 定时规则
 * 每天早上8点，跟晚上8点签到。
 * cron: 0 0 8,20 * * *
 */
const { CloudClient } = require("cloud189-sdk");
const fs = require('fs'); // 引入文件系统模块，用于写入日志

const mask = (s, start, end) => s.split("").fill("*", start, end).join("");

const buildTaskResult = (res, result) => {
  const index = result.length;
  if (res.errorCode === "User_Not_Chance") {
    result.push(`第${index}次抽奖失败,次数不足`);
  } else {
    result.push(`第${index}次抽奖成功,抽奖获得${res.prizeName}`);
  }
};

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const message = [];
// 任务 1.签到 2.天天抽红包 3.自动备份抽红包
const doTask = async (cloudClient) => {
  const result = [];
  const res1 = await cloudClient.userSign();
  result.push(
    `${res1.isSign? "已经签到过了，" : ""}签到获得${res1.netdiskBonus}M空间`
  );
  await delay(5000); // 延迟5秒

  const res2 = await cloudClient.taskSign();
  buildTaskResult(res2, result);

  await delay(5000); // 延迟5秒
  const res3 = await cloudClient.taskPhoto();
  buildTaskResult(res3, result);

  await delay(5000); // 延迟5秒
  const res4 = await cloudClient.taskKJ();
  buildTaskResult(res4, result);
  return result;
};

const doFamilyTask = async (cloudClient) => {
  const { familyInfoResp } = await cloudClient.getFamilyList();
  const result = [];
  if (familyInfoResp) {
    for (let index = 0; index < familyInfoResp.length; index += 1) {
      const { familyId } = familyInfoResp[index];
      const res = await cloudClient.familyUserSign(familyId);
      result.push(
        "家庭任务" +
          `${res.signStatus? "已经签到过了，" : ""}签到获得${
            res.bonusSpace
          }M空间`
      );
    }
  }
  return result;
};

// 开始执行程序
async function main(userName, password) {
  if (userName && password) {
    const userNameInfo = mask(userName, 3, 7);
    try {
      message.push(`账户 ${userNameInfo}开始执行`);
      console.log(`账户 ${userNameInfo}开始执行`);
      const cloudClient = new CloudClient(userName, password);
      await cloudClient.login();
      const result = await doTask(cloudClient);
      result.forEach((r) => console.log(r));
      const familyResult = await doFamilyTask(cloudClient);
      familyResult.forEach((r) => console.log(r));

      console.log("任务执行完毕");
      const { cloudCapacityInfo, familyCapacityInfo } =
        await cloudClient.getUserSizeInfo();
      let txt =
        `个人：${(
          cloudCapacityInfo.totalSize /
          1024 /
          1024 /
          1024
        ).toFixed(2)}G,家庭：${(
          familyCapacityInfo.totalSize /
          1024 /
          1024 /
          1024
        ).toFixed(2)}G`;

      message.push(txt);
      console.log(txt);
    } catch (e) {
      console.error(e);
      if (e.code === "ECONNRESET") {
        throw e;
      }
    } finally {
      message.push(`账户 ${userNameInfo}执行完毕`);
    }
  }
}

(async () => {
  try {
    const c189s = process.env.CLOUD_189;
if (!c189s) {
  console.log('未获取到天翼云盘 CLOUD_189');
  return;
}
let account = c189s.split('\n');



    for (const c189 of account) {
      let date = c189.split('#');
      await main(date[0], date[1]);
    }
  } finally {
    console.log(message.join('\n'));
    // 将消息内容写入日志文件
    const logContent = message.join('\n');
    fs.writeFileSync('天翼云盘签到日志.txt', logContent);
  }
})();
