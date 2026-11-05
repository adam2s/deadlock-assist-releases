# Bezpieczeństwo

## Zgłaszanie luk

Znalazłeś lukę w Deadlock Assist (np. w instalatorze, aktualizacjach albo w tym, jak aplikacja otwiera linki)? **Nie zgłaszaj jej publicznie w Issues.**

Użyj prywatnego zgłoszenia: zakładka **Security → [Report a vulnerability](https://github.com/adam2s/deadlock-assist-releases/security/advisories/new)**. Widzi je tylko autor.

Opisz:

- czego dotyczy luka i jak ją wywołać,
- wersję aplikacji (widać ją obok nazwy w oknie, np. 1.2.5) i wersję Windows,
- co może zrobić atakujący.

Odpowiedź dostaniesz zwykle w ciągu kilku dni. Po wydaniu poprawki opiszę lukę w notatkach wydania i, jeśli chcesz, podziękuję Ci z imienia lub nicku.

## Wspierane wersje

Poprawki bezpieczeństwa trafiają tylko do najnowszej wersji. Aplikacja aktualizuje się sama, więc wystarczy kliknąć „Zaktualizuj i uruchom ponownie”, gdy się pojawi.

| Wersja | Poprawki |
| --- | --- |
| najnowsza | tak |
| starsze | nie |

## Jak chronione są aktualizacje

- Instalatory są budowane automatycznie przez GitHub Actions i publikowane tylko w [wydaniach tego repo](https://github.com/adam2s/deadlock-assist-releases/releases).
- Każda aktualizacja jest podpisana kluczem autora. Aplikacja sprawdza podpis przed instalacją i odrzuca pliki bez ważnego podpisu.
- Każde wydanie ma plik `SHA256SUMS.txt` z sumami kontrolnymi instalatorów. Sprawdzisz pobrany plik w PowerShell: `Get-FileHash .\plik.exe` i porównasz wynik z tym w opisie wydania.
- Pobieraj aplikację tylko stąd. Kopie z innych stron mogą być zmienione.

## Czego nie uznajemy za lukę

- Ostrzeżenia SmartScreen „System Windows ochronił ten komputer”: instalator nie ma jeszcze płatnego certyfikatu podpisu kodu.
- Zgłoszeń o tym, że aplikacja robi zrzuty ekranu: to jej podstawowe działanie, opisane w [README](README.md#bezpieczeństwo). Zrzuty zostają na Twoim komputerze.
