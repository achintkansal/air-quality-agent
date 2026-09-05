                         AIR QUALITY AGENT
                              SYSTEM
                                │
                                ▼
                    ┌──────────────────────┐
                    │     master.db        │
                    │                      │ (OpenAQ.org)
                    │ Historical data for  │
                    │ Mumbai / Delhi / Pune│
                    └──────────┬───────────┘
                               │
                               │ 
                               │   Data Push Process 
                               |     Reads master.db 
                               |     and inserts new data
                               |     every ~10 min
                               ▼
                    ┌──────────────────────┐
                    │      live.db         │
                    │                      │
                    │      readings        │
                    │ ┌──────────────────┐ │
                    │ │ city             │ │
                    │ │ station          │ │
                    │ │ parameter=pm25   │ │
                    │ │ value            │ │
                    │ │ timestamp        │ │
                    │ └──────────────────┘ │
                    └──────────┬───────────┘
                               │
                               │ New reading
                               ▼
              ┌─────────────────────────────────┐
              │          agent.py               │
              │                                 │
              │ Continuously watches live.db    │
              │ and processes ONLY new readings│
              └────────────────┬────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      model.py        │
                    │                      │
                    │ Anomaly Detection    │
                    └──────────┬───────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
          ┌──────────────────┐   ┌──────────────────┐
          │   baseline.py    │   │    trend.py      │
          │                  │   │                  │
          │ Recent PM2.5     │   │ Sustained upward │
          │ mean + stddev    │   │ trend detection  │
          └────────┬─────────┘   └────────┬─────────┘
                   │                      │
                   └──────────┬───────────┘
                              ▼
                    ┌──────────────────────┐
                    │ Detection Verdict    │
                    │                      │
                    │ NORMAL               │
                    │ SPIKE                │
                    │ SUSTAINED_TREND      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  state_manager.py    │
                    │                      │
                    │ Deduplication +      │
                    │ Recovery detection   │
                    └──────────┬───────────┘
                               │
               ┌───────────────┼────────────────┐
               ▼               ▼                ▼
        ┌────────────┐  ┌──────────────┐  ┌──────────────┐
        │ FIRED      │  │ SUPPRESSED   │  │ RECOVERED    │
        │            │  │              │  │              │
        │ New alert  │  │ Duplicate /  │  │ Bad state →  │
        │ generated  │  │ normal state │  │ normal state │
        └─────┬──────┘  └──────┬───────┘  └──────┬───────┘
              │                │                  │
              └────────────────┼──────────────────┘
                               ▼
                     ┌─────────────────────┐
                     │      live.db        │
                     │                     │
                     │  notification_state │
                     │  event_log          │
                     │  agent_cursor       │
                     └──────────┬──────────┘
                                │
                                │ if FIRED
                                ▼
                     ┌─────────────────────┐
                     │ generate_message()  │
                     │                     │
                     │ Creates subject +   │
                     │ notification text   │
                     └──────────┬──────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │     Notification    │
                     │                     │
                     │ Printed/generated   │
                     │ alert message       │
                     └─────────────────────┘