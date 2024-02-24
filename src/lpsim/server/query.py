import shlex
from typing import Any, List

from .consts import ObjectPositionType, ObjectType


def _query(object_position: Any, match: Any, command: List[str]) -> List[Any]:
    """
    Function to deal with a query. `and` should not contain in command when calling,
    split it before calling this function.
    """
    assert len(command) > 0, "command is empty"
    current_objs = []
    if command[0] == "self":
        assert object_position.area in [
            ObjectPositionType.CHARACTER,
            ObjectPositionType.CHARACTER_STATUS,
            ObjectPositionType.SKILL,
        ], "self can only be used for objects in character skill or character_status"
        current_objs = [
            match.player_tables[object_position.player_idx].characters[
                object_position.character_idx
            ]
        ]
    elif command[0] == "both":
        current_objs = [match.player_tables[0], match.player_tables[1]]
    elif command[0] == "our":
        current_objs = [match.player_tables[object_position.player_idx]]
    elif command[0] == "opponent":
        current_objs = [match.player_tables[1 - object_position.player_idx]]
    else:
        raise ValueError(
            f"first token must be both, our, opponent, or self. input is {command[0]}"
        )
    for cmd in command[1:]:
        if cmd in [
            "active",
            "prev",
            "next",
            "deck",
            "hand",
            "character",
            "team_status",
            "summon",
            "support",
        ]:
            for obj in current_objs:
                assert obj.__class__.__name__ == "PlayerTable", (
                    f"object must be a player_table with command {cmd}, "
                    f"current object is {obj.__class__.__name__}"
                )
            if cmd == "active":
                current_objs = [x.get_active_character() for x in current_objs]
            elif cmd == "prev":
                current_objs = [
                    x.characters[x.previous_character_idx()] for x in current_objs
                ]
                current_objs = [x for x in current_objs if x is not None]
            elif cmd == "next":
                current_objs = [
                    x.characters[x.next_character_idx()] for x in current_objs
                ]
                current_objs = [x for x in current_objs if x is not None]
            elif cmd == "deck":
                current_objs = sum([x.table_deck for x in current_objs], [])
            elif cmd == "hand":
                current_objs = sum([x.hands for x in current_objs], [])
            elif cmd == "character":
                current_objs = sum([x.characters for x in current_objs], [])
            elif cmd == "team_status":
                current_objs = sum([x.team_status for x in current_objs], [])
            elif cmd == "summon":
                current_objs = sum([x.summons for x in current_objs], [])
            else:
                assert cmd == "support"
                current_objs = sum([x.supports for x in current_objs], [])
        elif cmd in ["weapon", "artifact", "talent", "status", "skill"]:
            for obj in current_objs:
                assert (
                    obj.__class__.__name__ != "PlayerTable"
                    and obj.type == ObjectType.CHARACTER
                ), (
                    f"object must be a character with command {cmd}, "
                    f"current object is {obj.__class__.__name__}"
                )
            if cmd in ["weapon", "artifact", "talent"]:
                current_objs = [getattr(x, cmd) for x in current_objs]
                current_objs = [x for x in current_objs if x is not None]
            elif cmd == "status":
                current_objs = sum([x.status for x in current_objs], [])
            else:
                assert cmd == "skill"
                current_objs = sum([x.skills for x in current_objs], [])
        elif "=" in cmd:
            key, value = cmd.split("=")
            current_objs = [
                x
                for x in current_objs
                if str(getattr(x, key, None)).lower() == value.lower()
            ]
        else:
            raise ValueError(f"unknown command {cmd}")
    return current_objs


def query(object_position: Any, match: Any, command: str) -> List[Any]:
    """
    Receives object position, match, and get objects from match based on command.

    Command contains:
    - `both / our / opponent` to select player_table, or `self` to select this character
        (caller area must be character or character_status). must appear first.
    - `[active / prev / next]` or
        `[deck / hand / character / team_status / summon / support]`
        for player_table, `[weapon / artifact / talent]` or `[skill / status]` for
        character, to select an object (first group) or object lists (second group).
        Note with `both`, select one object may also receive two objects.
    - `['key=value']` to filter current objects that `x.key == value`. All types will be
        converted to str to compare. it can be used multiple times. command can be
        surrounded with quotes, and if not space in key and value, quotes can be
        omitted.
    - `and` to make multiple queries, and their results are combined.

    Samples:
    - `self` to get self character when called by a character status
    - `opponent active status 'name=Seed of Skandha'` to get status
    - `opponent character status name=Refraction` to get status from all opponent
        characters
    - `both summon` to get all summons on field
    - `self and our active and our next` to select characters
    """
    tokens = shlex.split(command)
    results = []
    while True:
        and_index = -1
        if "and" in tokens:
            and_index = tokens.index("and")
        if and_index == -1:
            results.extend(_query(object_position, match, tokens))
            break
        else:
            results.extend(_query(object_position, match, tokens[:and_index]))
            tokens = tokens[and_index + 1 :]
    return results


def query_one(
    object: Any, match: Any, command: str, allow_multiple: bool = False
) -> Any | None:
    """
    Receives object position, match, and get one object from match based on command.
    If no object is found, return None. For command structure, see `query` function.
    """
    result = query(object, match, command)
    if len(result) == 0:
        return None
    if not allow_multiple and len(result) > 1:
        raise ValueError(f"Multiple objects found for command {command}")
    return result[0]


def _satisfy_single_position(
    object_position: Any, command: List[str], match: Any | None
) -> bool:
    """
    deal with one object position and command, return if the object position satisfies
    the command. match is optional. if not provided, some command will raise error.
    """
    for cmd in command:
        if "=" not in cmd:
            raise ValueError(f"command {cmd} is not valid")
        key, value = cmd.split("=")
        if key == "pidx":
            if object_position.player_idx != int(value):
                return False
        elif key == "cidx":
            if object_position.character_idx != int(value):
                return False
        elif key == "area":
            if object_position.area.name.lower() != value.lower():
                return False
        elif key == "id":
            if object_position.id != int(value):
                return False
        elif key == "active":
            value = value.lower()
            if object_position.character_idx == -1:
                raise ValueError("active can only be used with valid character index")
            if match is None:
                raise AssertionError(
                    "match is not provided when command contains active"
                )
            if value not in ["true", "false"]:
                raise ValueError(
                    f"active value {value} is not valid, should be true or false"
                )
            table = match.player_tables[object_position.player_idx]
            active_idx = table.active_character_idx
            value = value == "true"
            if (active_idx == object_position.character_idx) != value:
                return False
        else:
            raise ValueError(f"unknown command {cmd}")
    return True


def _satisfy_between_position(source: Any, target: Any, command: List[str]) -> bool:
    """
    deal with two object positions and command, return if the two object positions
    satisfy the command.
    """
    for cmd in command:
        if "=" not in cmd:
            raise ValueError(f"command {cmd} is not valid")
        key, value = cmd.split("=")
        if value not in ["same", "diff"]:
            raise ValueError(f"value {value} is not valid, should be same or diff")
        value = value == "same"
        if key == "pidx":
            if (source.player_idx == target.player_idx) != value:
                return False
        elif key == "cidx":
            if (source.character_idx == target.character_idx) != value:
                return False
        elif key == "area":
            if (source.area == target.area) != value:
                return False
        elif key == "id":
            if (source.id == target.id) != value:
                return False
        else:
            raise ValueError(f"unknown command {cmd}")
    return True


def _satisfy_one(
    source: Any, target: Any | None, command: List[str], match: Any | None
) -> bool:
    """
    deal with one command without and.
    """
    assert command != "and", "command should not contain and"
    if command[0] == "both":
        assert target is not None, "target is not provided"
        return _satisfy_between_position(source, target, command[1:])
    elif command[0] == "source":
        return _satisfy_single_position(source, command[1:], match)
    elif command[0] == "target":
        assert target is not None, "target is not provided"
        return _satisfy_single_position(target, command[1:], match)
    else:
        raise ValueError(f"unknown command {command[0]}")


def satisfy(
    source: Any, command: str, target: Any | None = None, match: Any | None = None
) -> bool:
    """
    receives source `ObjectPosition`, target `ObjectPosition` and match. target and
    match are optional. without them, related command string will raise error.

    - `source / target` to select one object position, or `both` to compare between two
        positions
    - if one position selected: `[pidx=? / cidx=? / area=? / active=(true|false)]` to
        check if position fulfills the situation. for area names, they are case
        insensitive. can use multiple times, and all of them should pass.
    - if two position selected (i.e. `both`), `[(pidx|cidx|area|id)=(same|diff)]` to
        compare two positions are same or not. can use multiple times, and all of them
        should pass.
    - `and` to make multiple checks. All check should pass.

    samples:
    - `source area=support` is placed to support
    - `source area=character and target area=skill and both pidx=same cidx=same` is
        equipped to a character, and target is skill of this character
    - `both pidx=same and source area=hand and target area=skill` self in hand and
        target is this player use skill
    """
    tokens = shlex.split(command)
    while True:
        and_index = -1
        if "and" in tokens:
            and_index = tokens.index("and")
        if and_index == -1:
            return _satisfy_one(source, target, tokens, match)
        else:
            if not _satisfy_one(source, target, tokens[:and_index], match):
                return False
            tokens = tokens[and_index + 1 :]
