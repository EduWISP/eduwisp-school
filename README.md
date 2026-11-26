<p align="center"><img src="https://raw.githubusercontent.com/EduWISP/.github/main/branding/eduwisp-mark.svg" alt="EduWISP" height="72"></p>

# eduwisp-school

**Gestione scolastica** · *School management*

Istituti, plessi, classi, gruppi didattici, docenti, studenti e assegnazione dei dispositivi.

> 🧪 **Stato: prototipo v0.** Struttura scolastica: plessi, sezioni, anni scolastici, classi, studenti e incarichi dei docenti. La progettazione è nella [documentazione EduWISP](https://eduwisp.github.io/docs/moduli/gestione-scolastica/).

🇬🇧 *Schools, sites, classes, teaching groups, teachers, students and device assignment. **Status: design phase**, no code yet. See the [design docs](https://eduwisp.github.io/docs/en/modules/school-management/).*

## Documentazione / Documentation

- Progettazione / Design: <https://eduwisp.github.io/docs/moduli/gestione-scolastica/>
- Mappa dei repository / Repository map: <https://eduwisp.github.io/docs/architettura/repository/>
- Documentazione del modulo / Module docs: [`docs/user/`](docs/user/) · [`docs/developer/`](docs/developer/)

## Cosa contiene il prototipo / What the prototype contains

- **Plessi** con il proprio ordine di scuola: infanzia (per sezioni), primaria (5 anni), secondaria di primo grado (**3 anni**), secondaria di secondo grado (**5 anni**).
- **Sezioni** e **indirizzi** definiti liberamente da ogni istituto e da ogni plesso.
- **Anni scolastici** e **classi** (anno + sezione, per esempio 2ª B), con controllo della durata dell'ordine di scuola.
- **Studenti** con i soli dati necessari, **iscritti** a una classe per anno.
- **Incarichi dei docenti**: su una **sezione intera** (tutte le sue classi) o su una **singola classe**. Un docente può avere più classi e sezioni, una classe più docenti. Per il sostegno non si registra l'abbinamento al singolo studente (RC-013).
- `queries.classes_for_teacher()`: le classi del docente nell'anno in corso, usata dagli altri moduli per limitare le sue azioni (RF-010).
- Nessun collegamento è possibile tra dati di istituti diversi.

```bash
pip install -e ../eduwisp-users -e ".[test]"
pytest
```

## Dipendenze / Dependencies

[`eduwisp-utils`](https://github.com/EduWISP/eduwisp-utils), [`eduwisp-users`](https://github.com/EduWISP/eduwisp-users), [`eduwisp-audit`](https://github.com/EduWISP/eduwisp-audit)

## Privacy

Dati personali previsti e regole: [PRIVACY.md](PRIVACY.md). Il rispetto della normativa su privacy e minori è un vincolo bloccante ([ADR-0008](https://eduwisp.github.io/docs/decisioni/0008-conformita-normativa/)).

## Responsabile del modulo / Module owner

Cerchiamo persone che vogliano prendere in carico questo modulo! Proponiti in [Discussions](https://github.com/EduWISP/docs/discussions). / *Want to own this module? Say hi in Discussions.*

## Contribuire / Contributing

Vedi [CONTRIBUTING](https://github.com/EduWISP/.github/blob/main/CONTRIBUTING.md) e il [Codice di condotta](https://github.com/EduWISP/.github/blob/main/CODE_OF_CONDUCT.md). **Mai dati personali reali** di studenti, famiglie o personale.

## Licenza / License

**AGPL-3.0-or-later**, con termini aggiuntivi di attribuzione e tutela del nome (sezione 7): vedi [LICENSE](LICENSE) e [NOTICE.md](NOTICE.md). Chi usa o modifica EduWISP deve sempre indicare «Basato su EduWISP» e non può usare il nome e il logo per versioni modificate. Licenza scelta secondo le [linee guida AgID](https://eduwisp.github.io/docs/decisioni/0006-licenza/) per il software usato via rete.

*AGPL-3.0-or-later with additional attribution and trademark terms (section 7): see LICENSE and NOTICE.md.*

I contributi richiedono il [DCO](https://github.com/EduWISP/.github/blob/main/CONTRIBUTING.md#dco) (`git commit -s`).
