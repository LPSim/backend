# Changelog

All notable changes to this project will be documented in this file.

The first three numbers in the version number are the same as the version of 
the game, and the last number is the patch version.

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

[Unreleased]: https://github.com/zyr17/GITCG/compare/v0.4.1.0...HEAD
[0.4.1.0]: https://github.com/zyr17/GITCG/releases/tag/v0.4.1.0
[0.4.0.0]: https://github.com/zyr17/GITCG/releases/tag/v0.4.0.0
[0.1.0]: https://github.com/zyr17/GITCG/releases/tag/v0.1.0