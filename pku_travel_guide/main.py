import subprocess
import os
from threading import Thread
import time

# 定义启动 Flask 应用的函数
def start_flask():
    subprocess.run(["python", "app.py"])

# 定义启动 Jupyter Notebook 的函数
def start_notebook():
    subprocess.run(["jupyter", "nbconvert", "--to", "script", "your_notebook.ipynb"])  # 将ipynb转换为py
    subprocess.run(["python", "templates\python\pku_travel_guide.ipynb"])

# 启动 Flask 和 Notebook
if __name__ == "__main__":
    # 创建线程启动Flask应用
    flask_thread = Thread(target=start_flask)
    flask_thread.start()

    # 给Flask应用一些启动时间
    time.sleep(5)

    # 启动Jupyter Notebook的代码
    start_notebook()

    # 等待Flask应用结束
    flask_thread.join()
