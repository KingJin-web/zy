#   --------------------------------注释区--------------------------------
#   警告！！请确认此时无阅读本在执行,否则会造成数据相互污染！由此造成的不良结果概不负责
#   警告！！请确保脚本运行结束,切勿中途自行结束！由此造成的不良结果概不负责
#   公众号取关脚本
#
#   需抓取数据: 
#   * 填写自动过检的api接口 本地 内网ip:5000 非本地自行进行穿透 变量名:yuanshen_api
#   * 登录多少个账号就跑多少个账号
#   * 此本提供白名单+黑名单功能 只能使用一个名单
#   * 白名单: 设置要跑的Wxid到环境变量 huaji_gzhqg_whitelist  多号#分割
#   * 黑名单: 设置要不跑的Wxid到环境变量 huaji_gzhqg_blacklist  多号#分割
#   * 注意两名单只能设置一个 同时设置优先读取白名单 当然你可以都不设置这样什么号都会跑
#
# 下面是自定义变量设置(注意是修改对应的环境变量而不是改文件内容):
# huaji_gzhqg_day   默认16 取关关注时间大于x天的公众号,x为此变量值,推荐默认,否则可能会封禁任务
#   --------------------------------一般不动区--------------------------------
#                     _ooOoo_
#                    o8888888o
#                    88" . "88
#                    (| -_- |)
#                     O\ = /O
#                 ____/`---'\____
#               .   ' \\| |// `.
#                / \\||| : |||// \
#              / _||||| -:- |||||- \
#                | | \\\ - /// | |
#              | \_| ''\---/'' | |
#               \ .-\__ `-` ___/-. /
#            ___`. .' /--.--\ `. . __
#         ."" '< `.___\_<|>_/___.' >'"".
#        | | : `- \`.;`\ _ /`;.`/ - ` : | |
#          \ \ `-. \_ __\ /__ _/ .-` / /
#  ======`-.____`-.___\_____/___.-`____.-'======
#                     `=---='
# 
#  .............................................
#           佛祖保佑             永无BUG
#           佛祖镇楼             BUG辟邪
#佛曰:  
#        写字楼里写字间，写字间里程序员；  
#        程序人员写程序，又拿程序换酒钱。  
#        酒醒只在网上坐，酒醉还来网下眠；  
#        酒醉酒醒日复日，网上网下年复年。  
#        但愿老死电脑间，不愿鞠躬老板前；  
#        奔驰宝马贵者趣，公交自行程序员。  
#        别人笑我忒疯癫，我笑自己命太贱；  
#        不见满街漂亮妹，哪个归得程序员？
#
#   --------------------------------代码区--------------------------------
'''
Create at [2025-05-08 16:39:41]
'''
import requests
import os
import sys
import platform
import subprocess
import importlib
import datetime
from urllib.parse import urlparse
import logging
import socket
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] ===> %(message)s')
log = logging.getLogger(__name__)

THIS_Proxies = 'https://github.huaji.asia/'   # 网络不行就填Github代理 这里只给出一个要是不行就自己找 https://github.huaji.asia/

data = 'g0UwsE3ZeCCKBlLLzvl+z1vtE0zGwKhukNYvdaGeZo9oh8FKsaCCsTog6fJifX9tYOKLy8wcvk+rUv5H80n84OvLFEWM0bzVIXEvOiZ24rLitrzFggdEMoRIBLli4j4ZYvkW0eacIlaP6QiEJ+GsCSI2p91BxvzD5Fy/h9+FMY4vciRRcrGXPcQB2CjFq7zxyx5z9jkHudIMRGfQ5QgucTl2yvtP59DZorklI9lngpH5CyTjSga05BFauigkzN3We9zuFbzAOTQlRISJnuoUKhhwSxwKwRG82cZk9kd75RWGrYvMkeqUw3kXxVWmKgIMbPtv1+tIeY/cs7nSaLEqZ2L4+MrFVg5h0bGlHKO2nxZcLnS9ZbzYPNY2F/QpgDe7m5pRL8hq5bAzDmFMzb1bin1xgIUbtPlZRnoqZZwS8G8KwEvrJEUFN8SYxHGYMNXZXBcUrHF8A/ccrHIUkUTiePzCgwRBQV+ZutoQJBeaJ/vWT8qtTI0yvQkuANfd67oozldJmV5UEu3QymYHUF0H9fzO2y2WLeQubDZbi+CNXMx5np4Oxmt3VeXQdTmxmNBq6wV14xHU4K6x9MixkPCwBbpvNTrqxOsvHaLjxGQfwdhFymMdOhI3Np3kKR8X3vrFJudajuTT7TLzkPaRaixfSefewkxF4w0fQADyLLhh09m2BJLxXD4EnucrsuXL1Kbq5m9/Yd9GNbUMQOE1SGdB8DXenDyWFt//E+Ghb3jEaxPU8fRDyu9WcgRvmY2cEECU42UUPfNQhaiHLp9TfklbD+qFZgztuTly8jKXaombmjHybUCRyX318ICyA1klGdS71ZNoVg3W+ci7jWrkmTmqn43kq5aY9nLte77biqeA2rURhG1ojpL/pXXLS9FxpNt2s8y7VdQUZACfq3XpzYexLyQeSuWTd7e++UWszTcDEDGIywCKVN9D1DVfS1w+HnmR4HeA1ZnJbwfRnBS7NI7WYHIqogz9ieYd1isyOiEw1yi3Sx1QFkc1ECjWv4jIIvOBZIkU8j7MYoJJJVv3H5rEdN+adst9eJEWS5DfXs3d+xF7SHypItIEFzFpxulYuQjOswUgY0V1rTSnGNCooT/USe3H5+DZN3cig7JmbvzpFOFZ21pW+K9CrST9K7pbNli2uQwQMEOtBMpD+p3qvwOr9SlCwfpFdAJhNVmMCCpkKddx5gC8xUqSA2TleuqgJAltog/ElbjyDvKAquPjdl+h2d4qXBQlo0TLsb/DxKpHfg4845zWIiCrdapWWMrm80y2wb/lvU4gsnGWQ07Xcg1+zAelwY6Gui3MrbCUhkcklK4sHRXl+Q1eroFzX/yXN0Ne/ln89y7IaZFg8IAQwPSlwZQjiEvI3Zp1ldprfBPGDUG+9LoD7FXv7fE39LK+yYrDcWqlSEQ/RKvtxqmPLyytlbhjz7XzwpvX9VGi+XCv6qhiyuO1lCY9sXI1Hg+FnK/+LCb3S9y3NrTIiW2JnLHsv81q772axp9Kc9SB8PfrJ7DM7aZ/hEwyXemb0pYp8T1Da4tKzWrjMvW0eO8YVA3udscs/to9AvRAhMmR72Qifd8Po51ow0D7N5bXPw69ZykYKquj9qrIonnKTijQfVGTZCRNXqSrxuSgF0Rv28EGay1FRaeRhr2Nb93bOFer3SPBIEVVY5PxgCzwo/67yGvlJ+N5du1qy2wiWtJ+YYCeonhttb12u+L8oARE9Xfaf3SBzaqU61NSCoYSiHi3dZx4d43iCZnDZgEpI+uZKBMbZl7xSksydW2QuLh3lyuukBIJWmmts1v9vxSYnvk55T1cNEuoEotf8deCeYrhKfx4jq7zg4KjVRa1YMWq+mMJFQJGtDPK3slJw6e6EXo5fSXwpHi/yOmMuo9/RAGrTlqY307JGu9APt5KR9edUpOYbSp0QIIu1kzy5MZo4eotJ+SD2uKdUzfLwaGXjeA5bCAW9YWxB3GEgV2Vz+doN8OeS8U2qf27z6hnOUXqfoPK16nCvq3RziVROD8a7u2zijOhhDDRjrJ3wxmTxerB00RH6LcCUGj20jTOf6J4UBwAkwfN6OZgclMaO95pp65HTkLvpALwAC8tNAYT84MGRZseK64M1baQ3SaKu1YJwpl9paSBqDIz0te7m2Xnf8h1RrwHse6RiOyR2HM3O/0xh590+9zVTxJLOwKF45bbO+cEgSsjmoN/96KOBD3U4BjkkZiQ7YXSsHs+4QpyYpm2ia2Vx7edm8rvgYkljBA/NzB9heqptLDVGSMNOLwQmzxT+L9xW24kGGZs0YQlKaBTaB/W2J/1ratEXGOAl5OkOlBlrTKnUzpU+1CHShMb1gvCvh3ObR7f8XSc9rErxiW9R2Forqt7u372vaebRtYY1qiK13baX2DK8XxJAhyvNTcgnObiRBDYuviPLe95vQogfSGOVXb/S2u6TAYCKH3sXf07TIu744kLqurc3WdJJpswtEiigCCO5YtLq80LqersEoKfDPdYnIlZZRnqY2JbHurnC8IU9mBmGdGeZtchYZqbb4Y5GktPdRslc2djQf+2itRYzbPmP4Z9QrW0Y15v3tszdlieScf8Xgvbvgy/YVnKQCK8ttAUsN5zML+VJXd1CFCsm1wz+jg0pG7+Teo6wo5oHBBkrPCKh21T17A83BK+dksjdTCLmjomGXDcKNZgZAb1VVtuULjnxVTu8u3KfpOQ/Dw3jjxYXxdwgn7BGOD9xrRYiJSAixUv/RSFZ9K52cRgGXHjAkEOvT6M66vRVPIZxheco2R38zoSy+j2V14XZZyxJf14deY3+pYTVx2U6rSODw3RhXvFo14zn9Z7lDONwPeRI/6DlzyvqyOBAhZRm5zoQfvUTCPdTTJf+gV5YlV1VHuMH7ZtbQavTdT2zLlB6oAQ13e8NwdCLVSNA9zVO67TLkDGFhnlXlej+kZOCrgw/KXavfU08Oj0Nrc7muIV74mkX8v/+oEU/vs6UIvFXrBGo0w+VzRyGhuMEfmgz3W41xMBAfsNe0UT9j3Aionb4l1zZsUh2Ei2m0Muo/CpzCo17lXD+nSyZCLb7KEd75gXLs+VWVE/RoaAu1t+bG0ZqzgIujKYn51QlNKOMrB4KeBlKrSJLL8N5yM+DT6ju8lxRUDYYMo8GKp+xCsMqaZPsAaS3mlatgCaK4FljxGWaOX/BfZGaybupNhW81ALpWDb14TrJ+xHdaMuApy2cSm01sP/L3YuPxPHq61VZP4RQC+nqRdOB3uwliws5SS7SMKp3SDUK4yD75Uv9a5iXXl4YReiFUCNFmomkb7Uw10InvKzIpBChzmLNToE7MFdW0H8dTD/c/yvO5RkOuSpZNPdXmzgfxq474OcX4qmOjNUp1s5vOatgsh0AZk6LGPzHaGJ86IuHoL9MrvudmNrtnu+ZuF9UyA+XAkbQ6EKz/gWSekVIUqo2AsOPdQROftY2ZQDtwAgV7P9BYndP0ylkDe8r7BDlClY9wk/ybjNIRzlnUfFQH47DaMcIqHTiV9kddt4BFfmRCQC8TPuDBkWiTxzwhYx4bQcnT4M484QekYQkKBHoF3a70E8qjszJ1rw+rrxb8Opsq/8Io5nBRIEIv5nOAKjqMFypGH/Lhfi6MoQJgB9bDYkvEOO6Ns2ptMi8thNWw0o8h0E1kbjTnBU5Ufl+oFjTYCYQ9A1ECBTlyEwk9EH3Es5fusEUcRGDvp7BKeA5tmfrPxabjf5V+JWcn9LowcQbfThABgg4sxddFtuTF/X80nWXbXGQlwrd6errm7QViaTt7AQFD6dpUUaG0QOxPMZ8AKiTBVz2T/sdrvfw5VaTv/mHreNjTSw7P+H2ZBvPDwVDl43WREOh0X52IRuRO07h7BwriiDfqZpXB41RpUpQTvX108WurwmxOmAvYwNRAIWO00W9p8ejOLjozcsiksX32EBrcQM1sCevCTbBx9vcIAqypa2DCFlCOFoWjeujUzBIKBB6wSgTQU6VuU3iZLekmKYaiiTpQ6uTOfwwhc4CBBJH80NSqm975YxwviK+KrjS9Tknx/JwvcQAUaK47bmWAgQXH1Cv7+o+KAUsgmbJOpFmadCH+7G4y9z+w359yOXrAreWfbfNGgVsL3oqc3/gKjnEkfrD4yBh7GcZazJKrcXyQqF2/O0UKQRNLCrpLKURokldCroBTQ+UCWAfqlvLw7b1Pm5nyY2cYYXLrWRJDsLYDlys66f69skO+bRxANQGYMlfnr7zHaTfIoN9AmAQaBIlpMh6zFk6zOPWjRATUvhPb9yrqQo+CG4ehqPxESSvN1yPAviXitO51ccild/FAQPqQKUqeFgkc/XDPlO5x6JraTaCsYftBxPezQJ2Kna82ywlazJqCf3aCQ5kWoTn4/gHX50nnWl94V+8IyhcjHKuNPIhCY5ssq7QQNV+9MTuvwmljEKvXAGm/6bKxvr1ZNn+PoVCXqAURkAAqw2W0OGnmhkNmCWOLhZU7+D4C1gNXY/6LtmqOcK5+krRIWDYAy8EcRdcPNrv9Nns+b7GO1FgPkclub0YDJUix4eWr3gvVQDpjjDoIPz/B+AJIl8nzh6ZQoUl7woiZ+R+3PwkA2pnPaoh7KpfFaeO1pEs2+NfjrTZJyq/z4Oq6UhKAv7sQybMGRV+EWj03Bf2lWRyqYea/cSFryR66eBws1oBVI+oCDQ7b0G1K6UImww1Zgj3nP8k/vdriEnLoWsRsa5E1KjVvm6OCWeLwjCpsxVkNtOF6BM3FDcKOjUgGOS792Ay9/hxUvth3uFsgQVoe8qQfpowfrImCWlx5bYa8b4P02zw46Cajry+hvgpJQmml0NJ2Vt4O7tBSKWIx4IESHsqV+rcCgkex9LlnPRr53YT2J5xN3GH5RHs63matRAZU6ZL11H5Z36GwaAMhwRUDbLQIx1DBdT0CNCksIQjA5vLgK5PCMpjKQO8iI8oWXvzeyEZGDYBahajeRS5cjieF+KzpdAFYdJ4kodfCz5O49ZQpIKWyV7IfS3+WaSneDahucTMl+RmyDIMiPqKsb6AzuyiBwUOuSACKIg6Kec+a+4XRoQkGJ7ZSkEZXdkPqu8ho/M2K/KCcXNDzqiuDsFu13Meeuw+AwGwcUE+2uRw2V5ywoAHUedVUo/ZYqG2mfAXS4ysiEDhi+CjBKk8uOOT8Psdk+PrzLi1JF2K3fRhB+eSrWS2Im973hrPG2bFYSbNu/Eg32dBmkB9L6BlgjVS7koYKUG2ZekIYpeTUgNW5t8O/8dbiDe+qh3rdqSRAWfGP6Ub2uDznewQtvg36cblOgJAfCkEFG2CCG4/7Ok8MwOp650OSHuRlCu2LbptGyx6TMYhGcjwBFQgNJbUcMnViPmWcv1LKi2DATcuMHA7qFoTSpBL8AVoptiY/SL3RRCltcsF6rv2H6AP5KIrAYCgviGe6WHroJTN6w3pNbhc5fbuA2TywvTrvU4+RMMhmiBnpCz50Snj7XNoc+hIvzHQQjR4TLR5dIBZCSL00RPfTEDjdFkbxj0uFbPGjg3DvMAIOlZpqLX1smeV8WkFVUyslUTRu2yt2HCK1EAdsEk3sfsGtChqXbcNZo3PR0HqQIj1DLb/BB03hAAhyfJsKna6VCOsSg4CSGqiAN5iDh55Q3vLPsY8MImBaqmWXave1d5EwcDkEXjHrfHr9omCBwSrsyebX9PZRwzrj4wZhGcsXksI90LKNODGvlSX5vvt4vO9yV9hShxEwnoUK8I4JKS/3YcmSEy2Q8pBH2I3XqrVbC6+ex/ChRAqoCiYYEspoCkb0rdXmiseSDUOFxxFxvel3gLMag0KKXxx01sSMhn6nsNj5hheplRuUr1eOlIEV84K6KKH99D4hriBColxZB7tu2wUFaEf8PGJWuNME3s+mfy3p7itOqDXuK//usEe5nufzxz3VEBq1uiMhXm9YAvM4/akzb9Rz85nJshQRAMSZNfuzPoENlXfKJyueIjUQL9ySJO7rv6+lJmcfk1MtOY7A9pgyW52MfmHWnk3CXnHhziZQDNHikHozEsToJBTgpNRio1XWHQbmiwKaITKppAPa7EHp91YBKr9Vqz73130vwu1ZZnLHz3lRYUXNsnqMZrJkQfYNdAiRrFQLdi/S7mXqPhZ31PsfuJtqr323f13HNHvQUcB/K2Q2gJ10CZdD5vwOPtiJTlWK8Fs0/RUXcqE9Hfkcihr0z8QfX7ZK2cIGM/6tuWqvmv9zmfddIOG8aBrCX20Jzje1Dr63UvgubUmLQ+sB1uJ6gJecHMPhuNeSKXfb4FHSAUOaltctvuffnJrUav+kRcGeVVLgkqUm02M8SDKSJ2+WtdL/mU+yPJgBayc/Gvb/YBBBd3WgeRE/QUVCJjw8bK+DxGKjmlylECeVuJdsRAVkTeReFKob+BHP6T+ZvX7UvWF2HhXofR5EjsDdCGHBVJD5VJj7t8YbmAOE/LKd6jrahUJaZIGJ089ycjgTCucPA8/eBYA6037FY3uX1l1mn915SqajbYU7VA5t00dOe+SOgwQkfVtObzLFU5xctxjK9Rduu+q5pWrWX6I5LjGW7FUbaRmHDtBD4kKTgDyWwc19+WUlH+PUR4sR7Clh/CnO4DKFhRwZFt1xMwX8aXUlLENq7lOANp824QlCYCR51uaxVgz2VVsbSQR2ExoxGznFeo1+GYVY1s1wtnzVULCOdb0XUk3bSGLdosHBxoczbpC/INKRXeotQ5GkHGuzkZg+5IKRi9aVDwQbNEQH0Fqa5KQHyO1JZmRSl6VakyOZIwnASThfJhcn7Mh/pcGGGBB0mUem9Z2chSoUgs30m4aqzq8JPlsSwgkhfXBA51JMbzpVqE/h/MjnR9wEwIWfoddEDU42FoKLwrv90UmYBoeiXG9+0uncJFA80iHruTNp4h/OuBuBc4BJeW5KOAqnE2cOFdXUzYMHLLTHfUMWrr9TF87CyxcvHZdu0TMxMlp73B/NWzSByOqa/UpGtda/RvQhMtkdGyrc9qNpLebnB3tzsR2GrN9p9kNhPiU9PF1rB3XNNyfic1I7FGuL/M+A1+klqkR1yA4hIq1+tfC8gUYBmhJaWCAwoah4xVDjot2N+4yXS0+jm19EoHuup6aX0rXIOqWr2AWdxtPQLc2Q6MP05mFVohGJe3VDTntmCDYwQav5WbhLphLQPeRVtbPQsTJ7PAy3U4mH6ZqSuoRgBeHqWRGKUasVeHKpTFhK0eiVBBaXWLUIvihO7IdVHQiTI1DXxPfYwogR3aZ80BOVd8AXI7KIn77sO34rDD0ljcyzhFHur4UVa7AAdtUsvaLWMzN9ZMzrEJpHujCEWYJN8F+yxJRPBslVoJo/xjyLg9VXz1KEML6hhNMHkgkmICFkcwLxZDpgTcuOJE6QE3uXkatP6yjt39u76VKqDI8MkV/Mas2wbiQE9a70Me10ip8+QI6K0XrQiifvCLWpoYtQowhyFTSU+vGV1r+Nul81ORJUjgx8HcqM9CXTqBnemmGEgVgufV75j+Vctf3Oi4e61KoMXRCWFXqYQclGV4wA6iy46ULQ7caZXh5ZhAlFMDEwHfv68Ke/ftTrfaWzVHWzSdpE85tzobpSSiUpJ8es41rfOfnj+U3DnrF9sdB7GGjiI2Ab92veVL2q8TVxbRVICYENbXEaUd0GJaiX9BgSs8QDuI+0IRPJduyXvnFGKjFgwCjPHj+QV76l+tuxDf6PgKRMPAZcJSP0ZAL/ulCDQqE9g8ySJkgKIcl2ZQqDFqo6nSOe4aTh8wdZYX0oEgVp2MGYrZ1iMeem38nvlyF3GjE882xjsKAWXhWNNfE1XfbnNCKCMMbIZLTTLhNoNtQMvHWC292ud/YSKtvTju/eGkPiL6djdyLt70z2Vp1NLwv1R/4g1rHmtlVBJQ+BjFMOFsnk3HZNGfOfg+2E3rntfvGgD11By3ykmhIJY8dLE3wG2MARrsdvNDWcCl+2FinxKX7Nm33G0k+cbRYoaDaI6AoDooqxKFg5swuxK6L51/6nB+MT3BD/SS3S7zTF3+0Unv9b0eGi61hl531oJ01efV/Nzq09dIkEtY4mJCkRGQROA0lL5xp+3dzjSmnUQG9R4heQ4srCtAU6ED5pehWPWnYwXyVwjP3pO87BnUVsJE66z8dQjG+1AWkqD/Oa+spF80AP2NUrg7wcCSGJ9Iqu+NEK26r7p6cLww+cUJR9mBfzH+aX8PdHLgpKPyi8Ck0DqVRT0tI0fANNIHRc69cg8rXMoXrsQ8XrftRVC3GZdz28lSiJUZWfBpGOYeUrzjNtSORHPlHlbr6hHlYlMeTmCjh6fdOTP6zjaaSSf+GMppJMCcX8txYqlahCSY0KlT9TOccZj8XPiS1LYO2APA19l9rgILac4Ui9wDarG0X8C/+Spqci2oHpx3fA8bWfdF2Wye/R66ICOWY804zlpkK9lr7DKOWqJHZ5n/ITsQTJJYwlPWKOsVFaEVcz89CbxAWQmyNQbGOemIBZE/qvxlNBiH03GGhjJOfTFDyQXfwIBXCMLuyogZsL+NhbvHtlzlJNwzm6cBhfLK6uu/vcXAhDgfyBlLKPmeDZ9WkGOajLHZh9LVDSWPy5EL8tMRrg6+xT5wDMOd4g/YbFvMHWkR1NI3fxRonGlEKSnrBxmoAX8vRUr7caO8INrFc5kpomQ19k5APv948V2C5kPiv54vBSkmpC5+mCHBVhoca/GDGyvSGf1fmUDLP94yqdzzDfYGbG+z6POR4yKDkSKMM8/IeLQq7ixjS4Kc1ukVmUOaDo6tFuiNpL7AdGpAUyn3YG7EZk5fd/pPdEgqmS4ZbhEKtVZqZsGnPe0Yojkribwyp/9MkHmG8iTq2TEH910CQ6UDoLBqtfFK6eiUki7be/qEd6Zj4ONFZUuPZGCr0EnOgDkGLRg7XKxuYtfHZbogUnU+zoz+vYDS6c6ce4d15FYf+7enYZTdQl8QLZjdEtC9UNIbI1aVg2SZ6VZMKb7TYQvDz3hZWmdyG9W4vkjCJzAKIF+aEIgtDX0sJ1Hy9SI2j2N/D/UOa1Rz6ZSjrtJqTEKDWCRDNBDLuDgTQ58fFq7uDBTFHuvx6Dm48V4pfoGf41QmUUMcE6f2MdJGqrXcK56zvZ0GcrGyfqYBlNf8yKvulsK7rrGhxnHYq95h2A3i4nBOMs2yDE+v7FUQ0oupYa0WX4oTBuo/UXYVszacwguPWr3PgmXaaSoR7bcNcLPTs6zYCYBXUcHt/DiywSDeqeQhsYSPEkFBPDsYNp3JSq1tNXFj1DXR7sDrxyaqMQ6JdTIPGrx+t3NEaMoq054P2ZG9e8XozF3dCbPmwomLP5uM1miHykRqw0X8XUUMsKIalTNcWgEl3MonqsQgOrRg4cAILz6PrnSx6uGH2uPqjX/vXphRhu0Wr/dNuy/Bs78rROH502fQYmej48CnxohoT2tLHzKT17+7QIFg+3QR3WQTNC+ZdDizyM8DCBro9ZlgjAvJ/8+hndJcd7OIG/hE3vGCZnH3d9tN6xbeEAscwE8XXy5AeHgdkKVEsI2HGBvFUVXOxduMfc1nuHSM8Wvx26KdAJjw4YsSDNpXYDfKBSc1E4KOebXIzJIyCpLbXviU5PuaURxa+RyONa0RT0/VGnEj5p/OTz6oVLRxE2Tq0tqFou6e/4qxl0dsSABPaIr1kqaSR2J6L/2mj8NvuoNiJ07sQSqRFRnB8qN9vDtXZ4Y8G1oHQkkkfsJjDzuV6ZDASNxiAtlNK3uuXUIur7q5tA6R+uwpBtu80QV2v05Bgb1uzT89pRgcuOWRmxzGjca7ptQ9HBp1nZ274ENpw8UmqJKwRaivUIASkfjJEp+TOb3Ok85SR8n4C5P6aaxjxfwhDOAGTIUjt7Xz5R0r6a5JKLY5XJ1djZPbzQ4w1LTaB59t6ySdN/Ut4+PydNgyvlmBmXbPm6oAA01MXB+0mpw007t5VAvvmz+UnxO9zl+0m6XfgurqGViPh6gatNhPvQURj6sO1hEa87E3vGtAMmg/x5qWwbUaU/WGD0By3545hBKFHFk5d6mnQlVD1EmCEaPlHIEez3rnGm65BWXh2dg1KZRpywMur4gQ2g77BftVBJLshA9PVf+qIk8ce+1GkrofhrQAOgRqL65KxKYhRz+6fztH2EO2T4Wy3JVcotW93pRG2JwkgFRlFiEFBSwMDZob5qoQkmkINcFbpHTTRcvdUjZ4/uZ5tPg+mlw2Z0ofPPuC0py0Zqu+xlkFMAmhaJJDBRTKrsYoIfUgqqwvVkyJrH9MmP1PFdyFVvIXi/ljBKNUdU+XqsdTZ5y+7/ZDdR+edpCFJ294OtZ3oI5cQIVV7/HBciiBNOio1xMxiZjB+5xX2Q88Urfw6m5/0Yt3kOJWcDOv++kTfWWR65vXHlOlP2Z33hcNOgeQbnxGKphAxUD9opqcd0sdGB0L0v9l+a5cMmhKP7Nuwh/GB3fTZMISajWPqmpEkv2VJ6zikNObtR9buz/GSOkqFEq2AZsHG5XoM2e4OXANEgiI0tLmwv5tncs5HxroYeiGHaO7wG9Z79mIfD+dXI7tb2x49eY/iFF6ypy+aF+J9vO2qmbEHAge+bx8JIkBu21iZPChAenIb/0HGqbvzvjN7wiJDFEdxdl1xpu4A7+/N6f0tUFV5kgO+WlFgvvgxNLdh+79ss5fiLj+BUFu2LkQ0horLOMuefoC1e1vPTdsrlaTarUrQ21LAkpAtnXn/YUkMbfHK5HPHEdLmeWtwjEYHgo8XF6Cc8UyQFteK9Zm8TeRl20J25Z1G3D1GfXIB5NZefF8sN+mu38E6YqSp0jMZIF4UzPjKLr9I1AcmCmoEy2WZlbru77KJmBn35+iYtYgEWCXv+YNT9SezwdOVAqBPHFyGZJorz+q8XHbjJbNDEwgzr7ZASqUla0aKIzMMBsNY/mecvVQHCsP7NZPGBLL/966q4oCrQN6VVSwYJwhJzoGYw3I/p5nArJsgq//LTfb93RtQa4N9I8hQIC8INBUueRH6sv2qhLY+OVfC3jjb038Mn+C7NtiW8ZQ/zjgZCK9e+4jR1d/yLN/ZSM0woENCUWCmMhpd9pzrH+2D0BgdytOh7sKvsU+kh54V9ZMlanfnbNbSsv8AchqA3OR463A7rx12+k8inTHt4XGqEArF9uDNjGHlraG4l6J6RMDBjRHe0cMFbguyoikmdo16JEBU+T17gluFTe/IFzzurE/Sblg6vfavfy7JwQgw7iB3eoUzYoWTB1wwKzlGSh6h0F6MkZZ4AATQLH9wHh9StpcPb0URV7L9Nc4UMkWAYMGETBOump2cac8b2gAKeNL/n2+dlrGf7VZBGHlJPRRzPwap0r1ORnhjBapkuhzAL/Meinuc3arx8R64UO5UJRgpFH70DF7OneZaOb4zUB9tqDSxpeOdyhsduertTFLr6QSHI0RConeC7uPLIx/rsBca8t/ptwdQ7KJw+222ZMX363XI7grAO2xP5QJH4v+pxjY9rwFLgMRPXEikpixIUUWgS4/a7o48l9YPXx4TlBDMUf39X4qvQVu3PT2PfCrz+TBH8WxsRLoiEHzmXtniF20022OaRknDcgaUyp7FmYlEpiKXwfhksE6G+PjHhXl1lLVU47M+l6D7tcqEUf9dtCDG8ohv/wk40hJVqVJsCr/0KNQlVKl76nlX5tZCq4iYRrfBwhbUcp4YKBxz1fKUN5P5ngjDKDlj0FxYrbUg1P0K7mwGXnpTk8wVwJa1QF0mJjKRsZzBIJSNGpvpPi3aj0MwdczjbOaNgItZF/C0bnYIYv026pfUwdtfS3oaf6ivyXAjLy45CG/ojc59Fq3gk7ZcnF7YXFtu/felzd8UevZqCQtpCp34EhwNSPkq9xmd9fykj0zzXrZbZju5ThljRYvwT3iCABr+nzO/Smz7zR0S5jbIAhsaxTbl/WdxXFMXjA6P0v3QwlZ6e3M7Alzk7mPJ/di+H2oquxZtWYNPejQ0UFZ+pkI1/VH3tXOI/5arumsAkeak+FwR6BUIqvD0qUBNLSBI1sOmGLCOyEpP46s4T6a16CA7wUc+ftfz8LiUQVy9Nd8nLb1YlJegMDVS1QzKS6g0CBa4hJO15fS/HHTOUEjQsL67uql3mvTIrfYdov0tO/5UY+SIShGCQMvdBEC1lbQPyv8sewSDLHTfZx24s2znCH54/uGG+zg1uFcGoz0HYI0VZhSDDcnLFCRJGKqp1gAIRuZxITMdxzXa7Bmf0JDvkdXYV+0ZX6gn2rAIUkJbzZVrNL7At5TtYw9E1UH1Zv9SVF92SruPz0ZVh5N0MLFZXrUyzm36B6KX4ufFQWo/r/JwSgEfxFP9H7UNTy00SAp0swhxiwhABSX1k34dSGI34voaXNx53dqto2NW3bM+Dpqi8kDg9LvReZeW60a4NOxDi73vxl/1iZrYJZFdljCN0DnZ14ZmNS7bZp/Ld/4/PiTpI2lnb17588ELgh2JghH7SYu/++gS48SJXyhX1Th9tzp6YEtgcfLtAv+lM5kl2VPePDQdNc89q17c69SrUWfFWA/IIospZaBeQztNE8ETq6znC32oBLt14hE0bnrFpnf5nPaHGDx4wLjdVCIlC77AksDaOEZK8uugBOR3tFV6QpyXLH3Td0dvQrqgQXqnlBOeAUHis/JbKbzFuAAnHYKZU73n7yIuw8O20ytkk71rxct6br1Z3ApZcA5RyYw5FH76wC9DJq9rPMq6yqBcZU4KUBFB7shrBCxBtEtEAVEswLm4+JNwox7rgUc2u8atTE/UkLKDCJhPDKkuuAIZz8tdi+wwOVuKM48AG6B1AGwG/guaq2ERveONaseEdQcTWYeAQGw41IpOnzaMMwyCEWpJEVq5qdr/GhzjZkub+9n30iojLCOtrdCEyWksl39CnXd9epUX+0/obvLd/bCBac9ci0DDiuisH+c0yzPbzPA3nAoER7gqcHHx1bO/T14YEaUZPWJHp9SVkAphUWQDCFKogdrp4PV4J2bUGpnosoXmZB9HTe+NLXrBiJJ1cWITURA56TEyrhgKPR8i8x7cz8qron/6/pVx1pjhHiQweR+MnLtJj7S68TGXBAFh7vO9lrF7mPK6GFj/tToYU6jE4/2r4Qj79XIsoWpB9tbt3RUAJrNZhfZvVr+5hQI8pRAniLx5FqWGuxMl0zuX8OSVQJN+pnQPF3P9x7FlDruW41qD/mo91usjGgqA1NEpArM4jlCSByffxboxop721ww7fm1JMEdyRonKEKMgW3hikjsLCF4C6V074hgfoRvxrw992hdWKCMhwaruDxT53BUZkRMtgG/HsXjRoeMOBFwH7oW8lcB5mpyw2/lsmfTFpiFhaoZ7BLc82M2eBXYKYHEzAEpHK8QvAknLQt7SwYeemraJojPtADjJ3jHAn/78+I7uPXzgRWhjT72ok5iG6qZDN44oGjUhX3PR42kNH/7XFU6AEqbpiXDZdXhj/GcgtQzjBn2l3J20CWkzOnhjjDmub6fV3XmG7hYJtaklsb07f7hbMM+qYSwlhZshlmIQi0fstpKz53volE1m70wJWPNEOgvTxAFCeAJ/pLPjnzXPxJyEvjSwiPBoH+hjCWRINfyGZ6YuAqQ6cf0PVLWOUzl3r3Q5KRCGRRxc2FWPIi4aCjEHwO/0JNH4M3zZNzUWhTFGrq0Yjms0LDGOJmT7u52bwnl6lTBR1g3YacT2unQOsYmTmGJdSkmywdZMtMGwtHwNVUguCHU93a8UdcP0vOjU04pGt/UbSkvz+CWGpZnwgQWQTDSuOdz1OR5hrIciYnXGbjkXuxT5gEAdhRE67omt1U9oIYIJ6nTdhr1yClOaUIJPblnjz5jRpoeCmu5dqtHlX0YSTny0AeUwEtwg7bVCND7Bgf+8T4VPgPkfi74DG1sUK2bW7Ds6mYmywSYmM5XJ49YwJOzITzjz+AsXHF34UmDZkL5aH7Q+RUeTEvIeJIKnfSNMZXEGW5HvkngZjUTUDhnEsvelhP60gzDZjvRhBIFeNDbDUf6GhrPTpIoj8LOwamKttbGaVoNpWyk9lynYMM81r1B9JZ3tEMph/m1qQ33yqScJtWitgJDmc6oTzDeEjDO5eLLC6EtQGIbU72z+tUzFzHpj5iAFYnwLOtukB8WQEesP26cz3bfMq+jH3VuelBmcTnlXm9doKN3mHrL/Y0e8/PdMBzjNJqN5BOE8u0sG5b7uhuybjY9N3kRBz1ThPnJCj3l1pXTqIpTuOwzfUVYqq2lPpEdpAyMKYYfylvzcotI8zlyXbR7ABr2e+K2pUtIzt+Q+Zz4O8G1KlKdTRfk+Rb442V7+a8l+gN9GJ94QgPZrVEFKw9L3iFVKOpnuOGXqCu485a6bp17hJ76+G7Pox48LiZ8gGCer+QPIGoG7T/VIUYIdjW36+xH+uucpn02ezdeQYQXj8ru2d8LmgY4yeQZx2DJfJSO7Yl0uFd1mBdtcFyfh48gBGQcpkHZ9DXoxg88vG1OthcsSVxIwvYHMhAw28VW8dxU4xWCxP5sHA8j8a/4E6htZt7X5+NYtZ1PyFdGtLeTWFFQtbGaf1Zr+DzvZ66wQolwQ8K5cnkchD7mDFPja3pEUL+pFyZjTcivDRZLidN56WjMK1F/30EkHwybVbREIqqVxurdBVwOw6iFBRRKVGfIZzyctRE+Xf73Y9plyT4z1/nsR/j7C0Ik0CWsemN+5Z6FrcGVkXqIEKSprp6ROIlRxSy2868cAcToDKWr36n0G1TeKmS2eZ8Nh4QZWpra2XrbvzpYQraafjBtKhwco/KH/i0P2nwKj0OO3DNYeGU5BmfVj67tPRsAWYQALPIWB9yswqTagc7aB7DgotEbAGewHsQBW7darmfiCMYy2rfkvj5O5NclQeslcCr5a0ROlmSpSR1CUpOrvwJG/hISkAFYUtqaQ11Jcf914Xs8WRStcW+ekoNbYR2tYDKv+y7cPWKts8+C5hH130LwGiDdOM+FIgOaL3bQQmW5W1owHScO/X+Fn8+nQbX6/UZjOWfi66HmhkrVTgcWHBdR1Ijo6xRQm3wAY3qBcPLVS1oCeYxYE+WQ6CCRm1Ncr7OBWV4slROYAK8/e1Owx5tpEPm6KcQpkn4LVCryIj722bqUWvj4U57aLssfDV6MvBuKg6h/DjiCJMpMIwEsD3TMAQCycmcUvG3DUxCJjL5XjqC8+f7/tzhZGgLT+2zWCbD589M4tmaLs7Yzq3eMER9lqUyHoEYSaXgBmOUf6+UAXo8+SEP840oor5cNaFSvrlLL84SbUjLmZBHQzzI6GdMWYm8oExToboiUoCq79jBsMbnw3z7O3dSTUN4CNNxBihgBqnxneAYg7avruK/jeH/wB25FX5Rr3jYOuFUdLQ6MUqnCVfSrMl0lp56sOOdaUpRX3PTAQquZ1Pc15lZI7RvN6khEk+BZi0xLvWgxxhR2N3iAQ2AMCp7vsskSBnkAlCCdNrpZ46R3jCxhNcKxDsEUzYisjjykMTEVY7A1+0pHVrJjjBd2PQW4udfC3VjiKuKJ16jxWiUD2Qg7kj7KuXjOwXBjqtBcCnr/0v1Cdoi2VWph4FJtPePDUlKDEHyv/CE49wtmQKP98YXZZrm0dQbV3yJRe5EkP6BB/3fWez91588l5PKKJdnEnBNcih+irTEMJRlfp/9bkPFS7FvUWuXI93mNTmIZAh9X7AzSksULyNqOcILrasqGp3h1xibOFjaGPd66BnKJlH9pXbh759mNNpWj0MTDYDrdRW77b5GJyq1XxfvylDRuJ7kPGum6c8cOGSMx5ULtKKdizPDzfXEcKAFbkVIBfjeoCZZSLtXBSM1tDGl2w01/2rI2PHiTF+EXX4lgjaNd8Zcue0J9488HU1a3KjtTHWFo5xEhxAGe+6kyq6Wan9VJyzQfhELnBjohGNap7mjGhQAJyyFyOpbi9J8ZNHA6yyJrJ2NIHANsNP5sYROXRoRywxZVPacPaU7fSx/WfS0uNFw4IzW5oRi9GRPUium5d4W2RUDsV4IvkAGZ2AxjjwmOEABKuer0mI3aXiZOo1SrbbaIPqdMVQGwCbyUHEP5jMzXG89FxxbSMrgpsmVU1C/huAE1FhfhTd2XsKXpKwKixypnjgFcMSjsj+f/N1tt3jqxdxesZUBapJ0Lpzz57qn7fv37AscVzOE2KAwWmzAtW4TrmCAUzvYZJXUNOEbwGqX9Y5XShu86h0sPkI5+UKKvlg5StkWWnirXMWLGulQ4JG4WDER0TYsna+f2VuE1k9nhPSvGKXv/LyMZqLFZaF/7sWXVohHxLG6p1C3vY4ELh9Dp24QT4xW347hGtyS1iPfdE0/B4QjtRZj+fP7Jli2Z30bTBBrdNgiTdeA62LzSVmkMjcsOChbFVh3xs2Rc6VR4LVrebve60tnlibDVLhG9AQroQUpasdjByIYmIxBa08LlQxkuH7xvbUk5PKQuQNxWmug9j+BOApHR61BqPWj4oNffsx7rGkN8H+sPN3FU9ZjePdu3oS2GFp6KcnWu7pp2j+W1bMeqpCg+0GRV3WLznBF49P6IWN5YXeRT+XGdAKmAVIvLR/gKlEdBQNXFvo12X3Q87G/OISXB20/Mt+zGFkoJuDSxV1VbORN2A/38hhlQ7rqTcckTxbKZICkpeDI24Q+2rZKudgmU1Ref6N0eEAwFvcO7+VCR6kPQqkQE6g+2BSVLiuBC74afDFdepVcj/2DV9Kbm3t1FqFD7PZiYbX3phKtno5PVValPoxR+PHw19/uhu/EvvP5OGmEYZJ38NAsODCq5z5CAKFt4WAWAW8x5G0Px3Z4Uv9rBDpJpz902ZIziS1GcwtKY04vyCbjklq3ZnFlUsWc5CZHQ8AvEf8qZhgjc6MECcKKC5m9j2Nw+BBM1acxbTtSz6XFHYYsbUtm/jVj/qJTOWPy4He4XF+FDCuMextag7tZfEMlKmL0Eustz3SeB1HGAOTANNsmuaw/UaiNt6ggRxSNDn9v5GXRwQjH9mIbLq854jZVFQA63LF+ft4qcKRwx9i4/1+eKJIIF7KaExh0vnC0aB71FhHe1TlYkUg0N42apMCAahbWoK9a9N+HwXAKS2U1O+m30+WsakFPn9t8ySdcqfoYVQ+FRoFWcN7HWDex4+cmU5nKQh6WI3W+s1tNvBEk+b/dqcjM336+OU/tCxaYfaAjoZpKe+SFyKpaa+o/HFpOI+0Z7bzsyYuefp/U6DGHxLvco7YYSPCVC+KHdrlIs2ydd8Uj4D6/VDbLLg6l6ZsEA4zVP2eFSmLpS1IuXzC8X7XZQykxh/CrGFcnRi27rnNEWS869uTZNqpvT7pmXFULGd52fdzmVvKvE0axEwMYImerTS4+GI6LY2xwNeKZaWrVVn8AeSoo6z5QSsHiUS8/iaIyYHLrIHl2QhxY7p2tuSpRS+4et9rg3Q5hlNwGcZXlDwuQuPFqKO3+hOVZJVRX/fDUsq4a0AG4+jgBBrYcAf0Dp4xX8QqZTRNjGrviw97QqcH9RSDsOLkp5Gwp3S4SyjVkLXLKMbn+LCoDx5MKtbej6eE0kyU8KAdMNkzCrw7/IOnKi53OlUTjDbLRa2RIfTzgaYeTTj+lom+qG/ELT0FXJZ6dzOhrvqukysqZ8ObxosuHUiPg3HrlJz818Oz3+BSbUDqtOc6rDZh+1XvxTqtw9xf3sdLB/z849dJ/cqEYmpjWMpseFpykAgm6OzXVkxcl3GGvnqdAoWHLy1fcW+JNhz8FMkK5i8HuNmN3JmvwjftwkeyX+s5UdV/GsavgHelRewTYXc0BocQNNLjX8//cNrsGMf2znWetr+eF8TUcCLDLLcdOQhPWzuF5D471u9oAT5ukawOiGGE/ajw6ruLlm/0rzVlNmiePQdYqZf54fjG25KCL7+0BGQrPJ4FeFkithrGj9pypJTlqe7SQBEYfDEh8gWjY9O7xkaW1yya+LCtXGb6xNpMt9JlpMb0qezOmEiF9DZheCpouzvKeEYEjqQRILkPyxQmZa4IJ58dxzpXG8DVf1AOuS1e8eFbAbY8+zaHFnQ2mDHGgDqbOtddJrCJ+DBagP6OwwOnVqMTtYAbBc9nKI8xwZWq/SKlLdwwbruUReqf7mYwAX5bViUiJdGZUiEB7v7l1XouO5D533UGn9dIU1lHX0i1qBB/2RS8SXGMpZ5/RY0m0q+QOIKw8/oTC9jaIgEl7lfN7QOtBQikX89FRrbof9mmk2YJUxF3j1ZV6ok1vDzdIuZ5p2zxLh7ojW27Ka4qHu+8qKGj+wzu7Y+jwjqrV2AWoKOO1QpCk3v5xda13rjyOPQvlFgSCdUK5rE+5SvcKK+7OcAaQbE/9T8H7DCwSiK2NjsIo/0KWUrIGdSwy2GSkkQn2jjLnAXHaHS3rl9IGrbghNa/9DZziECJUiRea0L1XWf/QERXpUGNZgEn7vbQr1dMf92Cq086jVn2chht+RcCqMARq6jdYnucAhddZ8KGXrFZYJAhLoG1T/A9hivyVHMPeau5x1GGuVgBQ+LBfETEPCCmJGXOa7yNy4/QNIiJviCVXjL+KEVUB5oremCnjx7/Y5Bnrdatr+19YfAxxJ+DJsnfeh5bZkyzOGCuKGI87uvOXaHjWugb87K9FRxElXdOzjwzbTYP25r0Kcv+0VEbqbKN5sTkzKdXWdwmSeIAJjbewNODZUg28ix1+x3FlOgJor4MZG/I7QTA9qManWQ6Hpt+nC9lNMOq+9iiqCATFBEP7gB92ANR5og61D90043hQiRmA/AJ2P9WrgkSRmc3j/slgjXsFdOAXDdCFRBAWoTYM8orlUBstjovBcHzCzn1NfYocRhkuuNbyH/c2u4ENpSwCHcyxSIjySgLmKougH8Jmd/d9KhK8zlJmSuo6g7wVIivuP/abkqEhxyrIGUUwQm+YpnldUeGscsLGmcnXlrDe43AAaN65vSWAN7WhEIIkgh1AHWfOg/0dWk+2dF0VZlXAGKbxRranV1TJGrU7C0tlrjjJKwmGQGfLGrbO1ViV0NPxuYo75XhQgiKPdnaqAMVhucCwVyWZBosQf2UmtHSQ7YejkZ1Jz6OnW/SvGUzOE+Shp8yhrTWsNvu6QZ3dxBQ4YRh5RJ8WiTTtbjlNy7JY+biwzc0q16edyosnwOrVDrgl3qVd3jaQBoOXM/oosIvx63Pri1BYnVS37lV9wCqWtP2y4CAR4jfGJdNxzy0NiHIipFtchIDcYP935xb0oBXefLC7AJxiKhL/+UBtYvkK3keV+QO8xHDkwRgNULrzgR0pgGZoILF04j24oJuemglAeMPVJhBXhecSxkKPhvCayfMoeOP1SNmIZWO4+eafBOBcgCJnj6Eg3ETe6kUUwLKHaQrK2QM8ZUwH17pcr24mtjeN2I+eX8PocOswkQEgzN6Nnrp6Sj+RPQO333SvRimD5RXih+bj12zsGfVKHwVqIu9uk+6qzifJtKnclx0obgqixcaiOtAWpo3MzHXAwMjrvdqNl0KYnSfuadDZ0RbRZZt831BtTaKiwk6RaDdiymwUVteg6vUzpOcx31w2tg6y35+//v94cSxZZOUEbpAmiQDih1i+eCNAtgOUjD1V49B5QH+TXzDNVtpBFaNMQPtnHXvRXSaGO7SsGkj0LSeIeD2XSjR2PEqBnv7kKcqZNrUrFEIP7GW9mSODHqcEeCckiaJlBZaObG4PVCRi1i5SQ1isnrIdtonF1KUporAbqwfS7POnkZLuu18I9kFHhKD84fvDON4sVja4cywIEkhA/hGz3Bib1bKUggz8595PaiNjMnfChgb+rwSiyMmlqXntlwTZ2Rq3QIuCWFmaCQRSpuXFZ0VN+tAKhzXtOpv+MbMLcwNvlwmcW7kcjEQd7qT0ojWm4xN/znnvtiokpJAwa2vw9iVa8i1TUa1Rc/UpjpjpXKF4iieIf5WA2/M6WUNppJmkwm89dwFXtIsfyOMA7jLW2tMFK6TF0eMCLnGf1oucaJwC+Pncfu+KvhZkgK2289kxFt9I00zokopI3zdJVIZXYkyq4AC/PkxQhpjq+BtHPe218v7httaDE4sf/vVLgBq4PCM+VSJPFmyHhOAH5khcKaTsFhaOjXVx3+YeqGcYOWHECAPecXuABAYwr/pc4HJLrK4YPp0v92W6ka7DPPkuJaGsd/Ej7sgM7OPCwTmNQhn5GFO5mlI+BYHhmt01fonJtvs7bPVhwCbiaST2pqo/ygkEdi9UWYBayGVKN6YLroGvQknc18ImY6REHptk6ts/txxIdvdRuLq14D2UPigdBWD3BuOXleCAkI3ACSJ2v7A9Yd3uJBkrP0bpz0EponJLonb6K/gjP+KoMcCZdP+CXuA16nUQGNyLA/9wRTgMbVPGWTeaJVeS7/ycqGObQcOgz0aF+B6x/dUMtLlUSEzmHeF3ufe1YcCwGp2W6dx9n8FeFyW6OR32Gu5G1pt8jSeXH0xgX3JM+EdYPwW2DQjQh/OM7mPR/Db0Qir7iXkrXMx2tMkBggSkiWUPP4Rfh8UwNJwsqAjrCVPnzvgc6DO5rSJuy/R/FAgWsAfmC6EWMTjaoIooKhSqzrJ+Vpr4/f8ZZS2m8zNutSl+uFSAncaQA4vvPmW8HGcNq1dWLQqH/RRg+q+/00is8YJZYH+d6HIXYaaJVxSmuEYwyXC7D/dEzzcjgjchxK8Nr1zFfxajzxrzl/B2KzUSyVY4+mGRA3ebtLvw7RiVF6i+C5EE3kl8WQK9QYo2NoNC4P0g5wBbl08mKdmZn6Szk1aEXeJgrAfii+O150/hD+lfsmjTFUyMB7DzBP+x8xYL4BHu/iTEVADjPepcjq1ciwvB9oxAszkyQVyAkg1cTgk4TxnCJG3EPmy+zO7hki5Jt0bysjSBl3SXLjIS2bXeB5BkPF2TZtHqoTKV+O6e15WTOYA78JqSXVHwwsHAhw+MoU8FEo5Vv7qDrOHbg4QqBzEw3hmWS7llNrnkrGHeqGafeQ5jvdWPhaQdkYTSIvuSofXmr6K5jNKA5T5dHQmBuXFaEVLdvm5d5mFdMl5Cuh9A8g7FRY4Rw+eug2Rr15BGLpqXFzmyPrKQ9C6VmdHCS8t1lrIFwiRQdLQCAecsS/8OT0eEoF3RyC8L73MYDhUCebYUZBASYJQ9WHAscKEO+lbwOr9W8FVE3sM/CXD+dkUzYOjh+bgqck9ipNGTUUbaN6LSfhtLWv/w4HvHYImFuIV/F32oDKNtJO7FQLlhu55m3vi2xitt3bB47T24XZF+pt5Glw5xOwuzy0kM0cUeZS99+fxczvxRZISfCa99GQrIuytUkqFQNLliojSf40uDcIyOWl7jhi0N0FdVq4YamFgeNlJ5Rv41dFDID83/Ghnw7E3e/e9e7LaM9ZlFLK1KSWLfkHifiVUrt9Y5cIDe+Ow6aGR0rlDsKLmJ15RNxUwvhy2fZpfn8L01ggXjWc76mpg1ZWGl6FbXPLKBQYnb2lMUB4tRUskg8xwh/yAONBuNWPm8+LDHtOmGDpz1s6AaYl+MHgQQwUyvYR0GCymSWB0AP0h+p7wcIzdGIKSilrMXflbitxtkiT5XlnhHh80aT8Tk2+4/h/T8lcCBUPXpg/OzZ3XCS+b+G9Tmpcn0MtDm2hnWOjkIvf53Pqo/8Tjfe2ISLZ6qCHs+M+LQVbGn7wzNU3oYn3bDK7VcawuKmxLvT99g+dKBbxoZii0suhucD5BKaLqNZUac/NRhMj+PdUJCxY93Btlx8JB9JHyGJOx65Ee4RuX/VKP0AXgBal2+V8gCsSE98OyS6w0zHendYfh3LFt5L1sdCfwqnWIztXmKhBYG2537oeQjmXrkuq3EnPcDppDptyfdECMO5LARjsHoLaeqHYENLNYJQOrBk2C4ZJQM01NLOGmfGedtNrM8e7xr6OFqZOOv4izNnmwcLbRWr/NbR6dauN+F3z2EUsGfxqyKb8A12B0HcOxKYTChowrr8BLlAXul0vsVptp9RFiUmJ+o1jWPWd6hnLnGpT/NWIlslXSVVQCo6scnPMUhe2oaaX6eV8lH2IidBa5IYPmO+E3NFYTCAshSCcO3FPfeVVDkJiQBUj7iFokwp0xKz8zGdelyN5+yu'
func = 'main'

GithubUrl = f"{THIS_Proxies.rstrip('/')}/https://raw.githubusercontent.com/huaji8/So_common/master/so" if THIS_Proxies else 'https://raw.githubusercontent.com/huaji8/So_common/master/so'
THIS_MODE = 'Huaji_SoLoader'
So_name = f'{THIS_MODE}.so'




def get_system_info() -> None:
    global Download_name
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    download_pyver = f'{sys.version_info.major}.{sys.version_info.minor}'
    processor_arch = platform.machine().replace('AMD64', 'x86_64').replace('x64', 'x86_64')
    system_name = platform.system()
    system_ver = platform.release() + " " + platform.version()
    system_arch = platform.architecture()[0]
    if system_name == "Darwin":
        system_name = "macOS"
        system_ver = platform.mac_ver()[0]
    elif system_name == "Windows":
        system_ver = f"{platform.release()} (Build {platform.win32_ver()[1]})"
    
    log.info(f"系统信息 [Python/{python_version}] [系统架构 {processor_arch}] [{system_name}/{system_ver} {system_arch}]")
    if download_pyver not in ['3.10','3.11','3.12']:
        log.error(f'当前Python版本不支持运行此脚本，请使用Python3.10或3.11或3.12运行此脚本,什么??你不重装,简单,删除本脚本然后睡觉觉就行了..')
        
    if processor_arch == 'x86_64' and system_name == 'Linux':
        Download_name = f'{THIS_MODE}_{download_pyver}_x64.so'
    elif processor_arch == 'aarch64' and system_name == 'Linux':
        Download_name = f'{THIS_MODE}_{download_pyver}_aarch64.so'
    else:
        Download_name = f'{THIS_MODE}_{download_pyver}_x64.so'
        
    if processor_arch not in ['x86_64', 'aarch64']:
        log.warning(f'当前系统架构大概率不支持运行此脚本...')
        return
    elif 'Linux' not in system_name:
        log.error(f'当前系统不支持运行此脚本，请使用Linux运行此脚本')
    else:
        log.info('系统检测通过,开始运行脚本')
        return
    
    
    
    exit()



def download_file(save_path: str = None) -> bool:
    url =  GithubUrl + '/' + Download_name
    
    try:
        try:
            socket.create_connection(("www.github.com", 80), timeout=5)
            socket.create_connection(("www.github.com", 443), timeout=5)
        except (socket.timeout, socket.gaierror):
            log.warning("无法连接到Github,大概率下载是失败的,请检查网络或使用代理")

        if not save_path:
            file_name = os.path.basename(urlparse(url).path) or "downloaded_file"
            save_path = os.path.join(os.getcwd(), file_name)
        if os.path.exists(save_path) and os.path.getsize(save_path) == 0:
            os.remove(save_path)
        save_dir = os.path.dirname(save_path)
        os.makedirs(save_dir, exist_ok=True)
        curl_cmd = "curl.exe" if platform.system() == "Windows" else "curl"
        cmd = [
            curl_cmd,
            "-L", 
            "-f",
            "--silent",
            "--show-error",
            "-o", save_path,
            "-m","180",
            url
        ]

        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )


        if not os.path.exists(save_path):
            log.error(f"下载文件不存在: {save_path}")
            return False
        if os.path.getsize(save_path) == 0:
            os.remove(save_path)
            log.error(f"下载文件为空: {save_path}")
            return False
        if result.returncode != 0:
            log.error(f"下载失败: {result.stderr.strip()}")
            return False
        log.info(f"文件下载成功: {save_path}")
        os.rename(Download_name, So_name)
        return True

    except subprocess.CalledProcessError as e:
        error_msg = f"下载失败: {e.stderr.strip()}" if e.stderr else "未知curl错误"
        log.error(error_msg)
        return False
    except Exception as e:
        log.error(f"下载异常: {str(e)}")
        return False
    
def dynamic_import(module_name: str) -> object:
    return importlib.import_module(module_name)

    
def Run() -> None:
    if os.path.exists(So_name):
        log.info('so文件存在,开始运行')
        print('='*30)
        obj = dynamic_import(THIS_MODE)
        obj.run(func, data)
    else:
        log.info('so文件不存在,开始下载')
        if download_file():
            Run()
        else:
            log.error('下载失败,请检查网络或使用代理')


if __name__ == '__main__':
    get_system_info()
    Run()
