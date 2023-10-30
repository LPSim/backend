# Changelog

All notable changes to this project will be documented in this file.

The second and third number in the version number are the same as the version 
of the game, and the last number is the patch version of this project.

## [Unreleased]

## [0.4.1.3] - 2023-10-31

### Added
- Add `Deck.deck_to_str` function.
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

[Unreleased]: https://github.com/LPSim/backend/compare/v0.4.1.3...HEAD
[0.4.1.3]: https://github.com/LPSim/backend/releases/tag/v0.4.1.3
[0.4.1.2]: https://github.com/LPSim/backend/releases/tag/v0.4.1.2
[0.4.1.1]: https://github.com/LPSim/backend/releases/tag/v0.4.1.1
[0.4.1.0]: https://github.com/LPSim/backend/releases/tag/v0.4.1.0
[0.4.0.0]: https://github.com/LPSim/backend/releases/tag/v0.4.0.0
[0.1.0]: https://github.com/LPSim/backend/releases/tag/v0.1.0
