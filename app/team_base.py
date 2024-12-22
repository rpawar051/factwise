from flask import Flask, request, jsonify
from datetime import datetime
from app.records import load_data, save_data


# In-memory storage for simplicity
teams = {}
users = {}
team_users = {}
team_counter = 1

# Helper functions
def generate_id(data_store):
    return str(len(data_store) + 1)

class TeamBase:
    """
    Base interface implementation for API's to manage teams.
    For simplicity a single team manages a single project. And there is a separate team per project.
    Users can be
    """

    # create a team
    def create_team(self, request: str) -> str:
        """
        :param request: A json string with the team details
        {
          "name" : "<team_name>",
          "description" : "<some description>",
          "admin": "<id of a user>"
        }
        :return: A json string with the response {"id" : "<team_id>"}

        Constraint:
            * Team name must be unique
            * Name can be max 64 characters
            * Description can be max 128 characters
        """
        
        global team_counter
        team_data = load_data('team_base.json')
        data = request
        name = data.get("name")
        description = data.get("description")
        admin = data.get("admin")

        if not name or len(name) > 64:
            return jsonify({"error": "Team name is required and must be at most 64 characters."}), 400
        if len(description) > 128:
            return jsonify({"error": "Description must be at most 128 characters."}), 400
        if name in [team["name"] for team in teams.values()]:
            return jsonify({"error": "Team name must be unique."}), 400

        team_id = team_counter
        team_counter += 1
        teams[team_id] = {
            "id": team_id,
            "name": name,
            "description": description,
            "creation_time": datetime.now().isoformat(),
            "admin": admin
        }
        # team_users = load_data('team_users.json')
        team_users[team_id] = [admin]
        save_data("team_users.json", team_users)
        save_data('team_base.json', teams)
        return jsonify({"id": team_id})

    # list all teams
    def list_teams(self) -> str:
        """
        :return: A json list with the response.
        [
          {
            "name" : "<team_name>",
            "description" : "<some description>",
            "creation_time" : "<some date:time format>",
            "admin": "<id of a user>"
          }
        ]
        """
        data = load_data('team_base.json')
        # return jsonify(list(teams.values()))
        return jsonify(data)

    # describe team
    def describe_team(self, request: str) -> str:
        """
        :param request: A json string with the team details
        {
          "id" : "<team_id>"
        }

        :return: A json string with the response

        {
          "name" : "<team_name>",
          "description" : "<some description>",
          "creation_time" : "<some date:time format>",
          "admin": "<id of a user>"
        }

        """
        teams = load_data('team_base.json')
        print(f"teams: {teams}")

        team_id = request.get("id")
        team = teams.get(team_id)
        if not team:
            return jsonify({"error": "Team not found."}), 404
        return jsonify(team)

    # update team
    def update_team(self, request: str) -> str:
        """
        :param request: A json string with the team details
        {
          "id" : "<team_id>",
          "team" : {
            "name" : "<team_name>",
            "description" : "<team_description>",
            "admin": "<id of a user>"
          }
        }

        :return:

        Constraint:
            * Team name must be unique
            * Name can be max 64 characters
            * Description can be max 128 characters
        """
        data = request
        teams = load_data('team_base.json')
        team_id = data.get("id")
        team_updates = data.get("team")

        if not team_id or team_id not in teams:
            return jsonify({"error": "Team not found."}), 404

        if "name" in team_updates and len(team_updates["name"]) > 64:
            return jsonify({"error": "Team name must be at most 64 characters."}), 400
        if "description" in team_updates and len(team_updates["description"]) > 128:
            return jsonify({"error": "Description must be at most 128 characters."}), 400

        teams[team_id].update(team_updates)
        save_data('team_base.json', teams)
        return jsonify(teams[team_id])

    # add users to team
    def add_users_to_team(self, request: str):
        """
        :param request: A json string with the team details
        {
          "id" : "<team_id>",
          "users" : ["user_id 1", "user_id2"]
        }

        :return:

        Constraint:
        * Cap the max users that can be added to 50
        """
        teams = load_data('team_base.json')
        print(f"Teams records: {teams}")
        team_id = request.get("id")
        new_users = request.get("users")
        print(f"team_id: {team_id}")
        if not team_id or team_id not in teams:
            return jsonify({"error": "Team not found."}), 404
        if len(new_users) > 50:
            return jsonify({"error": "Cannot add more than 50 users at once."}), 400

        team_users = load_data("team_users.json")
        team_users[team_id].extend(new_users)
        team_users[team_id] = list(set(team_users[team_id]))  # Remove duplicates
        save_data('team_users.json', team_users)
        return jsonify({"users": team_users[team_id]})

    # remove users to team
    def remove_users_from_team(self, request: str):
        """
        :param request: A json string with the team details
        {
          "id" : "<team_id>",
          "users" : ["user_id 1", "user_id2"]
        }

        :return:

        Constraint:
        * Cap the max users that can be added to 50
        """
        team_users = load_data('team_users.json')
        teams = load_data('team_base.json')
        print(f"Teams records: {teams}")
        team_id = request.get("id")
        remove_users = request.get("users")

        if not team_id or team_id not in teams:
            return jsonify({"error": "Team not found."}), 404
        if len(remove_users) > 50:
            return jsonify({"error": "Cannot remove more than 50 users at once."}), 400

        team_users[team_id] = [user for user in team_users[team_id] if user not in remove_users]
        save_data('team_users.json', team_users)
        return jsonify({"users": team_users[team_id]})

    # list users of a team
    def list_team_users(self, request: str):
        """
        :param request: A json string with the team identifier
        {
          "id" : "<team_id>"
        }

        :return:
        [
          {
            "id" : "<user_id>",
            "name" : "<user_name>",
            "display_name" : "<display name>"
          }
        ]
        """
        team_users = load_data('team_users.json')
        teams = load_data('team_base.json')
        print(f"Teams records: {teams}")
        users = load_data("user_base.json")
        print(f"User data: {users}")
        team_id = request.get("id")

        if not team_id or team_id not in teams:
            return jsonify({"error": "Team not found."}), 404

        user_list = [
            {"id": user_id, "name": users[user_id]["name"], "display_name": users[user_id]["display_name"]}
            for user_id in team_users[team_id]
        ]
        return jsonify(user_list)


