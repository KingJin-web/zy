import base64

def decrypt(encoded_code):
    return base64.b64decode(encoded_code).decode('utf-8')

# 替换为实际的Base64编码字符串
encoded_code =    ""

decrypted_code = decrypt(encoded_code)


print("解密后的代码:")
print(decrypted_code)

# 保存到文件以便查看
with open('decoded_source.py', 'w', encoding='utf-8') as f:
    f.write(decrypted_code)
print("\n源代码已保存到 decoded_source.py")
# 如果需要执行解密后的代码（谨慎操作）
# exec(decrypted_code)