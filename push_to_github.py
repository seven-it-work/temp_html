#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动推送dist目录内容到GitHub仓库的脚本
使用方法: python push_to_github.py
功能：推送前会自动检查并修复index.html中的资源路径（/assets/ 改为 .//assets/）
"""

import os
import re
import subprocess
import sys
from datetime import datetime

def run_command(cmd):
    """执行命令并返回结果"""
    try:
        # 在Windows上使用UTF-8编码处理输出
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            errors='replace'  # 替换无法解码的字符
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        # 处理错误输出
        error_output = e.stderr if isinstance(e.stderr, str) else e.stderr.decode('utf-8', errors='replace')
        return False, error_output

def fix_asset_paths():
    """检查并修复index.html中的资源路径
    将 /assets/ 替换为 ./assets/
    """
    index_path = os.path.join(os.getcwd(), 'index.html')
    
    # 检查index.html文件是否存在
    if not os.path.exists(index_path):
        print(f"错误: 找不到 {index_path} 文件")
        return False
    
    try:
        # 读取文件内容
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否需要修复
        if '"/assets/' not in content:
            print("不需要修复: index.html中没有找到 /assets/ 路径")
            return True
        
        # 替换路径
        new_content = re.sub(r'"/assets/', r'"./assets/', content)
        
        # 写回文件
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"成功修复index.html中的资源路径: \"/assets/ -> \"./assets/")
        return True
    
    except Exception as e:
        print(f"修复资源路径时出错: {str(e)}")
        return False

def main():
    print("===== 开始推送dist目录到GitHub =====")
    
    # 检查是否在正确的目录
    if not os.path.exists('.git'):
        print("错误: 当前目录不是git仓库！")
        print("请确保在包含.git目录的dist文件夹中运行此脚本")
        sys.exit(1)
    
    # 检查并修复index.html中的资源路径
    print("\n检查并修复index.html中的资源路径...")
    if not fix_asset_paths():
        print("资源路径修复失败，停止推送")
        sys.exit(1)
    
    # 检查远程仓库配置
    success, output = run_command('git remote -v')
    if not success:
        print(f"获取远程仓库信息失败: {output}")
        sys.exit(1)
    
    print("\n远程仓库配置:")
    print(output)
    
    # 执行git add
    print("\n执行 git add . ...")
    success, output = run_command('git add .')
    if not success:
        print(f"git add失败: {output}")
        sys.exit(1)
    print("git add 成功")
    
    # 执行git commit
    commit_message = f"自动更新 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    print(f"\n执行 git commit -m '{commit_message}' ...")
    success, output = run_command(f'git commit -m "{commit_message}"')
    if not success:
        # 检查是否是因为没有更改而导致的失败
        if 'nothing to commit' in output:
            print("没有更改需要提交")
        else:
            print(f"git commit失败: {output}")
            sys.exit(1)
    else:
        print("git commit 成功")
        print(output)
    
    # 执行git push
    print("\n执行 git push -f origin master:main ...")
    success, output = run_command('git push -f origin master:main')
    if not success:
        print(f"git push失败: {output}")
        sys.exit(1)
    
    print("\ngit push 成功！")
    print("===== 推送完成 =====")

if __name__ == "__main__":
    main()