from __future__ import annotations

import struct
from dataclasses import dataclass
from enum import IntEnum

from .item import Item
from ...utils.utils import extract_string_from_bytes


class GearType(IntEnum):
    MELEE = 2
    GUN = 3
    HEAD = 4
    CHEST = 5
    LEGS = 6
    ACCESSORIES = 7
    BULLETS = 8


class TargetType(IntEnum):
    SINGLE_ENEMY = 0
    ALL_ENEMIES = 1
    SINGLE_ALLY = 2
    ALL_ALLIES = 3
    YOURSELF = 4
    EVERYONE = 5
    RANDOM_ENEMIES = 6
    SINGLE_ALLY_2 = 7
    ALL_ALLIES_2 = 8
    PHYS = 9


class StatusEffect(IntEnum):
    NONE = 0
    KO = 1
    UNUSED_FORCE = 2
    UNUSED_BRAND = 3
    UNUSED_SMIRK = 4
    POISON = 5
    PANIC = 6
    SLEEP = 7
    BIND = 8
    SICK = 9
    UNUSED_QUESTION_MARK = 10
    UNUSED_SLEEP = 11


class ResistanceLevel(IntEnum):
    NONE = 0
    NULL = 1
    WEAK = 2
    REPEL = 3
    DRAIN = 4
    RESIST = 5


class Element(IntEnum):
    PHYS = 0
    GUN = 1
    FIRE = 2
    ICE = 3
    ELEC = 4
    FORCE = 5
    LIGHT = 6
    DARK = 7
    UNUSED_1 = 8
    UNUSED_2 = 9
    UNUSED_3 = 10
    POISON = 11
    PANIC = 12
    SLEEP = 13
    BIND = 14
    SICK = 15
    LOST = 16
    ALMIGHTY = 17


class WeaponType(IntEnum):
    SWORD = 0
    DAGGER = 1
    SPEAR = 2
    BLUNT = 3
    PISTOL = 7
    BAZOOKA = 8
    RIFLE = 9
    MACHINEGUN = 10
    PLASMA_SWORD = 11
    PLASMA_GUN = 12


@dataclass
class Gear(Item):
    _NAME_LENGTH = 80

    _STRUCT_FORMAT = f"<{_NAME_LENGTH}sH2B2H9B5b3H4B2H36s2H2I2H"
    _STRUCT_LENGTH = struct.calcsize(_STRUCT_FORMAT)

    gear_type: GearType
    purchase_price: int
    sell_price: int
    unknown_1: int
    unknown_2: int
    unknown_3: int
    unknown_4: int
    unknown_5: int
    unknown_6: int
    unknown_7: list[int]
    unknown_8: int
    unknown_9: int
    unknown_10: int

    @classmethod
    def from_bytes(cls, value_bytes: bytes) -> Gear:
        struct_bytes = value_bytes[:cls._STRUCT_LENGTH]

        (
            name_bytes, item_id, gear_type_int, unknown_1, damage, weapon_element_value,
            hit_count_byte, target_type_int, hit_chance, status_effect_int, status_chance,
            unknown_2, unknown_3, unknown_4, unknown_5,
            strength, dexterity, magic, agility, luck, hp, mp, skill_id,
            unknown_6, *unknown_7,
            model_prefix_number, model_number,
            resistances_bytes,
            unknown_8, unknown_9, purchase_price, sell_price, weapon_type_value, unknown_10
        ) = struct.unpack(cls._STRUCT_FORMAT, struct_bytes)

        original_name = name_bytes.decode(encoding="shift-jis")
        name = extract_string_from_bytes(name_bytes)

        gear_type = GearType(gear_type_int)

        weapon_element = Weapon.calculate_weapon_element(weapon_element_value)

        max_hits, min_hits = divmod(hit_count_byte, 16)
        target_type = TargetType(target_type_int)
        status_effect = StatusEffect(status_effect_int)

        resistances = Armor.parse_resistances(resistances_bytes)

        weapon_type = WeaponType(weapon_type_value)

        if gear_type in [GearType.MELEE, GearType.GUN, GearType.BULLETS]:
            return Weapon(item_id, name, original_name, gear_type, purchase_price, sell_price,
                          unknown_1, unknown_2, unknown_3, unknown_4, unknown_5, unknown_6, unknown_7, unknown_8,
                          unknown_9, unknown_10,
                          damage, weapon_element, min_hits, max_hits, target_type, hit_chance, status_effect,
                          status_chance,
                          weapon_type)
        else:
            return Armor(item_id, name, original_name, gear_type, purchase_price, sell_price,
                         unknown_1, unknown_2, unknown_3, unknown_4, unknown_5, unknown_6, unknown_7, unknown_8,
                         unknown_9, unknown_10,
                         strength, dexterity, magic, agility, luck, hp, mp, skill_id,
                         model_prefix_number, model_number,
                         resistances)

    @classmethod
    def from_dict(cls, data: dict) -> Gear:
        gear_type = data["gear_type"]

        if gear_type in [GearType.MELEE, GearType.GUN, GearType.BULLETS]:
            return Weapon.from_dict(data)
        else:
            return Armor.from_dict(data)

    def to_bytes(self) -> bytes:
        pass


@dataclass
class Weapon(Gear):
    damage: int
    element: Element
    min_hits: int
    max_hits: int
    target_type: TargetType
    hit_chance: int
    status_effect: StatusEffect
    status_chance: int
    weapon_type: WeaponType

    def to_bytes(self) -> bytes:
        name_bytes = self.get_name_bytes(self._NAME_LENGTH)

        hit_count_byte = self.hit_count_byte()
        element_value = self.element_value()
        resistance_bytes = b"\x00" * 3

        values = (
            name_bytes, self.item_id, self.gear_type.value, self.unknown_1, self.damage, element_value,
            hit_count_byte, self.target_type.value, self.hit_chance, self.status_effect.value, self.status_chance,
            self.unknown_2, self.unknown_3, self.unknown_4, self.unknown_5,
            0, 0, 0, 0, 0, 0, 0, 0,
            self.unknown_6, *self.unknown_7,
            0, 0, resistance_bytes,
            self.unknown_8, self.unknown_9, self.purchase_price, self.sell_price, self.weapon_type.value,
            self.unknown_10
        )

        return struct.pack(self._STRUCT_FORMAT, *values)

    def hit_count_byte(self) -> int:
        max_hits_nibble = self.max_hits << 4
        min_hits_nibble = self.min_hits

        return max_hits_nibble + min_hits_nibble

    def element_value(self):
        return self.element.value * 16

    @classmethod
    def calculate_weapon_element(cls, weapon_element_value: int) -> Element:
        enum_value = weapon_element_value // 16

        return Element(enum_value)

    @classmethod
    def from_dict(cls, data: dict) -> Weapon:
        item_id = data["item_id"]
        name = data["name"]
        original_name = data["original_name"]

        gear_type = GearType(data["gear_type"])
        purchase_price = data["purchase_price"]
        sell_price = data["sell_price"]

        unknown_1 = data["unknown_1"]
        unknown_2 = data["unknown_2"]
        unknown_3 = data["unknown_3"]
        unknown_4 = data["unknown_4"]
        unknown_5 = data["unknown_5"]
        unknown_6 = data["unknown_6"]
        unknown_7 = data["unknown_7"]
        unknown_8 = data["unknown_8"]
        unknown_9 = data["unknown_9"]
        unknown_10 = data["unknown_10"]

        damage = data["damage"]
        element = Element(data["element"])
        min_hits = data["min_hits"]
        max_hits = data["max_hits"]
        target_type = TargetType(data["target_type"])
        hit_chance = data["hit_chance"]
        status_effect = StatusEffect(data["status_effect"])
        status_chance = data["status_chance"]
        weapon_type = WeaponType(data["weapon_type"])

        return Weapon(item_id, name, original_name, gear_type, purchase_price, sell_price,
                      unknown_1, unknown_2, unknown_3, unknown_4, unknown_5, unknown_6,
                      unknown_7, unknown_8, unknown_9, unknown_10,
                      damage, element, min_hits, max_hits, target_type,
                      hit_chance, status_effect, status_chance, weapon_type)


@dataclass
class Armor(Gear):
    strength: int
    dexterity: int
    magic: int
    agility: int
    luck: int
    hp: int
    mp: int
    skill_id: int
    model_prefix_number: int
    model_number: int
    resistances: list[Resistance]

    def to_bytes(self) -> bytes:
        name_bytes = self.get_name_bytes(self._NAME_LENGTH)

        resistances_bytes = self.resistance_bytes()

        values = (
            name_bytes, self.item_id, self.gear_type.value, self.unknown_1, 0, 0,
            0, 0, 0, 0, 0,
            self.unknown_2, self.unknown_3, self.unknown_4, self.unknown_5,
            self.strength, self.dexterity, self.magic, self.agility, self.luck, self.hp, self.mp, self.skill_id,
            self.unknown_6, *self.unknown_7,
            self.model_prefix_number, self.model_number,
            resistances_bytes,
            self.unknown_8, self.unknown_9, self.purchase_price, self.sell_price, 0,
            self.unknown_10
        )

        return struct.pack(self._STRUCT_FORMAT, *values)

    def resistance_bytes(self) -> bytes:
        resistance_map = {resistance.element.value: resistance for resistance in self.resistances}
        resistances_count = len(Element)

        resistances = []
        for i in range(resistances_count):
            default_resistance = Resistance(Element(i), ResistanceLevel.NONE, 0, 0)
            resistance = resistance_map.get(i, default_resistance)
            resistances.append(resistance)

        resistance_bytes = [resistance.to_bytes() for resistance in resistances]

        return b"".join(resistance_bytes)

    @classmethod
    def parse_resistances(cls, resistances_bytes: bytes) -> list[Resistance]:
        resistance_bytes_length = len(resistances_bytes)
        signed_bytes = struct.unpack(f"{resistance_bytes_length}b", resistances_bytes)
        resistances_count = resistance_bytes_length // 2

        resistances = []
        for i in range(resistances_count):
            offset = i * 2

            element = Element(i)
            modifier = signed_bytes[offset]
            resistance_level_value = signed_bytes[offset + 1]
            resistance_level = Resistance.calculate_resistance(resistance_level_value)

            resistance = Resistance(element, resistance_level, modifier, resistance_level_value)
            resistances.append(resistance)

        return [resistance for resistance in resistances if resistance.resistance_level != ResistanceLevel.NONE]

    @classmethod
    def from_dict(cls, data: dict) -> Armor:
        item_id = data["item_id"]
        name = data["name"]
        original_name = data["original_name"]

        gear_type = GearType(data["gear_type"])
        purchase_price = data["purchase_price"]
        sell_price = data["sell_price"]

        unknown_1 = data["unknown_1"]
        unknown_2 = data["unknown_2"]
        unknown_3 = data["unknown_3"]
        unknown_4 = data["unknown_4"]
        unknown_5 = data["unknown_5"]
        unknown_6 = data["unknown_6"]
        unknown_7 = data["unknown_7"]
        unknown_8 = data["unknown_8"]
        unknown_9 = data["unknown_9"]
        unknown_10 = data["unknown_10"]

        strength = data["strength"]
        dexterity = data["dexterity"]
        magic = data["magic"]
        agility = data["agility"]
        luck = data["luck"]

        hp = data["hp"]
        mp = data["mp"]
        skill_id = data["skill_id"]
        model_prefix_number = data["model_prefix_number"]
        model_number = data["model_number"]

        resistances = [Resistance.from_dict(resistance) for resistance in data["resistances"]]

        return Armor(item_id, name, original_name, gear_type, purchase_price, sell_price,
                     unknown_1, unknown_2, unknown_3, unknown_4, unknown_5, unknown_6,
                     unknown_7, unknown_8, unknown_9, unknown_10,
                     strength, dexterity, magic, agility, luck,
                     hp, mp, skill_id, model_prefix_number, model_number, resistances)


@dataclass
class Resistance:
    _STRUCT_FORMAT = "<bB"

    element: Element
    resistance_level: ResistanceLevel
    modifier: int
    resistance_value: int

    @classmethod
    def calculate_resistance(cls, resistance_value: int) -> ResistanceLevel:
        enum_value = resistance_value // 4

        return ResistanceLevel(enum_value)

    def to_bytes(self) -> bytes:
        return struct.pack(self._STRUCT_FORMAT, self.modifier, self.resistance_value)

    @classmethod
    def from_dict(cls, data: dict) -> Resistance:
        element = Element(data["element"])
        resistance_level = ResistanceLevel(data["resistance_level"])
        modifier = data["modifier"]
        resistance_value = data["resistance_value"]

        return Resistance(element, resistance_level, modifier, resistance_value)
