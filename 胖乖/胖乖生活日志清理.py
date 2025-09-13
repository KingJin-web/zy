# 如果出现每日积分为2，或者运行脚本自动跳过任务，运行该脚本之后再运行主脚本即可
# cron = 01 00 * * *    # 每天凌晨0点区分开始执行任务

import os
import time

# 设定要删除的脚本路径和名称
script_path = 'pgsh.json'

# 检查文件是否存在
if os.path.exists(script_path):
    os.remove(script_path)
    print(f"脚本 {script_path} 已删除。")
else:
    print(f"脚本 {script_path} 不存在。")