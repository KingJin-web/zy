# ruishucookie.py
import os
import execjs
import httpx
httpx._config.DEFAULT_CIPHERS += ":ALL:@SECLEVEL=1"



filename = 'Cache.js'
if os.path.exists(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        fileContent = file.read()
else:
    fileContent = ''

def initCookie(getUrl='https://wapact.189.cn:9001/gateway/standQuery/detailNew/exchange'):
    global js_code_ym, fileContent
    cookie = ''
    response = httpx.post(getUrl)
    content = response.text.split(' content="')[2].split('" r=')[0]
    code1 = response.text.split('$_ts=window')[1].split('</script><script type="text/javascript"')[0]
    code1Content = '$_ts=window' + code1
    Url = response.text.split('$_ts.lcd();</script><script type="text/javascript" charset="utf-8" src="')[1].split('" r=')[0]
    urls = getUrl.split('/')
    rsurl = urls[0] + '//' + urls[2] + Url
    filename = 'Cache.js'
    if fileContent == '':
        if not os.path.exists(filename):
            fileRes = httpx.get(rsurl)
            fileContent = fileRes.text
            if fileRes.status_code == 200:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(fileRes.text)
            else:
                print(f"Failed to download {rsurl}. Status code: {fileRes.status_code}")
    if response.headers['Set-Cookie']:
        cookie = response.headers['Set-Cookie'].split(';')[0].split('=')[1]
    runJs = js_code_ym.replace('content_code', content).replace("'ts_code'", code1Content + fileContent)
    execjsRun = RefererCookie(runJs)
    
    # 将 cookies 转换为字符串格式
    cookies_str = f"yiUIIlbdQT3fO={cookie}; yiUIIlbdQT3fP={execjsRun.call('main').split('=')[1]}"
    return cookies_str

def RefererCookie(runJs):
    try:
        execjsRun = execjs.compile(runJs)
        return execjsRun
    except execjs._exceptions.CompileError as e:
        print(f"JavaScript 编译错误: {e}")
    except execjs._exceptions.RuntimeError as e:
        print(f"JavaScript 运行时错误: {e}")
    except Exception as e:
        print(f"其他错误: {e}")

js_code_ym = '''delete __filename
delete __dirname
ActiveXObject = undefined

window = global;

content="content_code"

navigator = {"platform": "Linux aarch64"}
navigator = {"userAgent": "CtClient;11.0.0;Android;13;22081212C;NTIyMTcw!#!MTUzNzY"}

location={
    "href": "https://",
    "origin": "",
    "protocol": "",
    "host": "",
    "hostname": "",
    "port": "",
    "pathname": "",
    "search": "",
    "hash": ""
}

i = {length: 0}
base = {length: 0}
div = {
    getElementsByTagName: function (res) {
        console.log('div中的getElementsByTagName：', res)
        if (res === 'i') {
            return i
        }
    return '<div></div>'

    }
}

script = {

}
meta = [
    {charset:"UTF-8"},
    {
        content: content,
        getAttribute: function (res) {
            console.log('meta中的getAttribute：', res)
            if (res === 'r') {
                return 'm'
            }
        },
        parentNode: {
            removeChild: function (res) {
                console.log('meta中的removeChild：', res)
                
              return content
            }
        },
        
    }
]
form = '<form></form>'

window.addEventListener= function (res) {
        console.log('window中的addEventListener:', res)
        
    }
    
document = {
    createElement: function (res) {
        console.log('document中的createElement：', res)
        
       if (res === 'div') {
            return div
        } else if (res === 'form') {
            return form
        }
        else{return res}
            
        


    },
    addEventListener: function (res) {
        console.log('document中的addEventListener:', res)
        
    },
    appendChild: function (res) {
        console.log('document中的appendChild：', res)
        return res
    },
    removeChild: function (res) {
        console.log('document中的removeChild：', res)
    },
    getElementsByTagName: function (res) {
        console.log('document中的getElementsByTagName：', res)
        if (res === 'script') {
            return script
        }
        if (res === 'meta') {
            return meta
        }
        if (res === 'base') {
            return base
        }
    },
    getElementById: function (res) {
        console.log('document中的getElementById：', res)
        if (res === 'root-hammerhead-shadow-ui') {
            return null
        }
    }

}

setInterval = function () {}
setTimeout = function () {}
window.top = window

'ts_code'

function main() {
    cookie = document.cookie.split(';')[0]
    return cookie
}'''

async def main(timeValue):
    global runTime, js_codeRead
    tasks = []
    
    init_result = initCookie()
    if init_result:
        cookie = init_result['cookie']
        execjsRun = init_result['execjsRun']
    else:
        print("初始化 cookies 失败")
        return
    
    runcookie = {
        'cookie': cookie,
        'execjsRun': execjsRun
    }
    
    # 添加输出 cookies 的代码
    cookies = {
        'yiUIIlbdQT3fO': runcookie['cookie'],
        'yiUIIlbdQT3fP': runcookie['execjsRun'].call('main').split('=')[1]
    }
    print(f"Cookies: {cookies}")

if __name__ == "__main__":
    asyncio.run(main(0))