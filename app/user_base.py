from app.records import load_data, save_data
from flask import Flask, request, jsonify
from datetime import datetime

# In-memory storage for simplicity
teams = {}
users = {}
team_users = {}
team_counter = 1
user_counter = 1

class UserBase:
    """
    Base interface implementation for API's to manage users.
    """

    # create a user
    def create_user(self, request: str) -> str:
        """
        :param request: A json string with the user details
        {
          "name" : "<user_name>",
          "display_name" : "<display name>"
        }
        :return: A json string with the response {"id" : "<user_id>"}

        Constraint:
            * user name must be unique
            * name can be max 64 characters
            * display name can be max 64 characters
        """
        global user_counter
        user_data = load_data('user_base.json')
        data = request
        name = data.get("name")
        display_name = data.get("display_name")

        if not name or len(name) > 64:
            return jsonify({"error": "User name is required and must be at most 64 characters."}), 400
        if len(display_name) > 64:
            return jsonify({"error": "Display name must be at most 64 characters."}), 400
        if name in [user["name"] for user in users.values()]:
            return jsonify({"error": "User name must be unique."}), 400

        user_id = user_counter
        user_counter += 1
        users[user_id] = {
            "id": user_id,
            "name": name,
            "display_name": display_name,
            "creation_time": datetime.now().isoformat()
        }
        save_data('user_base.json', users)
        return jsonify({"id": user_id})


    # list all users
    def list_users(self) -> str:
        """
        :return: A json list with the response
        [
          {
            "name" : "<user_name>",
            "display_name" : "<display name>",
            "creation_time" : "<some date:time format>"
          }
        ]
        """
        user_base = load_data('user_base.json')
        return jsonify(user_base)

    # describe user
    def describe_user(self, request: str) -> str:
        """
        :param request: A json string with the user details
        {
          "id" : "<user_id>"
        }

        :return: A json string with the response

        {
          "name" : "<user_name>",
          "description" : "<some description>",
          "creation_time" : "<some date:time format>"
        }

        """
        users = load_data('user_base.json')
        user_id = request.get("id")
        user = users.get(user_id)
        if not user:
            return jsonify({"error": "User not found."}), 404
        return jsonify(user)

    # update user
    def update_user(self, request: str) -> str:
        """
        :param request: A json string with the user details
        {
          "id" : "<user_id>",
          "user" : {
            "name" : "<user_name>",
            "display_name" : "<display name>"
          }
        }

        :return:

        Constraint:
            * user name cannot be updated
            * name can be max 64 characters
            * display name can be max 128 characters
        """
        users = load_data('user_base.json')
        data = request
        print(f"input data {data}")
        user_id = data.get("id")
        user_updates = data.get("user")

        if not user_id or user_id not in users:
            return jsonify({"error": "User not found."}), 404

        if "name" in user_updates:
            return jsonify({"error": "User name cannot be updated."}), 400
        if "display_name" in user_updates and len(user_updates["display_name"]) > 128:
            return jsonify({"error": "Display name must be at most 128 characters."}), 400

        users[user_id].update(user_updates)
        save_data("user_base.json", users)
        return jsonify(users[user_id])

    def get_user_teams(self, request: str) -> str:
        """
        :param request:
        {
          "id" : "<user_id>"
        }

        :return: A json list with the response.
        [
          {
            "name" : "<team_name>",
            "description" : "<some description>",
            "creation_time" : "<some date:time format>"
          }
        ]
        """
        users = load_data('user_base.json')
        teams = load_data('team_base.json')
        user_id = request.get("id")
        team_users = load_data('team_users.json')
        if not user_id or user_id not in users:
            return jsonify({"error": "User not found."}), 404

        print(f"team_users : {team_users}\n users: {users}\n teams: {teams} ")
        user_teams = [
            {
                "name": teams[team_id]["name"],
                "description": teams[team_id]["description"],
                "creation_time": teams[team_id]["creation_time"]
            }
            for team_id, members in team_users.items() if user_id in members
        ]
        return jsonify(user_teams)

