# Privacy — eduwisp-school

Documento vivo: va aggiornato a ogni modifica che riguarda dati personali. Riferimenti: [Quadro normativo](https://eduwisp.org/docs/sicurezza-privacy/quadro-normativo/), [Requisiti di conformità](https://eduwisp.org/docs/requisiti/requisiti/#requisiti-di-conformità).

## Dati personali previsti

- Struttura organizzativa dell'istituto.
- Appartenenza di studenti e docenti a classi e gruppi.
- Assegnazioni dei dispositivi.
- **Familiari** (ADR-0018): collegamento tra genitore, tutore o affidatario e studente, con tipo di relazione, referente, accesso attivo e data di verifica. Al massimo due collegamenti attivi per studente. Se un collegamento viene disattivato (per esempio per un provvedimento del giudice) **non si registra il motivo**.
- **Data di nascita** (ADR-0018): serve per l'età di ciascuno studente, che non dipende dalla classe (chi ripete l'anno può essere più grande dei compagni). Se ne ricavano solo le soglie di legge: **14 anni** per il consenso digitale (art. 2-quinquies del Codice privacy; L. 132/2025 per l'IA; configurabile con `EDUWISP_DIGITAL_CONSENT_AGE`, 16 negli Stati che seguono l'art. 8 del GDPR) e **18 anni** per la maggiore età. Dalla maggiore età i familiari perdono l'accesso, salvo consenso dello studente dal proprio tablet (scelta e data della scelta). La data di nascita non è mostrata a docenti e famiglie nelle app.

## Da definire prima dello sviluppo

| Dato | Finalità | Base giuridica | Conservazione | Chi vi accede |
|---|---|---|---|---|
| Collegamento familiare-studente | accesso della famiglia alle informazioni sul figlio | obbligo legale e compito di interesse pubblico (GDPR art. 6.1.c ed e), artt. 316 e 337-ter c.c. | finché lo studente è iscritto; poi da definire | la famiglia stessa, dirigente, segreteria, amministratore di sistema (registrato) |

---

🇬🇧 *Expected personal data:*

- *School organisational structure.*
- *Student and teacher membership of classes and groups.*
- *Device assignments.*
- *Adult students: only the date of majority is stored (not the birth date); families lose access unless the student consents on their tablet.*
- *Family links (ADR-0018): parent, guardian or foster carer to student, at most two active per student; the reason for disabling a link is never stored.*
