# TODO: Accept Challenge menu
# TODO: Check for correct user to make the input
# TODO: Timestamp when game started
# TODO: Cancel game after 5 minutes of no input
# TODO: Takeback
# TODO: early Draw, because of impossible winner
# TODO: Database
# TODO: Elo System
# TODO: AI


import random
# import time

import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands


COLOR_BLUE = (88, 172, 236)
COLOR_RED = (224, 44, 68)
COLOR_BLACK = (0, 0, 0)


async def add_genitiv(name):
    if name.endswith("s"):
        new_name = f"{name}'"
    else:
        new_name = f"{name}'s"
    return new_name

async def tuple_to_discord_color(t):
    return discord.Color.from_rgb(*t)

async def get_location_id(interaction):
    location_id = f"{interaction.guild_id}-{interaction.channel_id}"
    return location_id


class Connect4Game:

    def __init__(self):
        pass

    async def setup_game(self, interaction, opponent):
        location_id = await get_location_id(interaction)
        await self.add_game_to_games_list(location_id)
        await self.add_players(location_id, interaction, opponent)
        await self.give_players_colors(location_id)
        await self.create_empty_game(location_id)
        await self.add_empty_button_counter(location_id)
        await self.choose_beginner(location_id)

    @staticmethod
    async def add_game_to_games_list(location_id):
        Connect4.current_locations[location_id] = {}

    @staticmethod
    async def add_players(location_id, interaction, opponent):
        player0 = {"player": interaction.user, "player_name": interaction.user.name,
                   "player_name_genitiv": await add_genitiv(interaction.user.name),
                   "number": 0, "color": "", "color_name": ""}
        player1 = {"player": opponent, "player_name": opponent.name,
                   "player_name_genitiv": await add_genitiv(opponent.name),
                   "number": 1, "color": "", "color_name": ""}
        Connect4.current_locations[location_id]["player0"] = player0
        Connect4.current_locations[location_id]["player1"] = player1

    @staticmethod
    async def give_players_colors(location_id):
        Connect4.current_locations[location_id]["player0"]["color"] = COLOR_RED
        Connect4.current_locations[location_id]["player0"]["color_name"] = "red"
        Connect4.current_locations[location_id]["player1"]["color"] = COLOR_BLUE
        Connect4.current_locations[location_id]["player1"]["color_name"] = "blue"

    @staticmethod
    async def create_empty_game(location_id):
        empty_game_list = [
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None]
        ]
        Connect4.current_locations[location_id]["game"] = empty_game_list

    @staticmethod
    async def add_empty_button_counter(location_id):
        if Connect4.current_locations[location_id].get("button_counter") is None:
            Connect4.current_locations[location_id]["button_counter"] = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0}

    @staticmethod
    async def choose_beginner(location_id):
        Connect4.current_locations[location_id]["turn"] = random.randint(0, 1)

    async def click_piece_button(self, interaction, button):
        location_id = await get_location_id(interaction)
        user_check = await self.check_for_correct_user(interaction, location_id)
        if user_check is not None:
            return await interaction.response.send_message(user_check, ephemeral=True)
        await interaction.response.defer(ephemeral=True, thinking=False)
        column = int(button.label)
        await self.add_column_height(location_id, column)
        await self.check_for_full_column(location_id, interaction, button, column)
        await self.insert_piece(self, location_id, column)
        result = await self.check_result(self, location_id, interaction)
        if result is True:
            return
        await self.switch_turn(location_id, interaction)

    @staticmethod
    async def check_for_correct_user(interaction, location_id):
        if interaction.guild_id == 1060143808622370826 and interaction.channel_id == 1060145297252163705:
            return  # Test Server
        players = [Connect4.current_locations[location_id]["player0"]["player"],
                   Connect4.current_locations[location_id]["player1"]["player"]]
        turn = Connect4.current_locations[location_id]["turn"]
        if players[turn] == interaction.user:
            return
        elif interaction.user in players and interaction.user != players[turn]:
            return "It's not your turn!"
        elif interaction.user not in players:
            return "You cant participate in that game! Either start the next on or wait until somebody challanges you!"

    @staticmethod
    async def switch_turn(location_id, interaction):
        current_turn = Connect4.current_locations[location_id]["turn"]
        if current_turn == 0:
            Connect4.current_locations[location_id]["turn"] = 1
        elif current_turn == 1:
            Connect4.current_locations[location_id]["turn"] = 0
        turn = Connect4.current_locations[location_id]["turn"]
        players = [Connect4.current_locations[location_id]["player0"], Connect4.current_locations[location_id]["player1"]]
        embed = interaction.message.embeds[0]
        embed.color = await tuple_to_discord_color(Connect4.current_locations[location_id][f"player{turn}"]["color"])
        embed.remove_field(index=0)
        embed.insert_field_at(index=0,
                              name=f":{players[turn]['color_name']}_circle: {players[turn]['player_name_genitiv']} turn!\n\n:one::two::three::four::five::six::seven:",
                              value=await Connect4.convert_game_to_text(Connect4, location_id),
                              inline=True)
        await interaction.message.edit(embed=embed)

    @staticmethod
    async def add_column_height(location_id, column):
        Connect4.current_locations[location_id]["button_counter"][str(column)] += 1

    @staticmethod
    async def check_for_full_column(location_id, interaction, button, column):
        if button.disabled is True:
            return
        if Connect4.current_locations[location_id]["button_counter"][str(column)] == 6:
            button.disabled = True
            await interaction.message.edit(view=Connect4.current_locations[location_id]["menu"])

    @staticmethod
    async def convert_coordinates_to_position_in_list(x, y):
        x_position = x - 1
        y_conversions = {1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 0}
        y_position = y_conversions.get(y)
        return {"x": x_position, "y": y_position}

    async def insert_piece(self, location_id, column):
        game = Connect4.current_locations[location_id]["game"]
        turn = Connect4.current_locations[location_id]["turn"]
        x = column
        y = Connect4.current_locations[location_id]["button_counter"][str(column)]
        positions = await self.convert_coordinates_to_position_in_list(x, y)
        x_position = positions["x"]
        y_position = positions["y"]
        game[y_position][x_position] = turn

    @staticmethod
    async def check_horizontal_win(board):
        indexes = []
        for row in range(6):
            for value in range(4):
                if board[row][value] is not None and board[row][value] == board[row][value + 1] == board[row][value + 2] == board[row][value + 3]:
                    indexes.append({"y": row, "x": value})
                    indexes.append({"y": row, "x": value + 1})
                    indexes.append({"y": row, "x": value + 2})
                    indexes.append({"y": row, "x": value + 3})
        return indexes

    @staticmethod
    async def check_vertical_win(board):
        indexes = []
        for row in range(3):
            for value in range(7):
                if board[row][value] is not None and board[row][value] == board[row + 1][value] == board[row + 2][value] == board[row + 3][value]:
                    indexes.append({"y": row, "x": value})
                    indexes.append({"y": row + 1, "x": value})
                    indexes.append({"y": row + 2, "x": value})
                    indexes.append({"y": row + 3, "x": value})
        return indexes

    @staticmethod
    async def check_diagonal_win(board):
        indexes = []
        for row in range(6):
            for value in range(7):
                if board[row][value] is not None and (row > 2 and value > 2) and (
                        board[row][value] == board[row - 1][value - 1] == board[row - 2][value - 2] == board[row - 3][value - 3]):
                    indexes.append({"y": row, "x": value})
                    indexes.append({"y": row - 1, "x": value - 1})
                    indexes.append({"y": row - 2, "x": value - 2})
                    indexes.append({"y": row - 3, "x": value - 3})
                if board[row][value] is not None and (row < 3 and value > 2) and (
                        board[row][value] == board[row + 1][value - 1] == board[row + 2][value - 2] == board[row + 3][value - 3]):
                    indexes.append({"y": row, "x": value})
                    indexes.append({"y": row + 1, "x": value - 1})
                    indexes.append({"y": row + 2, "x": value - 2})
                    indexes.append({"y": row + 3, "x": value - 3})
        return indexes

    @staticmethod
    async def check_for_draw(location_id):
        button_counter = Connect4.current_locations[location_id]["button_counter"]
        return all(value == 6 for value in button_counter.values())

    @staticmethod
    async def determine_winner(location_id, winning_pieces, board):
        winner_number_index = winning_pieces[0][0]
        winner_number = board[int(winner_number_index["y"])][int(winner_number_index["x"])]
        winner = Connect4.current_locations[location_id][f"player{str(winner_number)}"]
        return winner

    async def check_result(self, location_id, interaction):
        board = Connect4.current_locations[location_id]["game"]
        winning_pieces = []
        horizontal_check = await self.check_horizontal_win(board)
        vertical_check = await self.check_vertical_win(board)
        diagonal_check = await self.check_diagonal_win(board)
        checks = [horizontal_check, vertical_check, diagonal_check]
        check_draw = await self.check_for_draw(location_id)
        for check in checks:
            if len(check) != 0:
                winning_pieces.append(check)
        if len(winning_pieces) == 0 and check_draw is False:
            return False
        if check_draw is False:
            winner = await self.determine_winner(location_id, winning_pieces, board)
        elif check_draw is True:
            winner = "draw"
        await self.end_game(self, location_id, interaction, winner, winning_pieces)
        return True

    async def end_game(self, location_id, interaction, winner, winning_pieces=None):
        await self.edit_board_to_finished(location_id, winner, winning_pieces, interaction)
        await self.disable_game(location_id, interaction)
        await self.remove_game_from_current_games(location_id)
        # add board to DB TODO
        # change elo TODO

    @staticmethod
    async def edit_board_to_finished(location_id, winner, winning_pieces, interaction):
        if winner == "draw":
            title = f"The game ended in a draw!\n\n:one::two::three::four::five::six::seven:"
        else:
            if winning_pieces is not None:
                board = Connect4.current_locations[location_id]["game"]
                for winning_line in winning_pieces:
                    for winning_piece in winning_line:
                        winning_piece_x = winning_piece["x"]
                        winning_piece_y = winning_piece["y"]
                        board[winning_piece_y][winning_piece_x] = f"{str(winner['number'])}x"
                Connect4.current_locations[location_id]["game"] = board
            title = f":{winner['color_name']}_circle: {winner['player_name']} won!\n\n:one::two::three::four::five::six::seven:"
        embed = interaction.message.embeds[0]
        if winner == "draw":
            embed.color = await tuple_to_discord_color(COLOR_BLACK)
        else:
            embed.color = await tuple_to_discord_color(winner["color"])
        embed.remove_field(index=0)
        embed.insert_field_at(index=0,
                              name=title,
                              value=await Connect4.convert_game_to_text(Connect4, location_id),
                              inline=True)
        await interaction.message.edit(embed=embed)

    @staticmethod
    async def disable_game(location_id, interaction):
        instance = Connect4.current_locations[location_id]["menu"]
        await Connect4Menu.disable_all_buttons(instance, interaction)

    @staticmethod
    async def remove_game_from_current_games(location_id):
        del Connect4.current_locations[location_id]


class Connect4Menu(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    async def disable_all_buttons(self, interaction):
        for button in self.children:
            button.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="2", style=discord.ButtonStyle.blurple)
    async def button_two(self, interaction: discord.Interaction, button: discord.ui.Button):
        await Connect4Game.click_piece_button(Connect4Game, interaction, button)

    @discord.ui.button(label="3", style=discord.ButtonStyle.blurple)
    async def button_three(self, interaction: discord.Interaction, button: discord.ui.Button):
        await Connect4Game.click_piece_button(Connect4Game, interaction, button)

    @discord.ui.button(label="4", style=discord.ButtonStyle.blurple)
    async def button_four(self, interaction: discord.Interaction, button: discord.ui.Button):
        await Connect4Game.click_piece_button(Connect4Game, interaction, button)

    @discord.ui.button(label="5", style=discord.ButtonStyle.blurple)
    async def button_five(self, interaction: discord.Interaction, button: discord.ui.Button):
        await Connect4Game.click_piece_button(Connect4Game, interaction, button)

    @discord.ui.button(label="6", style=discord.ButtonStyle.blurple)
    async def button_six(self, interaction: discord.Interaction, button: discord.ui.Button):
        await Connect4Game.click_piece_button(Connect4Game, interaction, button)

    @discord.ui.button(label="1", style=discord.ButtonStyle.blurple, disabled=False)
    async def button_one(self, interaction: discord.Interaction, button: discord.ui.Button):
        await Connect4Game.click_piece_button(Connect4Game, interaction, button)

    @discord.ui.button(label=" ", disabled=True)
    async def button_disabled1(self, interaction: discord.Interaction, button: discord.ui.Button, style=discord.ButtonStyle.gray):
        pass

    @discord.ui.button(label=" ", disabled=True)
    async def button_disabled2(self, interaction: discord.Interaction, button: discord.ui.Button, style=discord.ButtonStyle.gray):
        pass

    @discord.ui.button(label=" ", disabled=True)
    async def button_disabled3(self, interaction: discord.Interaction, button: discord.ui.Button, style=discord.ButtonStyle.gray):
        pass

    @discord.ui.button(label="7", style=discord.ButtonStyle.blurple)
    async def button_seven(self, interaction: discord.Interaction, button: discord.ui.Button):
        await Connect4Game.click_piece_button(Connect4Game, interaction, button)

    @discord.ui.button(label="Resign", style=discord.ButtonStyle.red, emoji="🏳️")
    async def button_resign(self, interaction: discord.Interaction, button: discord.ui.Button):
        location_id = await get_location_id(interaction)
        if interaction.user == Connect4.current_locations[location_id][f"player{Connect4.current_locations[location_id]['turn']}"]["player"]:
            await Connect4Game.switch_turn(location_id, interaction)
        await Connect4Game.end_game(Connect4Game, location_id, interaction, Connect4.current_locations[location_id][f"player{Connect4.current_locations[location_id]['turn']}"])
        await interaction.response.defer(ephemeral=True, thinking=False)  # TODO correct person must be winner

    @discord.ui.button(label="Offer Draw", style=discord.ButtonStyle.red, emoji="🤝")
    async def button_draw(self, interaction: discord.Interaction, button: discord.ui.Button):
        location_id = await get_location_id(interaction)
        await Connect4Game.end_game(Connect4Game, location_id, interaction, "draw")
        await interaction.response.defer(ephemeral=True, thinking=False)  # TODO Draw Menu

    # @discord.ui.button(label="Request takeback", style=discord.ButtonStyle.green, emoji="↩")
    # async def button_takeback(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     await interaction.response.send_message("Takeback", view=TakebackMenu())  # TODO



class TakebackMenu(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, emoji="✅")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Accept")

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red, emoji="✖️")
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Decline")


class AcceptChallengeMenu(discord.ui.View):

    original_interactions = {}

    def __init__(self):
        super().__init__()
        self.value = None

    @staticmethod
    async def create_connect4_embed(location_id):
        turn = Connect4.current_locations[location_id]["turn"]
        players = [Connect4.current_locations[location_id]["player0"], Connect4.current_locations[location_id]["player1"]]
        embed = discord.Embed(
            color=await tuple_to_discord_color(Connect4.current_locations[location_id][f"player{str(turn)}"]["color"]),
            title="Connect 4!")
        embed.add_field(
            name=f":{players[turn]['color_name']}_circle: {players[turn]['player_name_genitiv']} turn!\n\n:one::two::three::four::five::six::seven:",
            value=await Connect4.convert_game_to_text(Connect4, location_id), inline=True)
        embed.add_field(name="Players:",
                        value=f"{players[0]['player_name']} [{''}]\n{players[1]['player_name']} [{''}]",
                        inline=True)
        return embed

    async def check_opponent(self, location_id, interaction):
        if interaction.user != self.original_interactions[location_id]["opponent"]:
            return await interaction.response.send_message("You are not the challenged person!")

    async def check_for_same_players(self, location_id, interaction):
        if interaction.user == self.original_interactions[location_id]["interaction"].user:
            await interaction.response.defer(ephemeral=True)
            return False

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, emoji="✅")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        location_id = await get_location_id(interaction)
        same_player_check = await self.check_for_same_players(location_id, interaction)
        if same_player_check is False:
            return
        if self.original_interactions[location_id]["opponent"] is not None:
            opponent_check = await self.check_opponent(location_id, interaction)
            if opponent_check is not None:
                return await interaction.response.send_message(opponent_check)
        await Connect4Game.setup_game(Connect4Game, self.original_interactions[location_id]["interaction"], interaction.user)
        instance = Connect4Menu()
        await interaction.response.send_message(embed=await self.create_connect4_embed(location_id), view=instance)
        Connect4.current_locations[location_id]["menu"] = instance

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red, emoji="✖️")
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()


class Connect4(commands.Cog):

    current_locations = {}
    # location_id: {player0: {"player": interaction.user, "player_name": interaction.user.name,
    #                         "player_name_genitiv": await StaticMethods.add_genitiv(interaction.user.name),
    #                         "color": COLOR_BLUE/COLOR_RED, "color_name": "red"},
    #               player1: {...},
    #               turn: 0/1,
    #               game: [[None, None, None, None, None, None, None], [None, None, ...], ...],
    #               button_counter: {"1": 0, "2": 0, ...}


    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def check_for_correct_location(self, location_id):
        if location_id in self.current_locations.keys():
            return "There cant be 2 games in the same channel! Switch to an other channel or wait until the game is finished!"
        return None

    @staticmethod
    async def check_for_correct_parameters(opponent, ai):
        if opponent is not None and ai is not None:
            return "You have to at least select either an opponent or a AI!"
        if opponent is not None and ai is not None:
            return "You cant select 2 opponents at the same time! Please select only one"
        return None

    @staticmethod
    async def check_for_correct_opponent(challenger, opponent):
        if challenger.id == opponent.id:
            return "You cant play yourself!"
        # if opponent.bot is True:
        #     return "You cant play a bot, but you can play an AI!"  # TODO when finsihed
        return None

    async def convert_game_to_text(self, location_id):
        game = self.current_locations[location_id]["game"]
        game_str = ""
        for row in game:
            for spot in row:
                if spot is None:  # no piece yet
                    game_str = f"{game_str}⚫"
                elif spot == 0:  # player0's piece
                    game_str = f"{game_str}🔴"
                elif spot == 1:  # player1's piece
                    game_str = f"{game_str}🔵"
                elif spot == "0x":  # player0's winning piece
                    game_str = f"{game_str}❌"
                elif spot == "1x":  # player1's winning piece
                    game_str = f"{game_str}<:blue_x:1067109146807242773>"
            game_str = f"{game_str}\n"
        return game_str


    @app_commands.command(name="connect4", description="Play connect4 either against a friend or an AI with different strength")
    @app_commands.describe(opponent="Select the friend you want to play with (you cant select AI too)", ai="Select the AI you want to play against (You cant select opponent too)")
    @app_commands.choices(
        rated=[
            Choice(name="rated", value="rated"),
            Choice(name="not rated", value="not_rated")
        ],
        ai=[
            Choice(name="Level 1 - Weak", value=1),
            Choice(name="Level 2 - Medium", value=2),
            Choice(name="Level 3 - Strong", value=3)
        ]
    )
    async def connect4(self, interaction: discord.Interaction, rated: Choice[str], opponent: discord.Member = None, ai: Choice[int] = None):
        location_id = await get_location_id(interaction)
        location_check = await self.check_for_correct_location(location_id)
        view = AcceptChallengeMenu()
        if location_check is not None:
            return await interaction.response.send_message(location_check, ephemeral=True)
        parameter_check = await self.check_for_correct_parameters(opponent, ai)
        if parameter_check is not None:
            return await interaction.response.send_message(parameter_check, ephemeral=True)
        if opponent is not None:
            opponent_check = await self.check_for_correct_opponent(interaction.user, opponent)
            if opponent_check is not None:
                return await interaction.response.send_message(opponent_check, ephemeral=True)
            challenge_embed_title = f"{opponent.mention}, {interaction.user.display_name} sent you a challenge!"
        elif ai is not None:
            return await interaction.response.send_message("Feature not finished yet", ephemeral=True)  # TODO
        elif opponent is None and ai is None:
            challenge_embed_title = f"{interaction.user.display_name} sent a challenge! First one to accept is the opponent"
            view.remove_item("Decline")
        AcceptChallengeMenu.original_interactions[location_id] = {"interaction": interaction, "opponent": opponent}
        await interaction.response.send_message(challenge_embed_title, view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        Connect4(bot)
    )
