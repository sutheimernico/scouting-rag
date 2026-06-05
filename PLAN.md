<!--
Verbatim project plan as provided by Nico on 2026-06-05.
This is the binding reference for cycle scope and working mode.
Amendments agreed during design are documented in
docs/superpowers/specs/2026-06-05-scouting-rag-corpus-eval-design.md
and never silently edited into this file.
-->

# Projektplan: Scouting-RAG

## 1. Was wir bauen und warum

Ein Retrieval-Augmented-Generation-System als Scouting-Assistant für Fußball. Nutzer stellen Fragen wie "finde Außenverteidiger unter 23 mit aufbaustarkem Profil", "vergleiche Spieler A und B", "was sagen die Reports über die Schwächen von Spieler X". Das System beantwortet sie aus einem gemischten Korpus aus Scouting-Reports, Statistik-Tabellen und visuellen Statblättern.

Das eigentliche Ziel ist nicht "eine RAG-Pipeline, die läuft". Das eigentliche Ziel ist eine gemessene Vergleichsstudie: Wir bauen schrittweise fortgeschrittene Retrieval-Techniken ein und weisen bei jeder mit Zahlen nach, ob und wo sie die vorige Stufe schlägt. Das Endergebnis ist eine Vergleichstabelle plus Auswertung, welche Technik bei welchem Fragetyp wie viel bringt, inklusive Kosten und Latenz.

## 2. Wie du arbeitest (verbindlich)

Du arbeitest strikt in Zyklen. Pro Zyklus gilt:

1. Du baust nur den Umfang des aktuellen Zyklus. Kein Vorgreifen, kein eigenmächtiges Erweitern.
2. Du misst das Ergebnis mit den definierten Metriken und loggst die Zahlen in `results.md`.
3. Am Ende gibst du eine kurze Zusammenfassung nach dem Report-Template (Abschnitt 6).
4. Dann stoppst du und wartest auf meine Freigabe. Ich sage "passt" oder "passt nicht". Erst bei "passt" geht es weiter.
5. Bei "passt nicht" arbeitest du das Feedback im selben Zyklus ein und meldest dich erneut.

Wenn du eine Designentscheidung treffen musst, die nicht im Plan steht, triffst du die kleinstmögliche und nennst sie in der Zusammenfassung als offene Entscheidung. Du änderst nichts an bereits freigegebenen Zyklen, ohne vorher zu fragen.

## 3. Eiserne Prinzipien

- Korpus zuerst. Keine Retrieval-Technik wird gebaut, bevor Korpus und Golden-Eval-Set stehen (Zyklus 0).
- Alles wird gemessen. Eine Technik bleibt nur, wenn sie ihr Delta gegen die Vorstufe nachweist. Bringt sie nichts oder verschlechtert sie, fliegt sie raus und das wird so dokumentiert.
- Eine neue Technik pro Zyklus. Niemals mehrere Änderungen bündeln, sonst ist das Delta nicht zuordenbar.
- Ehrliche Eval. Kein Cherry-Picking, keine geschönten Zahlen. Immer Stichprobengröße nennen. Bei kleinem Eval-Set vorsichtig formulieren ("deutet auf", nicht "beweist").
- Reproduzierbar. Gepinnte Dependencies, fester Seed wo möglich, dokumentierte Datenquellen.
- Pro Fragetyp auswerten, nicht nur global. Eine Technik kann global neutral wirken, aber bei einem Fragetyp stark gewinnen.

## 4. Tech-Stack (Default, Abweichung nur mit Begründung)

- Sprache: Python, requirements gepinnt.
- Vektor-Store: Qdrant (native Hybrid-Suche).
- Embeddings: BGE-M3 (liefert dense, sparse und Multi-Vector aus einem Modell, deckt deutschen Korpus ab). Falls die Qualität auf echten Daten nicht reicht, Alternative dokumentieren.
- Reranker: ein Cross-Encoder (z.B. bge-reranker-v2 oder Qwen3-Reranker).
- Visuelles Retrieval: colpali-engine (ColPali / ColQwen).
- Eval: RAGAS oder DeepEval.
- Generierungs-LLM: via API, Modell konfigurierbar.

## 5. Die Zyklen

### Zyklus 0: Setup und Fundament
Ziel: Projekt steht, Korpus steht, Messbarkeit steht.
Aufgaben:
- Repo-Struktur, virtuelle Umgebung, gepinnte Dependencies, `.env`-Vorlage.
- Korpus beschaffen und in `data/` ablegen. Quellen, Lizenz und Umfang in `CORPUS.md` dokumentieren. Mischung sicherstellen: Fließtext-Reports, Tabellen, visuelle Statblätter.
- Korpus-Größe in Token messen und in `CORPUS.md` festhalten. Explizit prüfen und beantworten: Ist der Korpus groß genug, dass RAG überhaupt nötig ist, oder passt alles in ein Long-Context-Fenster? Wenn zu klein, als Stopp-Kandidat melden.
- Golden-Eval-Set bauen: 30 bis 50 Queries mit jeweils bekannten relevanten Chunks bzw. Soll-Antworten. Im Set nach Typ markiert: semantisch, exact-match (Namen/Metriken), multi-hop (Vergleiche), visuell (Charts). Ablage in `eval/golden_set.jsonl`.
- `results.md` mit leerer Vergleichstabelle anlegen.
Definition of Done: Dependencies installierbar, Korpus dokumentiert, Token-Check beantwortet, Golden-Set vorhanden und nach Typ markiert.

### Zyklus 1: Baseline (naive Vektor-RAG)
Ziel: die Zahl, die alle weiteren Zyklen schlagen müssen.
Aufgaben:
- Chunking, dense Embeddings (BGE-M3 dense), Top-k Vektorsuche, Kontext in den Prompt, Antwort generieren.
- Gegen das Golden-Set messen: Context Recall, Context Precision, Faithfulness, Answer Relevancy, plus Pass@k für Retrieval. Pro Fragetyp aufschlüsseln.
- Zahlen in `results.md` eintragen.
Definition of Done: Baseline läuft end-to-end, Metriken global und pro Fragetyp geloggt.

### Zyklus 2: Hybrid (dense + sparse + RRF)
Ziel: die exact-match-Schwäche der reinen Vektorsuche schließen.
Aufgaben:
- Sparse/BM25 ergänzen, Ergebnisse via Reciprocal Rank Fusion mit dense kombinieren.
- Delta gegen Zyklus 1 messen, besonders auf dem exact-match-Subset.
Definition of Done: Delta dokumentiert, klar benannt wo Hybrid hilft und wo nicht.

### Zyklus 3: Reranking
Ziel: Ranking-Qualität der Top-Treffer verbessern.
Aufgaben:
- Cross-Encoder-Reranker über die Top-N, dann Top-k an den Generator.
- Delta gegen Zyklus 2 messen (vor allem Context Precision).
Definition of Done: Delta dokumentiert, Latenzkosten des Rerankers notiert.

### Zyklus 4: Contextual Retrieval
Ziel: kontextlose Chunks (z.B. nackte Tabellenzellen) retrievebar machen.
Aufgaben:
- Pro Chunk per LLM einen kurzen Kontextsatz voranstellen, vor dem Embedding und vor der BM25-Indexierung.
- Delta gegen Zyklus 3 messen.
- Ehrlicher Ablations-Check: Schlägt Contextual Retrieval die Stufe Hybrid+Reranking genug, um den Mehraufwand und die LLM-Kosten der Kontextgenerierung zu rechtfertigen? Klar beantworten.
Definition of Done: Delta und Ablations-Ergebnis dokumentiert, Kostenabschätzung dabei.

### Zyklus 5: Visuelles Retrieval (ColPali / ColQwen)
Ziel: der Show-Off. Visuelle Statblätter direkt als Bild retrieven, ohne OCR und ohne Chunking.
Aufgaben:
- Visuelle Seiten (Radar-Charts, Heatmaps, Pizza-Plots, Statblätter) als Bilder mit colpali-engine indexieren, Late-Interaction-Retrieval.
- Treffer als Bilder an ein VLM zur Generierung geben.
- Delta gezielt auf dem visuellen Subset messen.
Definition of Done: visueller Pfad läuft, Delta auf visuellem Subset dokumentiert, Infrastruktur- und Tokenkosten notiert.

### Zyklus 6 (optional): Agentic RAG
Auslöser: nur bauen, wenn multi-hop-Fragen (Vergleiche, "finde ähnliche Spieler") in der Eval nachweislich schwach laufen.
Aufgaben:
- Query-Decomposition, iteratives Nachladen, Self-Correction (CRAG-Stil) für mehrstufige Fragen.
- Delta auf dem multi-hop-Subset messen, Latenzaufschlag notieren.
Definition of Done: Delta auf multi-hop-Subset dokumentiert, Aufwand-Nutzen klar.

### Zyklus 7 (optional, nur bei echtem Bedarf): GraphRAG
Auslöser: nur, wenn globale Fragen ("alle Spieler mit Verbindung zu Spielstil Z über den ganzen Korpus") gebraucht werden und Provenienz wichtig ist. Warnung: Indexing ist teuer, vorher klein testen.
Aufgaben:
- Entity-Graph bauen (Spieler, Club, Liga, Position, Spielstil), graph-gestütztes Retrieval.
- Delta auf globalen und multi-hop-Fragen messen.
Definition of Done: Delta dokumentiert, Kosten ehrlich gegen den Nutzen gestellt.

### Abschluss: Auswertung und Story
Ziel: das Portfolio-Artefakt.
Aufgaben:
- `results.md` zu einer Vergleichstabelle verdichten: Technik gegen Fragetyp, Deltas, Kosten, Latenz.
- Kurze Auswertung schreiben: welche Technik wo gewonnen hat, was sich nicht gelohnt hat, ehrliche Limitationen (Eval-Größe, fehlende Inter-Rater-Prüfung etc.).

## 6. Report-Template (am Ende jedes Zyklus)

```
## Zyklus N: [Name] — Zusammenfassung

Gebaut: [1-3 Sätze, was konkret entstanden ist]

Metriken (global): [Context Recall, Precision, Faithfulness, Answer Relevancy, Pass@k]
Metriken pro Fragetyp: [kurze Aufschlüsselung]
Delta zur Vorstufe: [+/- pro Metrik, kurz interpretiert]

Kosten/Latenz: [falls relevant]
Offene Entscheidungen: [was ich selbst entschieden habe oder von dir brauche]
Empfehlung: [behalten / verwerfen / anpassen, mit Begründung]

Warte auf Freigabe.
```
