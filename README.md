# Alarm Clock CLI

A simple command-line alarm clock built with Python.

The goal of this project is to keep the implementation simple and focused on the core alarm functionality, without adding a web UI, database, or external dependencies.

## MVP

The first version focuses on the following features:

1. Add an alarm
2. List alarms
3. Delete an alarm
4. Start the alarm scheduler
5. Trigger an alarm when its time is reached
6. Validate user input

## Assumptions

To keep the scope clear, I made a few assumptions:

* The alarm uses the local system time.
* Alarm time is entered in 24-hour `HH:MM` format.
* Alarms are one-time alarms.
* Notifications are shown in the terminal.
* Alarm data is stored locally in a JSON file.

## Project Structure

```text
alarm-clock-cli/
│
├── alarm_clock/
│   ├── cli.py          # Handles command-line input and output
│   ├── models.py       # Defines the Alarm structure and validation
│   ├── service.py      # Contains the main alarm business logic
│   ├── scheduler.py    # Checks the current time for due alarms
│   └── trigger.py      # Handles terminal notifications
│
├── data/
│   └── alarm.json      # Local alarm storage
│
├── tests/
│   ├── test_service.py
│   └── test_scheduling.py
│
└── README.md
```

## How It Works

The application is split into small components so each part has a clear responsibility.

* **CLI** handles what the user enters in the terminal.
* **Service** handles creating, listing, deleting, and updating alarms.
* **Scheduler** checks the current time and finds alarms that are due.
* **Trigger** displays the notification when an alarm fires.
* **Models** define what an alarm looks like and validate the alarm time.

The CLI does not contain the main alarm logic. This keeps the business logic separate and makes it easier to test.

## Running the Application

From the project root, run:

```bash
python -m alarm_clock
```

### Add an alarm

```bash
python -m alarm_clock add 07:30 --label "Wake Up"
```

### List alarms

```bash
python -m alarm_clock list
```

### Delete an alarm

```bash
python -m alarm_clock delete 1
```

### Enable an alarm

```bash
python -m alarm_clock enable 1
```

### Disable an alarm

```bash
python -m alarm_clock disable 1
```

### Start the scheduler

```bash
python -m alarm_clock run
```

The scheduler runs in the terminal and checks for due alarms periodically. Press `Ctrl+C` to stop it.

## Testing

The project includes automated tests for the service and scheduler.

Run them with:

```bash
pytest -v
```

The tests cover:

* Adding valid alarms
* Rejecting invalid times
* Listing alarms in time order
* Deleting alarms
* Handling invalid alarm IDs
* Enabling and disabling alarms
* Finding due alarms
* Triggering due alarms
* Removing triggered one-time alarms
* Ignoring disabled alarms

The tests use temporary files, so the actual alarm data is not modified during testing.

## Design Decisions

I intentionally kept the implementation small and dependency-free.

### JSON instead of a database

For a local CLI application, JSON is enough for the required persistence. Using a database would add complexity that isn't necessary for this MVP.

### Separate scheduler and service

The scheduler is responsible for checking time, while the service handles alarm data and operations. This keeps the responsibilities separate and makes the code easier to test.

### One-time alarms

For the MVP, an alarm is removed after it triggers. Recurring alarms and snooze functionality are outside the current scope.

## Out of Scope

The following features were intentionally not included:

* Web UI
* Database
* Recurring alarms
* Snooze
* Email/SMS/push notifications
* Time zones
* Multi-user support

## Known Limitation

The alarm data is stored in a JSON file. The application is designed for simple, single-user, sequential CLI usage and does not use file locking for simultaneous processes.

## Development Approach

I followed a simple development process:

**Define → Review → Design → Implement → Test → Review → Fix → Test again**

I used AI as a development assistant to discuss the requirements, review implementation ideas, and identify potential issues. I reviewed the suggestions and made the final implementation decisions myself.

The final implementation was manually tested through the CLI as well as through automated tests.
