# alarm-clock-cli

A terminal-based alarm clock. Set one or more alarms, leave `alarm run` open
in a terminal, and it rings (sound + message) when they're due.

```
$ alarm add 07:30 --label "Standup" --repeat daily
Added alarm e3fa8a17: 07:30 (daily) - Standup

$ alarm list
ID        TIME   REPEAT  STATUS  LABEL
e3fa8a17  07:30  daily   on      Standup

$ alarm run
Alarm clock running. Press Ctrl+C to stop.
ALARM! 07:30 - Standup
Press Enter to dismiss, or 's' + Enter to snooze:
```

## Why it looks the way it does

This was built for a 30-minute take-home exercise ("build an alarm clock as
a CLI, no web UI, no DB — decide the scope yourself"). This section is the
requirements/design pass I did *before* writing code, kept here rather than
thrown away, since the brief asked to show that thinking.

### Clarifying questions I'd normally ask a stakeholder

Since there was no one to ask, I answered these myself and treated the
answers as the spec:

1. **Does "alarm clock" mean one alarm, or a manager for several?**
   → Several — that's the realistic use case (weekday wake-up + a couple of
   reminders) and it's barely more code than one.
2. **Does it need to work when the terminal is closed?**
   → No. A real background service (systemd timer, Windows Task Scheduler,
   `launchd`) is the right tool for that, but wiring one up eats the whole
   budget on plumbing instead of the actual alarm logic. Explicitly out of
   scope; noted below.
3. **One-off alarms, or recurring ones?**
   → Both — "once" and "daily" are the common cases, plus specific weekdays
   (e.g. `mon,wed,fri`) since a work-days-only alarm is a very typical need.
4. **Does state need to survive a restart?**
   → Yes — losing your alarms every time you close the terminal would make
   this useless. Simple durable storage, not in-memory only.
5. **How does the user turn an alarm off when it's ringing?**
   → Dismiss or snooze, both very standard behavior for an alarm clock.

### Requirements

**Functional**
- Add an alarm: time (24h `HH:MM`), optional label, repeat mode
  (`once` / `daily` / comma-separated weekdays).
- List alarms (with id, time, repeat, on/off status, label); optionally
  include disabled ones.
- Remove, enable, disable an alarm by id.
- Watch for due alarms in the foreground (`alarm run`) and ring: audible
  beep + printed message, until dismissed or snoozed (default 5 min,
  configurable).
- Alarms persist across runs.

**Non-functional**
- CLI only, stdlib only (no runtime dependencies) — keeps it installable
  and reviewable in the exercise's time box.
- Clear, scriptable output; non-zero exit codes on error (unknown id, bad
  input) so it composes in shell scripts.
- Cross-platform-ish: sound uses `winsound` on Windows and falls back to
  the terminal bell elsewhere, since the target machine is Windows but the
  core logic shouldn't be Windows-only.

**Explicit non-goals** (cut for scope, not by accident)
- No background/daemon mode or OS-level scheduled task integration —
  `alarm run` must stay in an open terminal.
- No timezone handling beyond the host's local clock.
- No multi-user support.
- No GUI/notification-center integration.

### Design decisions

| Decision | Alternative considered | Why this way |
|---|---|---|
| JSON file in `~/.alarm_clock/alarms.json` | SQLite | A handful of alarms is not a database problem; JSON is human-inspectable, trivial to test, and needs no schema/migration story. |
| Foreground polling loop (`run`), 1s tick by default | OS-level scheduler (cron / Task Scheduler) | Keeps the whole thing in Python and testable; a real deployment would eventually want OS integration, but that's a separate, larger piece of work (see non-goals). |
| Store re-reads/writes the whole file per operation | In-memory cache with periodic flush | Simpler, and correct-by-construction (no cache invalidation bugs) at this scale. Would revisit if alarm counts were large. |
| Alarm id = short UUID (8 hex chars) | Sequential integer | Stable across removals, no risk of id reuse/collisions if the file is edited by hand. |
| Ringing runs the beep on a background thread while `input()` blocks on the main thread | `select`/non-blocking stdin polling | `select` on stdin doesn't work on Windows; a simple thread + blocking `input()` is portable and easy to read. |
| Dedup guard: `last_triggered` stores the exact minute an alarm fired | Track a boolean "fired today" | Works uniformly for `once`, `daily`, and weekday alarms without extra date bookkeeping, and naturally resets each new minute. |

### Architecture

```
alarm_clock/
  models.py   Alarm dataclass + is_due() — the only "business logic"
  store.py    AlarmStore — JSON persistence, CRUD, due-alarm queries
  sound.py    play_sound() — the one platform-specific seam
  cli.py      argparse wiring, table printing, the run/ring loop
  __main__.py  `python -m alarm_clock` entry point
```

Kept as four small modules instead of one script so `models`/`store` (the
parts with actual logic) can be unit-tested without touching argparse,
threading, or real time — that's most of the test suite.

## Install & run

```
pip install -e .
alarm --help
```

(or, without installing: `python -m alarm_clock --help`)

```
alarm add 07:30 --label "Standup" --repeat daily
alarm add 09:00 --repeat mon,wed,fri --label "Gym"
alarm add 14:00                      # one-off, defaults to --repeat once
alarm list                           # hides disabled/used-up alarms
alarm list --all                     # shows everything
alarm disable <id>
alarm remove <id>
alarm run                            # foreground watcher; Ctrl+C to stop
alarm run --snooze 10                # snooze duration in minutes
```

## Testing

```
pip install -r requirements-dev.txt
pytest
```

18 tests cover: due-time logic for `once`/`daily`/weekday alarms, the
same-minute refire guard, JSON persistence (add/remove/enable/disable,
survives reload), and the dismiss-vs-snooze branch of the ring loop
(sound mocked out, no real waiting).

## How AI was used

I used Claude to pressure-test the requirements above before writing any
code — walking through the clarifying questions, the scope cuts, and the
storage/threading tradeoffs in the design table — then to generate the
implementation from that agreed design. I reviewed and validated the
output by: running the full CLI by hand (add/list/enable/disable/invalid
input), writing and running the test suite, and checking the design
choices against the stated constraints (stdlib-only, CLI-only, works on
the target Windows machine) rather than accepting them by default.

## If I had more time

- A `--daemon`/install-as-scheduled-task mode so alarms fire without a
  terminal open.
- A config option for sound (custom `.wav`, volume, silent/notification-only
  mode).
- `alarm edit <id>` instead of remove+re-add.
- Structured JSON output (`--json`) for scripting.
