import os

from BaseClasses import Item
from worlds.AutoWorld import World
from . import items, regions, locations, web_world, smt4_settings
from . import options as smt4_options
from .config import GAME_NAME
from .smt4_patch import SMT4PatchInfo, SMT4Patch, patch_data_file_name


class SMT4World(World):
    """
    Shin Megami Tensei 4 is a JRPG released for the 3DS by Atlus in 2013.
    Fight, recruit and fuse demons to create your ideal world of chaos, law or balance!
    """

    game = GAME_NAME

    web = web_world.SMT4WebWorld()

    settings = smt4_settings.SMT4Settings
    settings_key = smt4_settings.settings_key

    options_dataclass = smt4_options.SMT4Options
    options: smt4_options.SMT4Options

    location_name_to_id = locations.location_name_to_id
    item_name_to_id = items.item_name_to_id

    origin_region_name = "Mikado"

    def create_regions(self) -> None:
        regions.create_and_connect_regions(self)
        locations.create_all_locations(self)

    def set_rules(self) -> None:
        pass

    def create_items(self) -> None:
        items.create_all_items(self)

    def create_item(self, name: str) -> Item:
        return items.create_item_with_correct_classification(self, name)

    def get_filler_item_name(self) -> str:
        return items.get_random_filler_item_name(self)

    def generate_output(self, output_directory: str) -> None:
        locations_to_items = {
            location.name: location.item.name if location.item.player == self.player
            else "AP Item" for location in self.get_locations()
        }

        seed = str(self.multiworld.seed)

        patch_info = SMT4PatchInfo(seed, locations_to_items)
        patch = SMT4Patch(player=self.player, player_name=self.player_name)
        patch.write_file(patch_data_file_name, patch_info.to_json())

        out_file_name = self.multiworld.get_out_file_name_base(self.player)
        patch.write(os.path.join(output_directory, f"{out_file_name}{patch.patch_file_ending}"))
