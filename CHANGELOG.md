# Changelog

All notable changes to this project will be documented in this file.

The second and third number in the version number are the same as the version 
of the game, and the last number is the patch version of this project.

## [Unreleased]

## [0.4.2.4] - 2023-12-13

### Added
- added `http_log_replay.py` to replay logs.

### Fixed
- errors in `main.py`.
- typos in `deck_code_data.json`.
- Yayoi Nantsuki decreases Artifact cost based on Weapon number.
- Timaeus and Wagner is not treated as Companion.
- Aquila Favonia will heal charactor when it is not active.
- Where is the Unseen Razor will decrease opponent weapon cost.
- Tenacity of the Millelith will generate dice when the charactor is defeated
  during the attack.

### Changed
- `heal_self` is changed to `attack_self` in `SkillBase`.
- `CharactorDefeatedAction` will also return `RemoveObjectEventArguments`.
- `deck_code_data` structure is changed. Charactors will have `charactor:`
  prefix.
- `HTTPServer` now use GZip.
- Rhodeia's Elemental Skill will give version hint when generating summons.
- `is_corresponding_charactor_use_damage_skill` from Damage values
  will ignore damages that is caused by elemental reaction.
- Some redundant assertions are removed.
- `command_history` in `HTTPServer.log` is changed, now it will record the
  corresponding frame number and command order in the history.

## [0.4.2.3] - 2023-12-03

### Added
- `get_class_by_base_class` for `ClassRegistry`, which can get all classes 
  that are inherited from the base class.
- Before using a card, card usage will be checked by `UseCardValue`, which can
  mark a card failed to use.
- Added `/deck_code_data` endpoint in HTTPServer, which can get deck code data
  from server, and frontend can generate deck code without asking server.
- Now default_version will be recorded in `Deck`. If not specified, it is 
  `None`.
- Now `/log` in `HTTPServer` will log match_config.
- `AttackAndGenerateStatusSummonBase` is added for summons perform like Dehya's
  Elemental Skill summon, which will generate status at each round, and when it
  is removed, the corresponding status will also be removed.
- `CreateStatusPassiveSkill` is implemented for charactors that will generate
  status when they are created. 
- Now costs of cards and skills will be recorded in `desc_registry`, and passed
  to frontend by `/patch` in `HTTPServer`.

### Fixed
- wrong description of Gambler's Earrings with version 3.3.
- Typo of error message in class_registry.
- When deck code contains unknown card number, it will raise error. After 
  fixing this, it will ignore unknown card number.
- RoundEffectSupports, e.g. Paimon, NRE, is not inherited from its 
  corresponding base class (e.g. CompanionBase, ItemBase).
- Wrong cost of Joyous Celebration.
- Charactors that has status created at game start, e.g. Raiden Shogun, will 
  not gain the status when revive. Now they will inherit 
  `CreateStatusPassiveSkill` to gain the status and handle revive actions.
- When charactor is stunned (e.g. Frozen), it can still use skill by equipping
  Skill Talent cards.
- Targtaglia will accidently increase additional damage caused by elemental
  reaction, e.g. Electro-Charged.
- Wrong charactor order when triggering events. Previously is active charactor
  then left first; now is active charactor then next first.
- Can switch to current active charactor from current active charactor in 
  `Match`, though no cards or skills can trigger it now.
- #12 When summon triggers other events that will stack self, e.g. Burning
  Flame, if it is currently in max usage, it still keeps max usage after 
  attacking. This is fixed by using `ChangeObjectUsageAction` instead of 
  modifying its usage by itself directly.

# Changed
- Move template files to `templates` folder.
- Define `AllCharactorFoodCard` for foods that will effect all charactors.
- Now `CostLabels` contains `EQUIPMENT` and `EVENT` enum, to represent 
  equipments (Weapons, Artifacts, most Talent cards) and event cards (Most
  normal event cards, Arcane-legend cards, and some talents).
- New `FactionType` is added for future charactors.
- `ChangeUsageAction` removes `change_type`, it only supports change type of
  `DELTA` now.

## [0.4.2.2] - 2023-11-18

### Added
- #4 #5 #9 Implement class registry, which supports registering class by name 
  and getting class by name. It also supports registering classes after lpsim 
  is initialized.
- #13 Implement desc registry, which saves the descriptions of classes. When a 
  class is registered in the class registry, a valid description is required.
- Implement `/patch` endpoint in HTTPServer, which can be used to get 
  description patchs from server.
- #3 Support create `Deck` from deck code, or export `Deck` to deck code.
  Also add related APIs in HTTPServer.

### Changed
- Now `desc` for a class means description hints for the class, e.g. with 
  talent activated, descriptions of some class will change. `desc` is a Literal
  now and default contains empty string. If a class has hints, add more strings
  into it, and modify `desc` when situation matchs. When `desc` is set, its
  corresponding descriptions should also be valid. Refer to Sucrose's Large
  Wind Spirit and desc_class for more details.
- #6 Now HTTPServer will send detailed error about deck in `/deck` when deck is 
  invalid.

### Fixed
- #7 Nilou E cannot generate Bountiful Core in the first time.

## [0.4.2.1] - 2023-11-05

### Changed
- Balance changes of 4.2
  - Charactors
    - Arataki Itto
    - Rhodeia of Loch
    - Shenhe
    - Yanfei
    - Jean
  - Talents
    - Xingqiu
    - Barbara
    - Mirror Maiden
    - Electro Hypostasis
    - Chongyun
    - Xiangling
    - Yoimiya
    - Candace
    - Razor
    - Beidou
    - Kujou Sara
    - Cyno
    - Sangonomiya Kokomi
    - Amber
    - Jean
    - Yanfei
  - Cards
    - Joyous Celebration
- For SkillTalents, they no longer record the skill object that will trigger;
  instead, it records the name of the skill, and find the skill object when
  it is triggered.
- When performing reroll-dice, instead of saving states in history for each
  reroll, now no states will be saved during reroll, and frontend will get
  latest dice color in the request.

### Fixed
- Bug of Seed of Skandha, which will cause match error when triggered and 
  target is defeated.
- Bug of shield from Baizhu, which will revive charactor.
- Skills that will add status to target, e.g. elemental burst of Nilou, will
  raise error when target is defeated by the skill.
- Nilou's talent will raise error when summon disappears after attack.
- I Haven't Lost Yet cannot use if it's not in hand when charactor is defeated.

## [0.4.2.0] - 2023-11-04

### Added
- All charactors and cards in 4.2 are implemented.
  - Charactors and their talents:
    - Nilou
    - Dori
    - Baizhu
    - The Starry Skies Their Flowers Rain
    - Discretionary Supplement
    - All Things Are of the Earth
  - Equipments
    - Ocean-Hued Clam
    - Shadow of the Sand King
  - Supports
    - Stormterror's Lair
  - Event Cards
    - Lyresong
    - In Every House a Stove
- Implement DeclareRoundEndAttackSummonBase, RoundEndAttackCharactorStatus,
  and replace parent classes of related objects.
- Added new interface for HTTPServer, so client can get current running server
  version.

### Changed
- AttackerSummonBase support healing.
- Remove source_player_idx and target_player_idx from MakeDamageAction, and
  change change_charactor logic while making damages.

### Fixed
- Typo of Calx's Arts.
- When healing self charactor, Itto can get Superlative Superstrenth.

## [0.4.1.3] - 2023-10-31

### Added
- Add `Deck.to_str` function.
- Add object trashbin to make objects able to trigger events when they are 
  removed. #2

### Changed
- Melody loop now heal and make elemental application in one action.
- When a card is used, now it will be firstly moved into table.using_hand.
- Riptide and Dunyarzad are now implemented based on new object trashbin.
- Decks in logs of HTTPServer will save deck string instead of dict.

### Fixed
- Dehya summon logic bug. #1
- Keqing can use Lightning Stiletto when she is frozen.

## [0.4.1.2] - 2023-10-24

### Fixed
- Added dictdiff, fastapi and uvicorn into dependencies.

## [0.4.1.1] - 2023-10-24

### Added
- IconType for Summons, Status, and Supports.
- Histories by action level, now important actions will generate a history,
  and frontend can see what happened during two requests.
- Re-create mode is added to Match, in this mode, all randomness is removed,
  which can be used to re-create existing matchs.
- Add `Match.last_action` and `Match.action_info` to get information for 
  frontend.
- Skill prediction support is added. When it is player's turn, regardless of 
  the skill is able to use or not (except skill the cannot use at all, e.g. 
  passive skills and prepare skills), the diff of Match after using a skill 
  will be calculated and saved in `Match.skill_prediction`.
- Add submodule `frontend` to match frontend commits with backend commits.
- Add HTTP server to serve match.

### Changed
- Ocean Mimic generation logic of Rhodeia has changed. Both old and new logics
  are valid, but they will generate different Ocean Mimics with the same random
  state, and the number of times that random function called is different. 
- `Match.history_level` is moved into `Match.config`.
- Location Sangonomiya will heal all charactors in one action.
- Move repo from zyr17/GITCG to LPSim/backend.

### Fixed
- Icyquill with only one usage will affect multiple times.
- 1 usage Icyquill with Wanderer will cause wrong damage calculation.
- I Haven't Lost Yet will activate even if opponent charactor is defeated.
- Wrong damage increase with back damage of Eye of Stormy Judgement.
- Typo in element artifact descriptions.
- Chef Mao and Dunyarzad's draw-card effect not trigger with zero-cost cards.

## [0.4.1.0] - 2023-10-01

### Added
- All Charactors and Cards of 4.1 are implemented.
  - Charactors and their talents:
    - Dehya
    - Wanderer
    - Yaoyao
    - Stalwart and True
    - Gales of Reverie
    - Beneficient
  - Equipments
    - MoonPiercer
    - Crown of Watatsumi
  - Supports
    - Yayoi Nanatsuki
    - Gandharva Ville
  - Event cards
    - Fresh Wind of Freedom (implemented in previous release)
    - Pankration!

### Changed
- Balance changes of 4.1 are implemented.
  - Kamisato Ayato
  - Fatui Cryo Cicin Mage
  - Tartaglia
  - Diona
  - Xingqiu
  - NRE
  - Teyvat Fried Egg
  - Wind and Freedom
  - Dunyarzad
  - Chef Mao
  - Emblem of Severed Fate
  - Blessing of the Divine Relic's Installation
  - Master of Weaponry

### Fixed
- Unconsistency of RandomAgent in tests.
- ChargeAction of some skills are earlier than making damage, which may cause
  damage calculation error with Shimenawa's Reminiscence equipped.
- Tartaglia do not attach Riptide to the target when using elemental burst
  in ranged mode.
- Absolute imports of some charactors.

## [0.4.0.0] - 2023-09-30

### Added
- All Charactors and Cards until 4.0 are implemented.
- Some of charactors and cards that has balance change in 4.1 are updated 
  as 4.1 version.
  - Kamisato Ayato
  - Fatui Cryo Cicin Mage
  - Wind and Freedom
  - Dunyarzad
  - Chef Mao
  - Emblem of Severed Fate
  - Blessing of the Divine Relic's Installation
  - Master of Weaponry
- One new card in 4.1 is implemented.
  - Fresh Wind of Freedom

## [0.1.0] - 2023-09-18

### Added
- Test version to ensure release pipeline is working

[Unreleased]: https://github.com/LPSim/backend/compare/v0.4.2.4...HEAD
[0.4.2.4]: https://github.com/LPSim/backend/releases/tag/v0.4.2.4
[0.4.2.3]: https://github.com/LPSim/backend/releases/tag/v0.4.2.3
[0.4.2.2]: https://github.com/LPSim/backend/releases/tag/v0.4.2.2
[0.4.2.1]: https://github.com/LPSim/backend/releases/tag/v0.4.2.1
[0.4.2.0]: https://github.com/LPSim/backend/releases/tag/v0.4.2.0
[0.4.1.3]: https://github.com/LPSim/backend/releases/tag/v0.4.1.3
[0.4.1.2]: https://github.com/LPSim/backend/releases/tag/v0.4.1.2
[0.4.1.1]: https://github.com/LPSim/backend/releases/tag/v0.4.1.1
[0.4.1.0]: https://github.com/LPSim/backend/releases/tag/v0.4.1.0
[0.4.0.0]: https://github.com/LPSim/backend/releases/tag/v0.4.0.0
[0.1.0]: https://github.com/LPSim/backend/releases/tag/v0.1.0
