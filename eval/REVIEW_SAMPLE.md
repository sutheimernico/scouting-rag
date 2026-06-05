# Golden-Set Review Sample (20%, seed=42)

Für jede Query unten: Prüfe, ob der gezeigte Beleg die Frage wirklich
beantwortet und ob die Annotation (Quote/Zeile/Bild) die richtige Stelle
markiert. Antworte pro Query mit ok oder nenne die q-Nummer + Problem.
Statblätter liegen unter `data/statsheets/` (im Explorer/VS Code zu öffnen).

## q001 (exact_match)

**Query:** Wie viele Tore hat Harry Kane in der Bundesliga-Saison 2025/26 erzielt?
**Soll-Antwort:** 36 Tore.

- **Beleg (Tabellenzeile):** `stats/openligadb/bundesliga_2025_scorers.csv`, keys ['H. Kane', '36']
  > `18898,H. Kane,36`

## q004 (exact_match)

**Query:** Wer war mit wie vielen Toren bester Torschütze der 2. Bundesliga 2025/26?
**Soll-Antwort:** Noel Futkeu mit 14 Toren.

- **Beleg (Tabellenzeile):** `stats/openligadb/2_bundesliga_2025_scorers.csv`, keys ['Noel Futkeu', '14']
  > `23411,Noel Futkeu,14`

## q009 (exact_match)

**Query:** Wie viele Punkte holte die TSG Hoffenheim in der Bundesliga-Saison 2025/26?
**Soll-Antwort:** 61 Punkte.

- **Beleg (Tabellenzeile):** `stats/openligadb/bundesliga_2025_table.csv`, keys ['TSG Hoffenheim', '61']
  > `175,TSG Hoffenheim,Hoffenheim,https://i.imgur.com/gF0PfEl.png,61,52,65,34,18,9,7,13`

## q016 (visual)

**Query:** Wie stark ist Álex Grimaldo laut Statblatt bei Key Passes pro 90 im Vergleich zu anderen Verteidigern?
**Soll-Antwort:** 100. Perzentil — bester Wert der Positionsgruppe.

- **Beleg (Statblatt):** `data/statsheets/alex_grimaldo_leverkusen.png`
  > Manifest: Álex Grimaldo (Leverkusen, DF) — npxG /90: P85, Shots /90: P99, SoT %: P61, Goals /90: P63, xAG /90: P99, Key passes /90: P100, Prog. passes /90: P89, Pass cmp %: P46

## q024 (visual)

**Query:** In welchem Perzentil liegt die Passquote von Tim Kleindienst laut seinem Statblatt 2024/25?
**Soll-Antwort:** 8. Perzentil unter Stürmern (60,9 %).

- **Beleg (Statblatt):** `data/statsheets/tim_kleindienst_gladbach.png`
  > Manifest: Tim Kleindienst (Gladbach, FW) — npxG /90: P73, Shots /90: P44, SoT %: P93, Goals /90: P81, xAG /90: P76, Key passes /90: P27, Prog. passes /90: P44, Pass cmp %: P8

## q031 (exact_match)

**Query:** Wie entwickelte sich der PPDA-Wert des FC Bayern zwischen erster und zweiter Saisonhälfte 2025/26?
**Soll-Antwort:** Verbesserung von 10,4 auf 9,3 Pässe pro Defensivaktion.

- **Beleg (Artikel):** _FC Bayern: Kompany vs. Bischof! Das sagen die Zahlen_ — `articles/227d796890c6973c.json`
  > …nne sind über zwei mehr pro Spiel als in den ersten 25 Partien (15,8). Und auch bei den Pässen pro bayerischer Defensivaktion gibt es einen klaren Fortschritt: **Bis zum Jahreswechsel lag der Wert im Schnitt bei 10,4. Jetzt liegt er bei 9,3.** Bedeutete also: Gegner bekommen durchschnittlich weniger Zeit am Ball. Aber: Die eigenen Pässe pro Ballbesitzphase sind minimal zurückgegangen. Statt etwas meh…

## q034 (semantic)

**Query:** Was fällt im Scouting-Report bei Saibaris Abschlussstatistiken besonders auf?
**Soll-Antwort:** Beste Trefferquote der Vergleichsgruppe: 20 % seiner Abschlüsse gehen rein, bei zweithöchster Torquote pro 90 Minuten.

- **Beleg (Artikel):** _Ismael Saibari im Scouting Report: Passt er zum FC Bayern?_ — `articles/57eeecd3ea2e49ba.json`
  > …che Feststellung, dass er defensiv gute Werte vorweisen kann. Dazu aber später mehr. Beim Blick auf die Werte gibt es dann aber doch eine Sache die herausragt: **Nicht nur hat er die zweithöchste Torquote pro 90 Minuten, er hat auch die beste Trefferquote. 20 Prozent seiner Abschlüsse gehen rein** – Uzun und Díaz kommen auf rund 19 Prozent, dahinter kommt dann schon ein größerer Sprung auf 16 Prozent (Musiala, Palmer). Olise und Gnabry kommen auf rund 14…

## q035 (semantic)

**Query:** Welche Schwäche attestierte das Spielverlagerung-Portrait von 2012 dem jungen Granit Xhaka?
**Soll-Antwort:** Das Spiel gegen den Ball / die Defensivarbeit; dazu leichte Probleme mit der ersten Ballberührung.

- **Beleg (Artikel):** _Adventskalender, Türchen 5: Granit Xhaka_ — `articles/02c4b1ffc87f1c90.json`
  > …es Aussage zielt dementsprechend nicht auf das Tempo der Bundesliga, sondern auf die individuellen Defizite Xhakas: Gerade defensiv muss er sich noch steigern. **Das Spiel gegen den Ball ist nicht seine Stärke; nicht umsonst verbrachte er fast seine gesamte Jugendzeit auf offensiven Positionen im Mittelfeld.** Das unterscheidet ihn vom klassischen Box-to-Box-Mittelfeldspieler, der „defensiv ausschließlich defensiv agiert und offensiv ausschließlich offensiv“ (ein fas…

## q043 (semantic)

**Query:** Wie veränderte sich Robert Lewandowskis Spiel in seiner ersten Dortmund-Zeit laut Spielverlagerung?
**Soll-Antwort:** Er schaltete sich zunehmend ins Aufbauspiel ein und entwickelte Spielstärke über die reine Stürmerrolle hinaus.

- **Beleg (Artikel):** _Adventskalender, Türchen 6: Robert Lewandowski_ — `articles/b1b4b107bb9b360d.json`
  > …e Chance gegeben, sondern nur auf ein Scheitern gewartet.“ Wer in dieser Rückrunde genauer hinschaute, entdeckte allerdings neue Qualitäten im Spiel des Polen: **Im Verlauf der Rückserie schaltete er sich mehr und mehr in das Aufbauspiel der Borussia ein.** Während er in seinen ersten Partien noch wie ein Fremdkörper im Passspiel und Pressing der Meistermannschaft wirkte, wurden seine Aktionen zunehmend selbstvers…

## q048 (multi_hop)

**Query:** Nach dem Gordon-Transfer zum FC Barcelona: Welchen Spieler nahm der FC Bayern laut Scouting-Report stattdessen ins Visier?
**Soll-Antwort:** Ismael Saibari von der PSV Eindhoven.

- **Beleg (Artikel):** _FC Bayern: Die besten Gordon-Alternativen in der Analyse_ — `articles/05a151c378243bff.json`
  > Anthony Gordon vom Markt: Wie geht die Linksaußen-Suche des FC Bayern weiter? **Der Wechsel von Anthony Gordon zum FC Barcelona dürfte den FC Bayern nur wenig überrascht haben.** Die von Newcastle United aufgerufenen 80 Millionen Euro wollte man in München nicht zahlen. Dass es andere Klubs gibt, die genau das tun würden, war absehbar. …
- **Beleg (Artikel):** _Ismael Saibari im Scouting Report: Passt er zum FC Bayern?_ — `articles/57eeecd3ea2e49ba.json`
  > …h vor der WM unter Dach und Fach zu bringen. Ein zielstrebiges Vorgehen, das darauf schließen lässt, dass man sich schon länger mit Saibari beschäftigt hat und **sich nach dem Transfer von Anthony Gordon zum FC Barcelona endgültig dazu entschloss, den offensiven Mittelfeldspieler zu verpflichten**. Doch wer ist Ismael Saibari überhaupt und wo liegen seine Stärken und Schwächen? Passt er ins System von Vincent Kompany? Miasanrot hat sich mehrere Stunden V…

## q055 (multi_hop)

**Query:** Welche Verletzung beendete Alphonso Davies' Saison 2025/26 vorzeitig, und welchen Top-Speed hatte er zuvor in der Saison erreicht?
**Soll-Antwort:** Verletzung am hinteren linken Oberschenkel; zuvor 34,88 km/h Top-Speed — schnellster Bayern-Außenverteidiger.

- **Beleg (Artikel):** _FC Bayern: Wieder Verletzt! Alphonso Davies erleidet nächsten Rückschlag_ — `articles/2af7516fa6b8f1e8.json`
  > …n Linksverteidiger. Nach dem Kreuzbandriss im vergangenen Jahr und einer Muskelverletzung im Frühjahr füllt sich Davies’ Krankenakte nun um eine weitere Seite: **Der Kanadier hat sich am hinteren linken Oberschenkel verletzt.** - Werbung: Das neue Bayern-Trikot und 50 Prozent auf Klassiker sparen – JETZT bei Kitbag (Affiliate-Link) - Werbung: Das WM-Trikot der Nationalmannschaft – jet…
- **Beleg (Artikel):** _FC Bayern: Upgrade oder Luxus? Die große AV-Frage_ — `articles/07ead1864dd51dd3.json`
  > …nze Wahrheit. Ein Blick auf die internationalen Spieldaten der abgelaufenen Saison zeigt: Im Bereich Top-Speed liegt der junge Niederländer (33,07 km/h) hinter **Davies (34,88 km/h)**, Laimer (33,91 km/h) und Stanišić (33,67 km/h). Case closed? Auch hier nicht ganz. Die gemessenen Werte beziehen sich lediglich auf die Endgeschwindigkeit – ni…

## q057 (multi_hop)

**Query:** Wie viele Bundesliga-Tore schoss Deniz Undav 2025/26, und welche Rolle spielte er im Pokalfinale gegen Bayern?
**Soll-Antwort:** 19 Liga-Tore; im Pokalfinale hatte er nach gut einer Minute die erste Halbchance per Kopf.

- **Beleg (Tabellenzeile):** `stats/openligadb/bundesliga_2025_scorers.csv`, keys ['D. Undav', '19']
  > `16686,D. Undav,19`
- **Beleg (Artikel):** _Kane nimmt VfB auseinander: FC Bayern gewinnt den Pokal!_ — `articles/f596b9c35add4b7e.json`
  > …hr das Schüller-Schicksal? - Zur aktuellen Podcast-Folge DFB-Pokal-Finale gegen VfB Stuttgart: Business as usual Die Schwaben starteten intensiv in die Partie. **Deniz Undav hatte nach gut einer Minute die erste Halbchance**, der Kopfball des Nationalstürmers nach einer Ecke war aber zu unplatziert. Und auch sonst zeigte der VfB gleich, dass man nicht das vierte Pflichtspiel in die…
