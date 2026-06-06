# Faithfulness Manual Sample (cycle 1) — seed=42, n=10 + 3 flagged calibration cases

Pro Fall: Stimmt das Judge-Urteil? Antworte z.B. 'q005: Judge irrt, Antwort ist gestützt'.
supported = jede Faktenaussage der Antwort steht im Kontext; ehrliche Verweigerung zählt als ok.

## q002 [exact_match]

**Frage:** Wie viele Bundesliga-Tore erzielte Deniz Undav in der Saison 2025/26?
**Antwort:** 19
**Judge:** supported=True, refusal=False — Die Anzahl der von Deniz Undav erzielten Tore in der Saison 2025/26 wird im Kontext explizit genannt.

**Kontext (gekürzt):**
> Bundesliga Spieler-Passstatistik 2024/25 (player passing stats) | Season_End_Year: 2025 | Squad: Stuttgart | Comp: Bundesliga | Player: Deniz Undav | Nation: GER | Pos: FW,MF | Age: 28 | Born: 1996.0 | Mins_Per_90: 19.2 | Cmp_Total: 431.0 | Att_Total: 589.0 | Cmp_percent_Total: 73.2 | TotDist_Total:
> Bundesliga Spieler-Schussstatistik 2024/25 (player shooting stats) | Season_End_Year: 2025 | Squad: Stuttgart | Comp: Bundesliga | Player: Deniz Undav | Nation: GER | Pos: FW,MF | Age: 28 | Born: 1996.0 | Mins_Per_90: 19.2 | Gls_Standard: 9.0 | Sh_Standard: 75.0 | SoT_Standard: 31.0 | SoT_percent_St
> Bundesliga Spieler-Einsatzzeiten 2024/25 (player playing time) | Season_End_Year: 2025 | Squad: Stuttgart | Comp: Bundesliga | Player: Deniz Undav | Nation: GER | Pos: FW,MF | Age: 28 | Born: 1996.0 | MP_Playing.Time: 27.0 | Min_Playing.Time: 1726.0 | Mn_per_MP_Playing.Time: 64.0 | Min_percent_Playi

## q007 [exact_match]

**Frage:** Wie viele Tore erzielte der FC Bayern München insgesamt in der Bundesliga-Saison 2025/26?
**Antwort:** Der FC Bayern München erzielte insgesamt 122 Tore in der Bundesliga-Saison 2025/26.
**Judge:** supported=True, refusal=False — Die Zahl 122 wird im Kontext mehrfach erwähnt, insbesondere als Rekord für die meisten Tore in einer Saison.

**Kontext (gekürzt):**
> FC Bayern, MSR Awards: Männer erstmals vor den Frauen
Mit 122 Ligatreffern stellte der Rekordmeister nicht nur einen neuen Bundesliga-Bestwert auf, sondern erzielte mehr Tore als jede andere Mannschaft zuvor im modernen Fußball – für einen höheren Wert muss man bis in die 40er-Jahre zurückgehen. Sel
> FC Bayern in der CL: Ist die Bundesliga das große Problem?
Champions-League: Scheitert der FC Bayern an der eigenen Dominanz? Der Reflex nach dem Ausscheiden des FC Bayern München gegen Paris Saint-Germain ist schnell da: Die Münchner scheitern auf europäischer Bühne, weil sie national nicht genug g
> Der FC Bayern fliegt förmlich – doch eine Schwäche bleibt
FC Bayern bekommt seine Standardschwäche nicht wirklich in den Griff
Dieser Artikel wurde von Maximilian verfasst. Maximilian hat sich bei Miasanrot beworben. Der FC Bayern hat jüngst im Spiel gegen St. Pauli den 54-jährigen Torrekord aus der

## q008 [exact_match]

**Frage:** Welcher Verein gewann die 2. Bundesliga 2025/26 und mit wie vielen Punkten?
**Antwort:** FC Schalke 04 gewann die 2. Bundesliga 2025/26 mit 70 Punkten.
**Judge:** supported=True, refusal=False — The answer is fully supported by the context, as it states that FC Schalke 04 won the league with 70 points.

**Kontext (gekürzt):**
> 2. Bundesliga Abschlusstabelle 2025/26 (final league table) | teamName: Hannover 96 | shortName: Hannover | points: 60 | opponentGoals: 44 | goals: 60 | matches: 34 | won: 16 | lost: 6 | draw: 12 | goalDiff: 16
> 2. Bundesliga Abschlusstabelle 2025/26 (final league table) | teamName: Fortuna Düsseldorf | shortName: Düsseldorf | points: 37 | opponentGoals: 53 | goals: 33 | matches: 34 | won: 11 | lost: 19 | draw: 4 | goalDiff: -20
> 2. Bundesliga Abschlusstabelle 2025/26 (final league table) | teamName: FC Schalke 04 | shortName: Schalke | points: 70 | opponentGoals: 31 | goals: 50 | matches: 34 | won: 21 | lost: 6 | draw: 7 | goalDiff: 19

## q009 [exact_match]

**Frage:** Wie viele Punkte holte die TSG Hoffenheim in der Bundesliga-Saison 2025/26?
**Antwort:** 61
**Judge:** supported=True, refusal=False — Die Anzahl der Punkte, die die TSG Hoffenheim in der Saison 2025/26 erzielt hat, ist im Kontext explizit angegeben.

**Kontext (gekürzt):**
> Bundesliga Abschlusstabelle 2025/26 (final league table) | teamName: TSG Hoffenheim | shortName: Hoffenheim | points: 61 | opponentGoals: 52 | goals: 65 | matches: 34 | won: 18 | lost: 9 | draw: 7 | goalDiff: 13
> Bundesliga Spieler-Schussstatistik 2024/25 (player shooting stats) | Season_End_Year: 2025 | Squad: Hoffenheim | Comp: Bundesliga | Player: Max Moerstedt | Nation: GER | Pos: FW | Mins_Per_90: 5.0 | Gls_Standard: 0.0 | Sh_Standard: 12.0 | SoT_Standard: 4.0 | SoT_percent_Standard: 33.3 | Sh_per_90_St
> Bundesliga Spieler-Schussstatistik 2024/25 (player shooting stats) | Season_End_Year: 2025 | Squad: Hoffenheim | Comp: Bundesliga | Player: Umut Tohumcu | Nation: GER | Pos: MF,FW | Age: 19 | Born: 2004.0 | Mins_Per_90: 4.2 | Gls_Standard: 0.0 | Sh_Standard: 3.0 | SoT_Standard: 1.0 | SoT_percent_Sta

## q015 [visual] **[flagged: bitte besonders prüfen]**

**Frage:** In welchem Perzentil liegt Álex Grimaldo beim xAG pro 90 Minuten laut seinem Statblatt 2024/25?
**Antwort:** Alex Grimaldo liegt im Perzentil 100 beim xAG pro 99.3 min, da sein Wert von 8.1 höher ist als der Wert von Felix Agu mit 1.8 und Aleix García ohne genauer Vergleichsdaten in diesem Bereich. Jedoch basierend auf den gegebenen Daten liegt er im höchsten Perzentil. Genauer kann hier nicht beantwortet werden, da kein expliziter Vergleichswert oder Perzentil angegeben ist.
**Judge:** supported=False, refusal=True — Kein expliziter Vergleichswert oder Perzentil für xAG pro 90 Minuten von Álex Grimaldo

**Kontext (gekürzt):**
> Bundesliga Spieler-Einsatzzeiten 2024/25 (player playing time) | Season_End_Year: 2025 | Squad: Leverkusen | Comp: Bundesliga | Player: Álex Grimaldo | Nation: ESP | Pos: DF | Age: 28 | Born: 1995.0 | MP_Playing.Time: 32.0 | Min_Playing.Time: 2636.0 | Mn_per_MP_Playing.Time: 82.0 | Min_percent_Playi
> Bundesliga Spieler-Passstatistik 2024/25 (player passing stats) | Season_End_Year: 2025 | Squad: Leverkusen | Comp: Bundesliga | Player: Álex Grimaldo | Nation: ESP | Pos: DF | Age: 28 | Born: 1995.0 | Mins_Per_90: 29.3 | Cmp_Total: 1700.0 | Att_Total: 2094.0 | Cmp_percent_Total: 81.2 | TotDist_Tota
> Bundesliga Spieler-Schussstatistik 2024/25 (player shooting stats) | Season_End_Year: 2025 | Squad: Leverkusen | Comp: Bundesliga | Player: Álex Grimaldo | Nation: ESP | Pos: DF | Age: 28 | Born: 1995.0 | Mins_Per_90: 29.3 | Gls_Standard: 2.0 | Sh_Standard: 44.0 | SoT_Standard: 13.0 | SoT_percent_St

## q016 [visual]

**Frage:** Wie stark ist Álex Grimaldo laut Statblatt bei Key Passes pro 90 im Vergleich zu anderen Verteidigern?
**Antwort:** Dazu finde ich nichts im Korpus.
**Judge:** supported=False, refusal=True — Keine Informationen über Álex Grimaldo in Bezug auf Key Passes pro 90 Minuten

**Kontext (gekürzt):**
> Bundesliga Spieler-Passstatistik 2024/25 (player passing stats) | Season_End_Year: 2025 | Squad: Leverkusen | Comp: Bundesliga | Player: Álex Grimaldo | Nation: ESP | Pos: DF | Age: 28 | Born: 1995.0 | Mins_Per_90: 29.3 | Cmp_Total: 1700.0 | Att_Total: 2094.0 | Cmp_percent_Total: 81.2 | TotDist_Tota
> Bundesliga Spieler-Schussstatistik 2024/25 (player shooting stats) | Season_End_Year: 2025 | Squad: Leverkusen | Comp: Bundesliga | Player: Álex Grimaldo | Nation: ESP | Pos: DF | Age: 28 | Born: 1995.0 | Mins_Per_90: 29.3 | Gls_Standard: 2.0 | Sh_Standard: 44.0 | SoT_Standard: 13.0 | SoT_percent_St
> Bundesliga Spieler-Einsatzzeiten 2024/25 (player playing time) | Season_End_Year: 2025 | Squad: Leverkusen | Comp: Bundesliga | Player: Álex Grimaldo | Nation: ESP | Pos: DF | Age: 28 | Born: 1995.0 | MP_Playing.Time: 32.0 | Min_Playing.Time: 2636.0 | Mn_per_MP_Playing.Time: 82.0 | Min_percent_Playi

## q018 [visual]

**Frage:** In welchem Perzentil liegt Granit Xhaka bei progressiven Pässen pro 90 laut seinem Statblatt?
**Antwort:** Dazu finde ich nichts im Korpus.
**Judge:** supported=False, refusal=True — Keine Informationen über Xhakas Leistung in Bezug auf progressive Pässe pro 90 Minuten finden.

**Kontext (gekürzt):**
> Bundesliga Spieler-Passstatistik 2024/25 (player passing stats) | Season_End_Year: 2025 | Squad: Leverkusen | Comp: Bundesliga | Player: Granit Xhaka | Nation: SUI | Pos: MF | Age: 31 | Born: 1992.0 | Mins_Per_90: 32.1 | Cmp_Total: 2528.0 | Att_Total: 2818.0 | Cmp_percent_Total: 89.7 | TotDist_Total
> Bundesliga Spieler-Schussstatistik 2024/25 (player shooting stats) | Season_End_Year: 2025 | Squad: Leverkusen | Comp: Bundesliga | Player: Granit Xhaka | Nation: SUI | Pos: MF | Age: 31 | Born: 1992.0 | Mins_Per_90: 32.1 | Gls_Standard: 2.0 | Sh_Standard: 21.0 | SoT_Standard: 3.0 | SoT_percent_Stan
> Bundesliga Spieler-Einsatzzeiten 2024/25 (player playing time) | Season_End_Year: 2025 | Squad: Leverkusen | Comp: Bundesliga | Player: Granit Xhaka | Nation: SUI | Pos: MF | Age: 31 | Born: 1992.0 | MP_Playing.Time: 33.0 | Min_Playing.Time: 2888.0 | Mn_per_MP_Playing.Time: 88.0 | Min_percent_Playin

## q041 [semantic]

**Frage:** Warum denkt der FC Bayern über einen weiteren Rechtsverteidiger nach, obwohl die Position doppelt besetzt ist?
**Antwort:** Der FC Bayern denkt über einen weiteren Rechtsverteidiger nach, weil Laimer und Stanišić flexibel genutzt werden können und künftig in anderen Rollen eingesetzt werden könnten. Zudem wäre eine zusätzliche Option für die Balance der Abwehr nützlich.
**Judge:** supported=True, refusal=False — Die Antwort wird durch den Text unterstützt, insbesondere durch die Aussage 'Denn sowohl Laimer als auch Stanišić könnten künftig auch in anderen Rollen eingesetzt werden – wodurch die Suche nach eine

**Kontext (gekürzt):**
> FC Bayern: Upgrade oder Luxus? Die große AV-Frage
Wer Read auf dem Platz beobachtet, wird seine Explosivität im Antritt als einen entscheidenden Unterschied zu Laimer und Stanišić ausmachen. Eine Eigenschaft, die besonders für die intensive Spielweise und das hohe Verteidigen unter Kompany gefragt i
> FC Bayern: Upgrade oder Luxus? Die große AV-Frage
Dann könnte der ehemalige Leipziger allerdings nicht mehr im gleichen Ausmaß für die Außenverteidigerrolle eingeplant werden. Wirkliche Anzeichen gibt es für eine solche Umstellung im Kader bisher aber nicht. In der Innenverteidigung ist bislang unkl
> Simon verlässt den FC Bayern: Chance für beide Seiten?
Trotzdem bleiben dem FC Bayern mit Kett, Gwin und Naschenweng nur noch drei nominelle Außenverteidigerinnen. Die vielseitige Kett kann zwar beide Seiten bespielen, trotzdem sind drei Spielerinnen auf den Außen wohl zu wenig. Konkrete Gerüchte um

## q048 [multi_hop]

**Frage:** Nach dem Gordon-Transfer zum FC Barcelona: Welchen Spieler nahm der FC Bayern laut Scouting-Report stattdessen ins Visier?
**Antwort:** Luis Díaz wurde als Alternative für Anthony Gordon in den Scouting-Reports des FC Bayern erwähnt.
**Judge:** supported=True, refusal=False — Der Artikel erwähnt, dass Luis Díaz eine Chance ergab, nachdem die Causa Florian Wirtz noch viel länger dauerte.

**Kontext (gekürzt):**
> FC Bayern: Die besten Gordon-Alternativen in der Analyse
Anthony Gordon vom Markt: Wie geht die Linksaußen-Suche des FC Bayern weiter? Der Wechsel von Anthony Gordon zum FC Barcelona dürfte den FC Bayern nur wenig überrascht haben. Die von Newcastle United aufgerufenen 80 Millionen Euro wollte man i
> FC Bayern: Die besten Gordon-Alternativen in der Analyse
2024/25 waren es noch fast sieben bei einer Quote von 57 Prozent, in dieser Saison sind es nur noch vier bei rund 59 Prozent. Dass der 26-Jährige immenses Potenzial hat, steht außer Frage. Sein Tempo, seine technischen Fähigkeiten, sein Gespür
> FC Bayern: Passt das? Vlahović und Gordon in der Analyse
Lennart Karl, Olise und Díaz bewegen sich alle im Bereich zwischen 33 und 34 km/h, für Flügelspieler auf Top-Niveau keine herausragenden Werte. Gordon dagegen gehört zu den schnellsten Spielern Europas. Der Engländer knackte in dieser Saison u

## q056 [multi_hop]

**Frage:** Mit wie vielen Punkten wurde der FC Bayern 2025/26 Meister, und wie komplettierte er das Double?
**Antwort:** Der FC Bayern München wurde 2025/26 mit 89 Punkten Meister und komplettierte damit das Double, da er auch die Bundesliga-Titeliegezeit gewann.
**Judge:** supported=True, refusal=False — Die Antwort enthält alle in der Tabelle genannten Fakten.

**Kontext (gekürzt):**
> Bundesliga Abschlusstabelle 2025/26 (final league table) | teamName: FC Bayern München | shortName: Bayern | points: 89 | opponentGoals: 36 | goals: 122 | matches: 34 | won: 28 | lost: 1 | draw: 5 | goalDiff: 86
> FC Bayern, MSR Awards: Männer erstmals vor den Frauen
Mit 122 Ligatreffern stellte der Rekordmeister nicht nur einen neuen Bundesliga-Bestwert auf, sondern erzielte mehr Tore als jede andere Mannschaft zuvor im modernen Fußball – für einen höheren Wert muss man bis in die 40er-Jahre zurückgehen. Sel
> FC Bayern: Sehnsucht nach dem DFB-Pokal so groß ist wie nie
Kaum ein Verein in Europa dominiert die nationale Liga wie der FC Bayern die höchste deutsche Spielklasse. Seit dem vergangenen Wochenende steht der 35. Meistertitel der Vereinsgeschichte fest. In den letzten 14 Jahren landete die Schale am

## q005 [exact_match] **[flagged: bitte besonders prüfen]**

**Frage:** Wie viele Zweitliga-Tore erzielte F. Bilbija 2025/26?
**Antwort:** 13
**Judge:** supported=False, refusal=False — The context shows that F. Bilbija scored only 1 goal, not 13.

**Kontext (gekürzt):**
> 2. Bundesliga Torschützenliste 2025/26 (top scorers) | goalGetterName: F. Bilbija | goalCount: 13
> 2. Bundesliga Torschützenliste 2025/26 (top scorers) | goalGetterName: Bilbija | goalCount: 1
> 2. Bundesliga Torschützenliste 2025/26 (top scorers) | goalGetterName: Filip Bilbija | goalCount: 1

## q036 [semantic] **[flagged: bitte besonders prüfen]**

**Frage:** Welche Rolle spielte Granit Xhaka beim FC Basel laut Spielverlagerung-Portrait?
**Antwort:** Granit Xhaka war bei Borussia Mönchengladbach nicht die omnipräsente Kraft, sondern er agierte abwechselnd als abkippende Sechs und spielte auch Schnittstellenpässe. Bei FC Basel dagegen war er der omnipräsente Motor der Mannschaft in allen Spieldritteln.
**Judge:** supported=False, refusal=False — Die Aussagen über Xhakas Rolle beim FC Basel und bei Borussia Mönchengladbach sind widersprüchlich.

**Kontext (gekürzt):**
> Adventskalender, Türchen 5: Granit Xhaka
Er durchlief alle Jugendstationen des Rekordmeisters und der Schweizer Jugend-Auswahlteams. 2009 gewann er mit der U17 seines Landes die Weltmeisterschaft – völlig überraschend, war das Team doch krasser Außenseiter. Im offensiven Mittelfeld war er neben den 
> Adventskalender, Türchen 5: Granit Xhaka
Das konnte bedeuten, dass er abwechselnd mit Huggel als abkippende Sechs agierte, aber auch, dass er am gegnerischen Strafraum Schnittstellenpässe spielte oder zu seinen gefährlichen Fernschüssen ansetzte. Granit Xhaka war in allen Spieldritteln der omnipräse
> Türchen 11: Lars Stindl
Er sieht also trotz seiner spielmachenden Anlagen eher als Passspieler für die Situation, der eher eingebunden werden muss, als dass er seine Mitspieler einbindet. Eine Gegenthese dazu ist übrigens Granit Xhaka. Der ehemalige Zehner versucht bei Borussia Mönchengladbach sehr 
