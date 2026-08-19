from dataclasses import dataclass

from Options import PerGameCommonOptions, Choice, Toggle, OptionGroup


class Route(Choice):
    """
    What route to play.
    """

    display_name = "Route"

    option_neutral = 0
    option_chaos = 1
    option_law = 2
    option_nihilism = 3

    default = option_neutral


class RelicSanity(Toggle):
    """
    Adds relic piles to the list of checks.
    """

    display_name = "Relicsanity"


@dataclass
class SMT4Options(PerGameCommonOptions):
    route: Route
    relic_sanity: RelicSanity


option_groups = [
    OptionGroup(
        "Progression",
        [Route]
    ),
    OptionGroup(
        "Locations",
        [RelicSanity]
    )
]
