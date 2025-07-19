/**
 * create: 2025/07/11
 * author: 问情，Q群：960690899
 * description: 应用商店下载富豪免费剧场，抓包Hearders的token值，签到、新手红包、新手看15分钟没写，需要自行添加
 * test: 青龙2.19.2
 * 环境变量：wqwl_fhdj，多个换行或者新建多个
 * 免责声明：本脚本仅用于学习，请勿用于商业用途，否则后果自负，请在下载24小时之内删除，否则请自行承担。有问题自行解决。
 * 注：本脚本大多数代码均为ai写。
 */

const axios = require('axios');

const crypto = require("crypto")
let index = 0;
const BASE_URL = 'https://app.whhxtc.ltd'

class Task {
    constructor(cookie) {
        this.index = index++;
        this.cookie = cookie;
        this.init()

    }
    init() {
        this.iTag = this.randomITag(Date.now());
        this.headers = {
            'User-Agent': 'okhttp/4.9.0',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/x-www-form-urlencoded',
            'iTag': this.iTag,
            'path': '',
            'checksum': '',
            'Sign': '',
            'source': 'Android',
            'X-SCDN-Req-Token': '',
            'Timestamp': '',
            'version': '1.1.3',
            'seqID': '',
            'token': this.cookie
        }
    }
    randomITag(j) {
        const randomDigits = new Set();
        while (randomDigits.size < 4) {
            const digit = Math.floor(Math.random() * 10); // 0 ~ 9
            randomDigits.add(digit);
        }
        const digitsStr = [...randomDigits].join('');
        const result = j.toString() + digitsStr;
        return result;
    }
    getXSCDNReqToken(timestamp, path, random) {
        random = random || this.randomString();
        const sign = crypto.createHash('md5').update(`${timestamp}${random}7a21c2347f14aecea9f42846fcb83a04${path}`).digest('hex');
        //  console.log(`${timestamp}|${random}|${sign}}`);
        return `${timestamp}|${random}|${sign}`
    }
    getSign(j) {
        const valueOf = (BigInt(j) * BigInt(3)).toString();
        let stringBuilder = [];
        for (let i = 0; i < valueOf.length; i++) {
            if (i % 2 !== 0) {
                stringBuilder.push(valueOf[i]);
            }
        }
        stringBuilder.push(valueOf.slice(-3));
        return stringBuilder.join('').split('').reverse().join('');
    }
    getChecksum(timeStamp, params) {
        //console.log(timeStamp, params);
        const checksum = crypto.createHash('md5').update(`${timeStamp}${params}NS2pzOy3x5iXkW96zd73dfXdG7DM9vb86esS7Kws`).digest('hex');
        //console.log(checksum);
        return checksum;
    }

    getParams(data) {
        const sortedKeys = Object.keys(data).sort();
        const result = sortedKeys.map(key => data[key]).join('');
        return result;
    }
    randomString(length = 12) {
        const characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
        let result = '';
        const charactersLength = characters.length;
        for (let i = 0; i < length; i++) {
            result += characters.charAt(Math.floor(Math.random() * charactersLength));
        }
        return result;
    }

    //添加观看时间
    async play(times = 30, path = '/yk/drama/play') {
        const url = `${BASE_URL}${path}`
        const data = {
            "episodeId": this.getRandomInt(1000, 5000),
            "second": this.randomTime(times),
            "path": path,
            "equipment": "android"
        }
        this.headers['path'] = path
        const randomShare = this.getRandomInt(0, 29)
        const randomFavorite = this.getRandomInt(0, 29)
        const likesIndex = this.randomLikesIndex()
        let j = 0
        for (let i = 0; i < 30; i++) {
            try {
                if (i % 3 === 0)
                    data['episodeId'] += 1
                if (i === randomShare) {
                    const shareData = await this.share()
                    this.sendMessage(`🔔分享结果：${JSON.stringify(shareData)}`)
                }
                if (i === randomFavorite) {
                    const favoriteData = await this.favorite()
                    this.sendMessage(`🔔收藏结果：${JSON.stringify(favoriteData)}`)
                }
                const timestamp = Date.now()
                const timestamp2 = Math.floor(timestamp / 1000)
                this.headers['X-SCDN-Req-Token'] = this.getXSCDNReqToken(timestamp2, url)
                this.headers['checksum'] = this.getChecksum(timestamp, this.getParams(data));
                this.headers['Timestamp'] = timestamp
                this.headers['seqID'] = timestamp
                this.headers['Sign'] = this.getSign(timestamp)
                const config = {
                    url: url,
                    method: 'POST',
                    headers: this.headers,
                    data: data
                }
                const res = await axios(config)
                this.sendMessage(`📺第${i + 1}次模拟观看结果：${JSON.stringify(res.data)}`)
                if (likesIndex.includes(i)) {
                    const likesResult = await this.likes(data['episodeId'])
                    this.sendMessage(`💖第${(j++) + 1}次视频点赞结果：${JSON.stringify(likesResult)}`)
                    data['episodeId'] += 1
                }
                const playSleep = this.getRandomInt(4, 16)
                await this.sleep(playSleep * 1000)
            } catch (error) {
                this.sendMessage(`第${i + 1}次模拟观看出错：${error}`)
                return
            }

        }
    }

    randomLikesIndex() {
        let data = []
        while (data.length < 3) {
            const temp = this.getRandomInt(0, 29)
            if (!data.includes(temp))
                data.push(temp)
        }
        return data
    }
    //点赞
    async likes(episodeId, path = '/yk/drama/likes') {
        try {
            const url = `${BASE_URL}${path}`
            episodeId = episodeId || this.getRandomInt(1000, 5000)
            const data = {
                "episodeId": episodeId,
                "path": path,
                "equipment": "android"
            }
            this.headers['path'] = path
            const timestamp = Date.now()
            const timestamp2 = Math.floor(timestamp / 1000)
            this.headers['X-SCDN-Req-Token'] = this.getXSCDNReqToken(timestamp2, url)
            this.headers['checksum'] = this.getChecksum(timestamp, this.getParams(data));
            this.headers['Timestamp'] = timestamp
            this.headers['seqID'] = timestamp
            this.headers['Sign'] = this.getSign(timestamp)
            const config = {
                url: url,
                method: 'POST',
                headers: this.headers,
                data: data
            }
            const res = await axios(config)
            return res.data
        } catch (e) {
            throw `点赞出错了,${e}`
        }
    }

    //分享
    async share(path = '/yk/task/share') {
        try {
            const url = `${BASE_URL}${path}`
            const data = {
                "path": path,
                "equipment": "android"
            }
            this.headers['path'] = path
            const timestamp = Date.now()
            const timestamp2 = Math.floor(timestamp / 1000)
            this.headers['X-SCDN-Req-Token'] = this.getXSCDNReqToken(timestamp2, url)
            this.headers['checksum'] = this.getChecksum(timestamp, this.getParams(data));
            this.headers['Timestamp'] = timestamp
            this.headers['seqID'] = timestamp
            this.headers['Sign'] = this.getSign(timestamp)
            const config = {
                url: url,
                method: 'POST',
                headers: this.headers,
                data: data
            }
            const res = await axios(config)
            return res.data
        } catch (e) {
            throw `分享出错了,${e}`
        }
    }

    //收藏
    async favorite(episodeId, path = '/yk/drama/favorite') {
        try {
            const url = `${BASE_URL}${path}`
            episodeId = episodeId || this.getRandomInt(1000, 5000)
            const data = {
                "episodeId": episodeId,
                "path": path,
                "equipment": "android"
            }
            this.headers['path'] = path
            const timestamp = Date.now()
            const timestamp2 = Math.floor(timestamp / 1000)
            this.headers['X-SCDN-Req-Token'] = this.getXSCDNReqToken(timestamp2, url)
            this.headers['checksum'] = this.getChecksum(timestamp, this.getParams(data));
            this.headers['Timestamp'] = timestamp
            this.headers['seqID'] = timestamp
            this.headers['Sign'] = this.getSign(timestamp)
            const config = {
                url: url,
                method: 'POST',
                headers: this.headers,
                data: data
            }
            const res = await axios(config)
            return res.data
        } catch (e) {
            throw `点赞出错了,${e}`
        }
    }

    //饭补0.30-8.30 ，11.30-12.30,17.30-18.30，22.30-23.30
    async diningCheckIn(path = '/yk/task/diningCheckIn') {
        try {
            const url = `${BASE_URL}${path}`
            const data = {
                "path": path,
                "equipment": "android"
            }
            this.headers['path'] = path
            const timestamp = Date.now()
            const timestamp2 = Math.floor(timestamp / 1000)
            this.headers['X-SCDN-Req-Token'] = this.getXSCDNReqToken(timestamp2, url)
            this.headers['checksum'] = this.getChecksum(timestamp, this.getParams(data));
            this.headers['Timestamp'] = timestamp
            this.headers['seqID'] = timestamp
            this.headers['Sign'] = this.getSign(timestamp)
            const config = {
                url: url,
                method: 'POST',
                headers: this.headers,
                data: data
            }
            const res = await axios(config)
            this.sendMessage(`🍚饭补领取结果：${JSON.stringify(res.data)}`)
        } catch (e) {
            throw `获取饭补出错了,${e}`
        }
    }

    async query() {
        try {
            const data1 = await this.accountBalance(7)
            const data2 = await this.accountBalance(8)
            if (data1 && data2) {
                let result = ''
                result += `🪙${data1.data.name}：${data1.data.quantity}`
                result += `\n🪙${data2.data.name}：${data2.data.quantity}`
                this.sendMessage(`查询结果：\n ${result}`)
            } else {
                this.sendMessage(`🪙$查询结果：\n 获取数据失败`)
            }
        } catch (e) {
            throw `查询账号出错了,${e}`
        }
    }

    async accountBalance(accountType = "7", path = '/yk/user/accountBalance') {
        try {
            const url = `${BASE_URL}${path}`
            const data = {
                "accountType": accountType,
                "path": "/user/accountBalance",
                "equipment": "android"
            }
            this.headers['path'] = path
            const timestamp = Date.now()
            const timestamp2 = Math.floor(timestamp / 1000)
            this.headers['X-SCDN-Req-Token'] = this.getXSCDNReqToken(timestamp2, url)
            this.headers['checksum'] = this.getChecksum(timestamp, this.getParams(data));
            this.headers['Timestamp'] = timestamp
            this.headers['seqID'] = timestamp
            this.headers['Sign'] = this.getSign(timestamp)
            const config = {
                url: url,
                method: 'POST',
                headers: this.headers,
                data: data
            }
            const res = await axios(config)
            return res.data
        } catch (e) {
            throw `获取余额出错了,${e}`
        }
    }


    randomTime(time = 30) {
        return this.getRandomInt(time - 5, time + 5)
    }

    async main() {
        await this.play()
        if (this.isInMealTime() == true)
            await this.diningCheckIn()
        await this.query()
    }

    isInMealTime() {
        const now = new Date();

        const currentHour = now.getHours();
        const currentMinute = now.getMinutes();
        const currentTime = currentHour * 60 + currentMinute;
        const mealTimes = [
            { start: 7 * 60 + 30, end: 8 * 60 + 30 },   // 07:30 - 08:30
            { start: 11 * 60 + 30, end: 12 * 60 + 30 }, // 11:30 - 12:30
            { start: 17 * 60 + 30, end: 18 * 60 + 30 }, // 17:30 - 18:30
            { start: 22 * 60 + 30, end: 23 * 60 + 30 }  // 22:30 - 23:30
        ];

        return mealTimes.some(time => {
            return currentTime >= time.start && currentTime <= time.end;
        });
    }
    async sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    getRandomInt(min, max) {
        if (min > max) throw new Error("min 不能大于 max");
        min = Math.ceil(min);
        max = Math.floor(max);
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    sendMessage(message) {
        console.log(`账号[${this.index + 1}] ${message}`);
    }
}

//获取环境变量
function checkEnv(userCookie) {
    try {
        const envSplitor = ["&", "\n"];
        //console.log(userCookie);
        let userList = userCookie
            .split(envSplitor.find((o) => userCookie.includes(o)) || "&")
            .filter((n) => n);
        if (!userList || userList.length === 0) {
            console.log("没配置环境变量就要跑脚本啊！！！");
            console.log("🔔还没开始已经结束!");
            process.exit(1);
        }

        console.log(`共找到${userList.length}个账号`);
        return userList;
    } catch (e) {
        console.log("环境变量格式错误,下面是报错信息")
        console.log(e);
    }
}


!(async function () {
    console.log("富豪短剧开始运行");
    const tokens = checkEnv(process.env['wqwl_fhdj']);
    const tasks = tokens.map(token => new Task(token).main());
    await Promise.all(tasks); // 所有任务并发执行
    console.log("全部任务已完成！");
})(); 