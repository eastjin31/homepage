from flask import Flask, render_template, request, redirect, url_for
import json
import os
import uuid

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')

def load_messages():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_messages(messages):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

@app.route('/test')
def test():
    return 'This is a Test'

# 메인 페이지
@app.route('/')
def index():
    return render_template('index.html')

# 나의 소개
@app.route('/about')
def about():
    return render_template('about.html')

# 방명록
@app.route('/guestbook')
def guestbook():
    messages = load_messages()
    return render_template('guestbook.html', messages=messages)


# 방명록 작성 (UUID 적용)
@app.route('/write', methods=['POST'])
def write():
    name = request.form.get('name')
    content = request.form.get('content')
    password = request.form.get('password')

    if name and content and password:
        messages = load_messages()
        # 전 세계에서 유일한 ID 생성 (충돌 확률 0%에 수렴)
        new_id = str(uuid.uuid4())

        new_msg = {
            'id': new_id,
            'name': name,
            'content': content,
            'password': password
        }
        messages.insert(0, new_msg)
        save_messages(messages)

    return redirect(url_for('guestbook'))


# 방명록 수정 (비밀번호 검증 포함)
@app.route('/edit/<msg_id>', methods=['POST'])
def edit_message(msg_id):
    input_pw = request.form.get('password')
    new_content = request.form.get('content')
    messages = load_messages()

    for m in messages:
        if m['id'] == msg_id:
            if m['password'] == input_pw:
                m['content'] = new_content
                save_messages(messages)
                return redirect(url_for('guestbook'))
            else:
                return "<script>alert('비밀번호가 틀렸습니다!'); history.back();</script>"

    return "<script>alert('글을 찾을 수 없습니다.'); history.back();</script>"


# 방명록 삭제 (UUID 대응)
@app.route('/delete/<msg_id>', methods=['POST'])
def delete_message(msg_id):
    input_pw = request.form.get('password')
    messages = load_messages()

    # 비밀번호가 맞지 않거나 ID가 다른 것들만 남김 (필터링)
    new_messages = [m for m in messages if not (m['id'] == msg_id and m['password'] == input_pw)]

    if len(messages) == len(new_messages):
        return "<script>alert('비밀번호가 틀렸습니다!'); history.back();</script>"

    save_messages(new_messages)
    return redirect(url_for('guestbook'))
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)