<div align="center">

<img src="docs/icon.png" width="96" alt="">

# Deadlock Assist

**Free Deadlock overlay that tells you what to buy mid-match (counter items vs the enemy team) and keeps your match history.**

[Website](https://deadlock-assist.com/) · [Polski](README.pl.md)

[![Download for Windows](https://img.shields.io/badge/Download-Windows%20.exe-f2a33a?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/adam2s/deadlock-assist-releases/releases/latest)

[![Latest version](https://img.shields.io/github/v/release/adam2s/deadlock-assist-releases?label=version&color=f2a33a)](https://github.com/adam2s/deadlock-assist-releases/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/adam2s/deadlock-assist-releases/total?label=downloads&color=57c46a)](https://github.com/adam2s/deadlock-assist-releases/releases)
![Windows 10/11](https://img.shields.io/badge/Windows-10%20%7C%2011-0e1014)
[![Support on Ko-fi](https://img.shields.io/badge/%E2%98%95-Support%20on%20Ko--fi-f2c94c)](https://ko-fi.com/deadlockassist)

<img src="docs/deadlock-overlay-counters.jpg" width="820" alt="Deadlock overlay: lane counters, “Buy now”, game clock and jungle camp timers">

</div>

## What it does

- **Counter items vs the enemy team.** Reads the heroes from the top bar and suggests the items that work best against them, with prices and what you can afford right now.
- **“Buy now” and next buys.** A build plan based on stats from thousands of matches (deadlock-api), fitted to what you already own.
- **Enemy purchases.** Hold Tab and it remembers the enemies' items, and warns you when someone buys, say, healing.
- **Clock and timers.** Mid Boss, jungle camps, power-ups and the soul urn.
- **Match history.** Results, minute-by-minute farm, buy order and a summary of what to improve.
- **Runs by itself.** A match starts when the game clock shows the first minute; the app updates itself.

<p align="center">
  <img src="docs/deadlock-overlay-tab.webp" width="49%" alt="Overlay with Tab held: every player's items and counters">
  <img src="docs/deadlock-match-history@2x.webp" width="49%" alt="Match history">
</p>

More: [counter items for every hero](https://deadlock-assist.com/counters/) · [Deadlock patch notes](https://deadlock-assist.com/patch-notes/) · [changelog](https://deadlock-assist.com/changes/)

## Install

1. Download `Deadlock.Assist_x.y.z_x64-setup.exe` from the [latest release](https://github.com/adam2s/deadlock-assist-releases/releases/latest).
2. Run the installer. If Windows shows “Windows protected your PC”, click **More info → Run anyway** (the installer does not have a paid code signature yet).
3. Run Deadlock in **borderless window** mode so the overlay shows on top of the game.

New versions install from inside the app: when one is out, an “Update and restart” button appears.

The app starts in English; switch to Polish with **PL** in the top right corner.

| Key | Action |
| --- | --- |
| `F10` | end the match and save it to history |
| `Tab` (held) | refresh every player's items |

## Safety

Deadlock Assist **does not read the game's memory, does not modify its files and sends no keys to it**. It only takes screenshots (like OBS or Discord) and downloads public stats from [deadlock-api.com](https://deadlock-api.com). Screenshots stay on your PC and are deleted once the match is saved.

This is an unofficial fan tool, not affiliated with Valve. Valve does not publish a list of allowed third-party programs, so you use it at your own risk.

## Ideas and bugs

- Got an idea? Click **“Suggest a change”** in the app or [post it here](https://github.com/adam2s/deadlock-assist-releases/issues/new?template=pomysl.yml).
- Something broken? [Report a bug](https://github.com/adam2s/deadlock-assist-releases/issues/new?template=blad.yml), ideally with a screenshot.

English or Polish, both are fine.

## Support

The app is and will stay free. If it helps you win, you can buy the author a coffee at **[ko-fi.com/deadlockassist](https://ko-fi.com/deadlockassist)** or with the **“☕ Support”** button in the top right corner of the app.

---

<sub>Deadlock is a trademark of Valve Corporation. This project is not affiliated with or endorsed by Valve. Item and hero data come from <a href="https://deadlock-api.com">deadlock-api.com</a>.</sub>
