import base64
import lzma

# 将这里的 "xxx" 替换为实际的 base64 编码字符串
encoded_data = ""
# 解密 lzma.decompress(base64.b64decode("xxx")))
try:
    # 解码 base64
    decoded_bytes = base64.b64decode(encoded_data)

    # 解压缩 lzma
    decompressed_data = lzma.decompress(decoded_bytes)

    # 尝试以 UTF-8 编码转换为字符串
    try:
        decoded_text = decompressed_data.decode('utf-8')
        print("解密后的内容 (UTF-8):")
        print(decoded_text)
    except UnicodeDecodeError:
        # 尝试以 GBK 编码转换为字符串
        try:
            decoded_text = decompressed_data.decode('gbk')
            print("解密后的内容 (GBK):")
            print(decoded_text)
        except UnicodeDecodeError:
            print("无法以常见编码方式解码为文本，显示原始字节数据:")
            print(decompressed_data)

    # 保存解密后的内容到文件
    with open('decoded_lzma_content.txt', 'wb') as f:
        f.write(decompressed_data)
    print("\n解密内容已保存到 decoded_lzma_content.txt")

except Exception as e:
    print(f"解密过程中发生错误: {e}")