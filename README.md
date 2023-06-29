# Genius Invokation TCG simulator

---

Backend of Genius Invokation TCG, written with Python and Pydantic.

This project is created for killing time.
No guarantee for progress and quality.

## feature

pydantic to save & load states of match, exported data is complete to restore 
from certain state and continue running.

interact by request and response. when request list is not empty, agents need
to response to one of the request. when multiple players need to response,
their requests will appear simultaneously.

all changes to the match table is done by actions. every action will generate
a event and may activate new actions. use lists of action list to deal with 
chain events and actions. 

use a register to trigger events from objects. when new object is generated, 
it will be registered to the register, get unique id, and register event
handler.

TODO: how to decide order when trigger multiple events. how to get 
self-condition, e.g. Lightning Stiletto card generated from Keqing, will 
disappear when Keqing uses her skill again. However, if it is switched into
deck by other cards, it will not disappear.

current dicision: every object will record its position. when position changed,
update the position. 
