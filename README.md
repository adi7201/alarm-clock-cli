#MVP

1. Add Alarm
2. List alrams
3. Delete Alarms
4. start the alarm scheduler.
5. Trigger Alarm
6. validate input

Assumptions

1. Local system time
2. 24- hour format : HH:MM
3. Terminal Notification 

##Project-structure 

   alarm-clock-cli
      |
      alarm-clock
        -cli.py (user interaction)
        -models.py (alarm structure ( id, time, label))
        -service.py(buisness logic)
        -scheduler.py(time monitoring)
        -trigger.py(notification)

      data
       - alarm.json

      test 
       - test_service.py
       - test_scheduling.py 

    Readme.md (requirements)