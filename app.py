from flask import Flask, render_template, request
import requests,os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)

class Member(db.Model):
    member_id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    pwd = db.Column(db.String, nullable=False)
    memos = relationship('Memo', backref='member', lazy=True)
    todo_lists = relationship('ToDoList', backref='member', lazy=True)
    address_books = relationship('AddressBook', backref='member', lazy=True)
    diaries = relationship('Diary', backref='member', lazy=True)

class Memo(db.Model):
    memo_id = db.Column(db.Integer, primary_key=True)
    main_text = db.Column(db.Text, nullable=False)
    edit_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    member_id = db.Column(db.String, db.ForeignKey('member.member_id'), nullable=False)

class ToDoList(db.Model):
    todolist_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    deadline = db.Column(db.Date, nullable=True)
    is_complete = db.Column(db.Boolean, nullable=False, default=False)
    member_id = db.Column(db.String, db.ForeignKey('member.member_id'), nullable=False)

class AddressBook(db.Model):
    address_id = db.Column(db.Integer, primary_key=True)
    team_member_name = db.Column(db.String, nullable=False)
    project = db.Column(db.String, nullable=False)
    realization = db.Column(db.Text, nullable=True)
    member_id = db.Column(db.String, db.ForeignKey('member.member_id'), nullable=False)

class Diary(db.Model):
    diary_id = db.Column(db.Integer, primary_key=True)
    main_text = db.Column(db.Text, nullable=False)
    edit_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    member_id = db.Column(db.String, db.ForeignKey('member.member_id'), nullable=False)

@app.route("/memo/")
def memo():

    # 예시 메모
    memo_list = []
    for i in range(100):
        memo = {
            'text': i+1,
            'date': i+2000
        }
        memo_list.append(memo)

    memo_per_page= 6
    # 클라이언트의 현재 페이지 숫자(없으면 기본적으로 1페이지)
    page = request.args.get('page',1,type=int)

    # 내보내야 할 데이터 정보의 start index와 end index
    start_index = (page-1)*memo_per_page
    end_index = start_index+memo_per_page

    # 내보낼 메모들 리스트로 저장
    current_page_memo = memo_list[start_index:end_index]

    total_memos = len(memo_list)
    total_pages = (total_memos+memo_per_page-1)//memo_per_page
    
    return render_template('memo.html', data=current_page_memo, page_num=total_pages)


if __name__ == '__main__':
    app.run()
