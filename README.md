# Genius Invokation TCG simulator

---

Backend of Genius Invokation TCG, written with Python and Pydantic.

This project is created for killing time.
No guarantee for progress and quality.

## feature

pydantic to save & load states of match, exported data is complete to restore 
from certain state and continue running, and also easy for frontend to render
the game states.

interact by request and response. when request list is not empty, agents need
to response to one of the request. when multiple players need to response,
their requests will be generated simultaneously.

all changes to the match table is done by actions. every action will generate
a event and may activate new actions, and new action lists are added to the
top of all actions. It looks like a stack of lists of actions.
