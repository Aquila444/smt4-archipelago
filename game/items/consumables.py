from __future__ import annotations

import struct
from dataclasses import dataclass
from enum import IntEnum

from .item import Item
from ...utils.utils import extract_string_from_bytes, create_name_entry


class ItemIcon(IntEnum):
    FIRE = 0
    ICE = 1
    ELEC = 2
    FORCE = 3
    ALMIGHTY = 4
    LIGHT = 5
    DARK = 6
    PHYS = 7
    GUN = 8
    STATUS = 9
    HEALING = 10
    SUPPORT = 11
    MISC = 12
    SPEECH_BUBBLE = 13
    QUESTION_MARK = 14
    DELIVERY_ITEM = 15
    SLEEP = 16


class ConsumableTarget(IntEnum):
    SINGLE = 0
    ALL = 1


class ConsumableEffect(IntEnum):
    NONE = 0
    REVIVE = 1
    CURE_ALL = 12
    PATRA = 18
    DISPOISON = 21


@dataclass
class Consumable(Item):
    _NAME_LENGTH = 80
    _CATEGORY_LENGTH = 16

    _STRUCT_FORMAT = f"<{_NAME_LENGTH}s{_CATEGORY_LENGTH}s4H10B2x2H2I"
    _STRUCT_LENGTH = struct.calcsize(_STRUCT_FORMAT)

    category: str
    flat_hp_recovery: int
    percentage_hp_recovery: int
    flat_mp_recovery: int
    percentage_mp_recovery: int
    stack_size: int
    purchase_price: int
    sell_price: int
    skill_id: int
    xp_gain_percentage: int
    app_point_gain: int
    item_icon: ItemIcon
    sort_order: int
    target: ConsumableTarget
    effect: ConsumableEffect
    unknown_1: bytes
    unknown_2: bytes
    unknown_3: bytes
    unknown_4: bytes

    @classmethod
    def from_bytes(cls, value_bytes: bytes) -> Consumable:
        struct_bytes = value_bytes[:cls._STRUCT_LENGTH]

        (
            name_bytes, category_bytes, item_id, skill_id, flat_hp_recovery, flat_mp_recovery,
            percentage_hp_recovery, percentage_mp_recovery,
            effect_byte, unknown_1, item_icon_value, unknown_2, unknown_3, sort_order, unknown_4,
            stack_size, xp_gain_percentage, app_point_gain, purchase_price, sell_price
        ) = struct.unpack(Consumable._STRUCT_FORMAT, struct_bytes)

        name = extract_string_from_bytes(name_bytes)
        category = extract_string_from_bytes(category_bytes)

        item_icon = ItemIcon(item_icon_value)
        target, effect = cls.parse_effect_byte(effect_byte)

        return Consumable(item_id, name, name_bytes, category,
                          flat_hp_recovery, percentage_hp_recovery, flat_mp_recovery, percentage_mp_recovery,
                          stack_size, purchase_price, sell_price, skill_id,
                          xp_gain_percentage, app_point_gain, item_icon, sort_order, target, effect,
                          unknown_1, unknown_2, unknown_3, unknown_4)

    def to_bytes(self) -> bytes:
        name_bytes = self.get_name_bytes(self._NAME_LENGTH)
        category_bytes = create_name_entry(self.category, self._CATEGORY_LENGTH)
        effect_byte = self.effect_byte()

        values = (
            name_bytes, category_bytes, self.item_id, self.skill_id, self.flat_hp_recovery, self.flat_mp_recovery,
            self.percentage_hp_recovery, self.percentage_mp_recovery,
            effect_byte, self.unknown_1, self.item_icon.value, self.unknown_2, self.unknown_3, self.sort_order,
            self.unknown_4,
            self.stack_size, self.xp_gain_percentage, self.app_point_gain, self.purchase_price, self.sell_price
        )

        return struct.pack(self._STRUCT_FORMAT, *values)

    @classmethod
    def parse_effect_byte(cls, effect_value: int):
        effect_byte = effect_value.to_bytes(1, byteorder="little")
        bitmap = [(b >> shift) & 1 for b in effect_byte for shift in range(7, -1, -1)]

        target = ConsumableTarget(bitmap[0])

        effect_value_stripped = effect_value & 127
        effect = ConsumableEffect(effect_value_stripped)

        return target, effect

    def effect_byte(self) -> int:
        target_bit = self.target.value
        effect_value = self.effect.value

        return effect_value + 128 * target_bit
