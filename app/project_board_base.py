from app.records import load_data, save_data
from datetime import datetime
from flask import Flask, request, jsonify

# In-memory storage
boards = {}
tasks = {}
board_counter = 1
task_counter = 1

class ProjectBoardBase:
    """
    A project board is a unit of delivery for a project. Each board will have a set of tasks assigned to a user.
    """

    # create a board
    def create_board(self, request: str):
        """
        :param request: A json string with the board details.
        {
            "name" : "<board_name>",
            "description" : "<description>",
            "team_id" : "<team id>"
        }
        :return: A json string with the response {"id" : "<board_id>"}

        Constraint:
         * board name must be unique for a team
         * board name can be max 64 characters
         * description can be max 128 characters
        """
        global board_counter
        project_board_base = load_data('project_board_base.json')
        data = request
        name = data.get("name")
        description = data.get("description")
        team_id = data.get("team_id")

        if not name or len(name) > 64:
            return jsonify({"error": "Board name is required and must be at most 64 characters."}), 400
        if len(description) > 128:
            return jsonify({"error": "Description must be at most 128 characters."}), 400
        if any(board["name"] == name and board["team_id"] == team_id for board in boards.values()):
            return jsonify({"error": "Board name must be unique for the team."}), 400

        board_id = board_counter
        board_counter += 1
        boards[board_id] = {
            "id": board_id,
            "name": name,
            "description": description,
            "team_id": team_id,
            "creation_time": datetime.now().isoformat(),
            "status": "OPEN",
            "end_time": None
        }
        save_data('project_board_base.json', boards)
        return jsonify({"id": board_id})


    # close a board
    def close_board(self, request: str) -> str:
        """
        :param request: A json string with the user details
        {
          "id" : "<board_id>"
        }

        :return:

        Constraint:
          * Set the board status to CLOSED and record the end_time date:time
          * You can only close boards with all tasks marked as COMPLETE
        """
        boards = load_data('project_board_base.json')
        board_id = request.get("id")
        board = boards.get(board_id)

        if not board:
            return jsonify({"error": "Board not found."}), 404
        if board["status"] != "OPEN":
            return jsonify({"error": "Board is already closed."}), 400
        if any(task["board_id"] == board_id and task["status"] != "COMPLETE" for task in tasks.values()):
            return jsonify({"error": "All tasks must be marked as COMPLETE before closing the board."}), 400

        board["status"] = "CLOSED"
        board["end_time"] = datetime.now().isoformat()
        save_data('project_board_base.json', boards)
        return jsonify(board)

    # add task to board
    def add_task(self, request: str) -> str:
        """
        :param request: A json string with the task details. Task is assigned to a user_id who works on the task
        {
            "title" : "<board_name>",
            "description" : "<description>",
            "user_id" : "<user_id>",
            "board_id": "<board_id>"
        }
        :return: A json string with the response {"id" : "<task_id>"}

        Constraint:
         * task title must be unique for a board
         * title name can be max 64 characters
         * description can be max 128 characters

        Constraints:
        * Can only add task to an OPEN board
        """
        global task_counter
        task_base = load_data('task.json')
        boards = load_data('project_board_base.json')
        print(f"boards: {boards}")
        data = request
        title = data.get("title")
        description = data.get("description")
        user_id = data.get("user_id")
        board_id = data.get("board_id")

        if not title or len(title) > 64:
            return jsonify({"error": "Task title is required and must be at most 64 characters."}), 400
        if len(description) > 128:
            return jsonify({"error": "Description must be at most 128 characters."}), 400

        board = boards.get(board_id)
        if not board:
            return jsonify({"error": "Board not found."}), 404
        if board["status"] != "OPEN":
            return jsonify({"error": "Can only add tasks to an OPEN board."}), 400
        if any(task["title"] == title and task["board_id"] == board_id for task in tasks.values()):
            return jsonify({"error": "Task title must be unique for the board."}), 400

        task_id = task_counter
        task_counter += 1
        tasks[task_id] = {
            "id": task_id,
            "title": title,
            "description": description,
            "user_id": user_id,
            "board_id": board_id,
            "creation_time": datetime.now().isoformat(),
            "status": "OPEN"
        }
        save_data('task.json', tasks)
        return jsonify({"id": task_id})

    # update the status of a task
    def update_task_status(self, request: str):
        """
        :param request: A json string with the user details
        {
            "id" : "<task_id>",
            "status" : "OPEN | IN_PROGRESS | COMPLETE"
        }
        """
        tasks = load_data("task.json")
        task_id = request.get("id")
        status = request.get("status")

        if status not in ["OPEN", "IN_PROGRESS", "COMPLETE"]:
            return jsonify({"error": "Invalid status. Must be one of OPEN, IN_PROGRESS, or COMPLETE."}), 400

        task = tasks.get(task_id)
        if not task:
            return jsonify({"error": "Task not found."}), 404

        task["status"] = status
        save_data('task.json', tasks)
        return jsonify(task)

    # list all open boards for a team
    def list_boards(self, request: str) -> str:
        """
        :param request: A json string with the team identifier
        {
          "id" : "<team_id>"
        }

        :return:
        [
          {
            "id" : "<board_id>",
            "name" : "<board_name>"
          }
        ]
        """
        boards = load_data("project_board_base.json")
        team_id = request.get("id")
        team_boards = [
            {"id": board_id, "name": board["name"]}
            for board_id, board in boards.items() if board["team_id"] == team_id and board["status"] == "OPEN"
        ]
        return jsonify(team_boards)

    def export_board(self, request: str) -> str:
        """
        Export a board in the out folder. The output will be a txt file.
        We want you to be creative. Output a presentable view of the board and its tasks with the available data.
        :param request:
        {
          "id" : "<board_id>"
        }
        :return:
        {
          "out_file" : "<name of the file created>"
        }
        """
        boards = load_data('project_board_base.json')
        tasks = load_data('task.json')
        board_id = request.get("id")
        board = boards.get(board_id)
        print(f"available task: {tasks}")
        if not board:
            return jsonify({"error": "Board not found."}), 404

        board_tasks = [
            {
                "id": task_id,
                "title": task["title"],
                "description": task["description"],
                "status": task["status"]
            }
            for task_id, task in tasks.items() if task["board_id"] == board_id
        ]

        output = f"Board: {board['name']}\nDescription: {board['description']}\nStatus: {board['status']}\nTasks:\n"
        for task in board_tasks:
            output += f"- {task['title']} (Status: {task['status']})\n  Description: {task['description']}\n"

        out_file = f"board_{board_id}.txt"
        with open(out_file, "w") as file:
            file.write(output)

        return jsonify({"out_file": out_file})

