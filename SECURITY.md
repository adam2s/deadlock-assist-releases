# Security

[Polski poniżej](#wersja-polska)

## Reporting a vulnerability

Found a vulnerability in Deadlock Assist (e.g. in the installer, the updates, or how the app opens links)? **Please do not report it publicly in Issues.**

Use a private report: the **Security → [Report a vulnerability](https://github.com/adam2s/deadlock-assist-releases/security/advisories/new)** tab. Only the author sees it.

Describe:

- what the vulnerability affects and how to trigger it,
- the app version (shown next to the name in the window, e.g. 1.2.5) and your Windows version,
- what an attacker could do.

You will usually get an answer within a few days. Once a fix is released, I will describe the vulnerability in the release notes and, if you like, thank you by name or nickname.

## Supported versions

Security fixes go only into the latest version. The app updates itself, so just click “Update and restart” when it shows up.

| Version | Fixes |
| --- | --- |
| latest | yes |
| older | no |

## How updates are protected

- Installers are built automatically by GitHub Actions and published only in [this repo's releases](https://github.com/adam2s/deadlock-assist-releases/releases).
- Every update is signed with the author's key. The app checks the signature before installing and rejects files without a valid one.
- Every release has a `SHA256SUMS.txt` file with the installers' checksums. Check a downloaded file in PowerShell: `Get-FileHash .\file.exe` and compare the result with the one in the release notes.
- Download the app only from here. Copies from other sites may be altered.

## What we do not treat as a vulnerability

- SmartScreen's “Windows protected your PC” warning: the installer does not have a paid code-signing certificate yet.
- Reports that the app takes screenshots: that is its core job, described in the [README](README.md#safety). Screenshots stay on your PC.

## Wersja polska

### Zgłaszanie luk

Znalazłeś lukę w Deadlock Assist (np. w instalatorze, aktualizacjach albo w tym, jak aplikacja otwiera linki)? **Nie zgłaszaj jej publicznie w Issues.**

Użyj prywatnego zgłoszenia: zakładka **Security → [Report a vulnerability](https://github.com/adam2s/deadlock-assist-releases/security/advisories/new)**. Widzi je tylko autor.

Opisz:

- czego dotyczy luka i jak ją wywołać,
- wersję aplikacji (widać ją obok nazwy w oknie, np. 1.2.5) i wersję Windows,
- co może zrobić atakujący.

Odpowiedź dostaniesz zwykle w ciągu kilku dni. Po wydaniu poprawki opiszę lukę w notatkach wydania i, jeśli chcesz, podziękuję Ci z imienia lub nicku.

### Wspierane wersje

Poprawki bezpieczeństwa trafiają tylko do najnowszej wersji. Aplikacja aktualizuje się sama, więc wystarczy kliknąć „Zaktualizuj i uruchom ponownie”, gdy się pojawi.

| Wersja | Poprawki |
| --- | --- |
| najnowsza | tak |
| starsze | nie |

### Jak chronione są aktualizacje

- Instalatory są budowane automatycznie przez GitHub Actions i publikowane tylko w [wydaniach tego repo](https://github.com/adam2s/deadlock-assist-releases/releases).
- Każda aktualizacja jest podpisana kluczem autora. Aplikacja sprawdza podpis przed instalacją i odrzuca pliki bez ważnego podpisu.
- Każde wydanie ma plik `SHA256SUMS.txt` z sumami kontrolnymi instalatorów. Sprawdzisz pobrany plik w PowerShell: `Get-FileHash .\plik.exe` i porównasz wynik z tym w opisie wydania.
- Pobieraj aplikację tylko stąd. Kopie z innych stron mogą być zmienione.

### Czego nie uznajemy za lukę

- Ostrzeżenia SmartScreen „System Windows ochronił ten komputer”: instalator nie ma jeszcze płatnego certyfikatu podpisu kodu.
- Zgłoszeń o tym, że aplikacja robi zrzuty ekranu: to jej podstawowe działanie, opisane w [README](README.pl.md#bezpieczeństwo). Zrzuty zostają na Twoim komputerze.
