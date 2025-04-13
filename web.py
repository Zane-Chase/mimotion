#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import time
from datetime import datetime
import pytz
import random
from main import MiMotionRunner, get_beijing_time

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/modify_step', methods=['POST'])
def modify_step():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        steps = request.form.get('steps')
        
        # 检查是否是AJAX请求
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/x-www-form-urlencoded'
        
        if not username or not password or not steps:
            if is_ajax:
                return jsonify({'success': False, 'message': '请填写所有必要信息'})
            else:
                return render_template('index.html', message='请填写所有必要信息', success=False)
        
        try:
            steps = int(steps)
            if steps < 0 or steps > 98800:
                if is_ajax:
                    return jsonify({'success': False, 'message': '步数必须在0到98800之间'})
                else:
                    return render_template('index.html', message='步数必须在0到98800之间', success=False)
        except ValueError:
            if is_ajax:
                return jsonify({'success': False, 'message': '步数必须是有效的数字'})
            else:
                return render_template('index.html', message='步数必须是有效的数字', success=False)
        
        # 调用现有的MiMotionRunner来修改步数
        try:
            runner = MiMotionRunner(username, password)
            result_message, success = runner.login_and_post_step(steps, steps)  # 使用相同的最小和最大步数，确保固定值
            
            # 记录操作日志
            time_bj = get_beijing_time()
            log_message = f"[{time_bj.strftime('%Y-%m-%d %H:%M:%S')}] 账号：{username} 步数：{steps} 结果：{'成功' if success else '失败'}"
            
            with open('web_access_log.txt', 'a', encoding='utf-8') as f:
                f.write(log_message + '\n')
            
            if is_ajax:
                return jsonify({'success': success, 'message': result_message})
            else:
                return render_template('index.html', message=result_message, success=success)
        
        except Exception as e:
            error_message = f"操作失败：{str(e)}"
            if is_ajax:
                return jsonify({'success': False, 'message': error_message})
            else:
                return render_template('index.html', message=error_message, success=False)
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    # 创建模板目录
    os.makedirs('templates', exist_ok=True)
    
    # 确保日志文件存在
    if not os.path.exists('web_access_log.txt'):
        with open('web_access_log.txt', 'w', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Web服务启动\n")
    
    print("=====================================================")
    print("Zepp Life 步数修改Web服务已启动!")
    print("可通过以下地址访问：")
    print("  http://localhost:5000")
    print("=====================================================")
    
    app.run(host='0.0.0.0', port=5000, debug=True) 