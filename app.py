from flask import Flask, render_template, request, jsonify
import requests,os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime
from flask_migrate import Migrate
from sqlalchemy import asc


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

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

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime)
    member_id = db.Column(db.String, db.ForeignKey('member.member_id'), nullable=False)


# Create the database tables  
with app.app_context():
    db.create_all()


# Define the route to render the index.html template
@app.route('/')
def index():
    todos = Todo.query.order_by(asc(Todo.date)).all()
    return render_template('todo.html', todos=todos)

# Define the route to add a new todo
@app.route('/api/todolist/', methods=['POST'])
def add_todo():
    try:
        data = request.get_json()
        task = data['task']
        date_str = data['date']
        date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else None
        DEFAULT_MEMBER_ID = 'your_default_member_id'
        member_id = data.get('member_id', DEFAULT_MEMBER_ID)
        new_todo = Todo(task=task, completed=False, date=date, member_id=member_id)
        db.session.add(new_todo)
        db.session.commit()
        sorted_todos = Todo.query.order_by(asc(Todo.date)).all()

        todos_list = [
            {
                "id": todo.id,
                "task": todo.task,
                "completed": todo.completed,
                "date": todo.date.strftime('%Y-%m-%d') if todo.date else None,
            }
            for todo in sorted_todos
        ]
        response_data = {
            "task":task,
            "success": True,
            "message": "할 일이 성공적으로 추가되었습니다",
            "id": new_todo.id,
            "todos": todos_list
        }

        if new_todo.date:
            response_data["date"] = new_todo.date.strftime('%Y-%m-%d')

        return jsonify(response_data)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# Define the route to update a todo using PATCH
@app.route('/api/todolist/<int:todo_id>', methods=['PATCH'])
def update_todo(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        if todo:
            data = request.get_json()
            todo.completed = data.get('completed', False)
            db.session.commit()
            return jsonify({"success": True, "message": "할 일이 성공적으로 업데이트되었습니다"})
        else:
            return jsonify({"success": False, "message": "존재하지 않는 할 일입니다"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

# Define the route to delete a todo using DELETE
@app.route('/api/todolist/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        if todo:
            db.session.delete(todo)
            db.session.commit()
            return jsonify({"success": True, "message": "할 일이 성공적으로 삭제되었습니다"})
        else:
            return jsonify({"success": False, "message": "존재하지 않는 할 일입니다"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run()
