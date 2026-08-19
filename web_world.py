from worlds.AutoWorld import WebWorld
from .config import GAME_NAME
from .options import option_groups


class SMT4WebWorld(WebWorld):
    game = GAME_NAME

    theme = "stone"

    option_groups = option_groups
