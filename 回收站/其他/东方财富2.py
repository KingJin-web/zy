'''
export dfcf='CToken#UToken#EM-MD#GToken' 
多账户@ 分割 账号后面不要有备注去掉

'''
#有问题请及时联系大大鸣 v:xolag29638099  （有其他想要的脚本也可以联系，尽量试着写一写）
#Expecting value: line 1 column 1 (char 0) 报错请求频繁 过段时间重试即可
#
#   --------------------------------祈求区--------------------------------
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
#   --------------------------------代码区--------------------------------
import base64
import zlib
import lzma
import bz2
import gzip

exec((lambda _: compile(_.decode(),'','exec'))(zlib.decompress(lzma.decompress(bz2.decompress(gzip.decompress(base64.b64decode(b'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')))))))
