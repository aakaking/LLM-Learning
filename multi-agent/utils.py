import base64
import re

# 将 langchain 运行状态下的表保存到全局变量中
def save_table_to_global(x):
    global table
    if 'TABLE' in x.content:
        table = x.content.split('TABLE', 1)[1].split('END_TABLE')[0]
    return x

# helper function 用于Debug
def print_and_return(x):
    print(x)
    return x

# 对打模型生成的代码进行处理, 将注释或解释性文字去除掉, 留下pyhon代码
def extract_python_code(text):
    pattern = r'```python\s*(.*?)\s*```'
    matches = re.findall(pattern, text, re.DOTALL)
    return [match.strip() for match in matches]

# 执行由大模型生成的代码
def execute_and_return(x):
    code = extract_python_code(x.content)[0]
    try:
        result = exec(str(code))
        #print("exec result: "+result)
    except ExceptionType:
        print("The code is not executable, don't give up, try again!")
    return x

# 将图片编码成base64格式, 以方便输入给大模型
def image2b64(image_file):
    with open(image_file, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()
        return image_b64

