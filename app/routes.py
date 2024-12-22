from app.team_base import TeamBase
from app.user_base import UserBase
from app.project_board_base import ProjectBoardBase
from flask import request
from app import app

team_base = TeamBase()

project_board_base = ProjectBoardBase()

user_base = UserBase()

@app.route('/create_team', methods=['POST'])
def create_team():
    return team_base.create_team(request.json)

@app.route('/list_teams', methods=['GET'])
def list_teams():
    return team_base.list_teams()

@app.route('/describe_team', methods=['POST'])
def describe_team():
    return team_base.describe_team(request.json)

@app.route('/update_team', methods=['PUT'])
def update_team():
    return team_base.update_team(request.json)

@app.route('/add_users_to_team', methods=['POST'])
def add_users_to_team():
    return team_base.add_users_to_team(request.json)

@app.route('/remove_users_from_team', methods=['POST'])
def remove_users_from_team():
    return team_base.remove_users_from_team(request.json)

@app.route('/list_team_users', methods=['POST'])
def list_team_users():
    return team_base.list_team_users(request.json)


# user base route

@app.route('/create_user', methods=['POST'])
def create_user():
    return user_base.create_user(request.json)

@app.route('/list_users', methods=['GET'])
def list_users():
    return user_base.list_users()

@app.route('/describe_user', methods=['POST'])
def describe_user():
    return user_base.describe_user(request.json)

@app.route('/update_user', methods=['PUT'])
def update_user():
    return user_base.update_user(request.json)

@app.route('/get_user_teams', methods=['POST'])
def get_user_teams():
    return user_base.get_user_teams(request.json)


@app.route('/create_board', methods=['POST'])
def create_board():
    return project_board_base.create_board(request.json)

@app.route('/close_board', methods=['POST'])
def close_board():
    return project_board_base.close_board(request.json)

@app.route('/add_task', methods=['POST'])
def add_task():
    return project_board_base.add_task(request.json)

@app.route('/update_task_status', methods=['PUT'])
def update_task_status():
    return project_board_base.update_task_status(request.json)

@app.route('/list_boards', methods=['POST'])
def list_boards():
    return project_board_base.list_boards(request.json)

@app.route('/export_board', methods=['POST'])
def export_board():
    return project_board_base.export_board(request.json)
