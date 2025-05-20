# Development SLDC Standards
These file describes development coding and design standards.

<<<<<<< HEAD
<<<<<<< HEAD
* When thinking for answers, clarify any doubts preferably with yes or no type of questions. Do not go wild with solutions, ask always.
* Always create git repositories named as 'main'

## General Standards
This section describes general coding standards, not specific to any language
=======
* When thiking for answers, clarify any doubts prefereble with yes or no type of questions. Do not go wild with solutions, ask always.
* Always create git repositories named as 'main'

## General Standards#
This section describes general coding standards, not specif to any language
>>>>>>> f6c40d8 (Created the container environment for remote dev)
=======
* When thinking for answers, clarify any doubts preferably with yes or no type of questions. Do not go wild with solutions, ask always.
* Always create git repositories named as 'main'

## General Standards
This section describes general coding standards, not specific to any language
>>>>>>> b967599 (Apply suggestions from code review)

* Use markdown for documentation
* Use markdown for README
* Prefix log messages with '>' for debug, '>>' for info, '>>>' for warn, '>>>>' for error and after that add Classname::Methodname
* Try to follow SOLID Principles when using OOP
* Declare variable near where they going to be used, try to minimize their scope
* Give meaningful variable names
<<<<<<< HEAD
<<<<<<< HEAD
* Use design pattern when needed, but only if needed.
* Metrics are first class citizens and should be there from start, we should use prometheus for that
* Whenever possible avoid global variable
=======
* Use desgin pattern when needed, but only if needed.
* Metrics are first class citizens and should be there from start, we should use prometheus for that
* Qhenever possible avoid global variable
>>>>>>> f6c40d8 (Created the container environment for remote dev)
=======
* Use design pattern when needed, but only if needed.
* Metrics are first class citizens and should be there from start, we should use prometheus for that
* Whenever possible avoid global variable
>>>>>>> b967599 (Apply suggestions from code review)


## Python Standards
This section describes standards for python code

* Never pip individual libraries, always add them to requirements file
* Avoid print, try to use logging always
* Specially ensure Single Principle of responsibility and Interface Segregation.
* Maintain import order according to python standards
* Format code according top PEP8
* Use modules to keep different concerns apart, to the point I can replace them, so low coupling and high cohesion
<<<<<<< HEAD
<<<<<<< HEAD
* Avoid external libraries if possible, pydantic, dataclasses, pandas and numpy are ok
=======
* Avoid external libraries if possible, pydatantic, dataclasses, pandas and numpy are ok
>>>>>>> f6c40d8 (Created the container environment for remote dev)
=======
* Avoid external libraries if possible, pydantic, dataclasses, pandas and numpy are ok
>>>>>>> b967599 (Apply suggestions from code review)

## Shell Script Standards
This section describes standards for shell scripts

* Be clear on info, warn and error messages, using semaphoro colors whenver possible
* Split in small functions that make things easier to read and understand
* When displaying messages try to use the ame formatting as for python

### Envrioment
Assumptions about the current environment, in the case you do not know the answer, please ask

* Assume Linux Fedora
* Assume ZSH
* Assume PODMAN over DOCKER
* Assume prometheus for metric
* Assume promtail and Loki for log collection
* Assume Grafana for visualization


## Source Code management

<<<<<<< HEAD:.github/instructions/copilot-instructions.md
* When making changes avoid making extensive changes at once, go step by step, find the path with least impact and blast radius and perform the change, and after that commit that change and test. If that is OK, then go to the next and so on so forth
=======
* When making changes avoid making extensive changes at once, go step by step, find the path with last impact and balst radio and perform the change, and after that commit that change and test. If that is OK, then go to the next and so on so forth
>>>>>>> c0656dd (Dev env (#8)):.github/copilot-instructions.md
