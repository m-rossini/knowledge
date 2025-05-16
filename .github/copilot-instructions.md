# Development SLDC Standards
These file describes development coding and design standards.

When thiking for answers, clarify any doubts prefereble with yes or no type of questions. Do not go wild with solutions, ask always.

Always create git repositories named as 'main'

## Python Standards
This section describes standards for python code

* Never pip individual libraries, always add them to requirements file
* Avoid print, try to use logging always
* Prefix log messages with '>' for debug, '>>' for info, '>>>' for warn, '>>>>' for error and after that add Classname::Methodname
* whenver possible avoid global variable
* Try to follow SOLID Principles when using OOP
* Specially ensure Single Principle of responsibility and Interface Segregation.
* Use desgin pattern when needed, but only if needed.
* Maintain import order according to python standards
* Format code according top PEP8
* Give meaningful variable names
* Declare variable near where they going to be used, try to minimize their scope
* Metrics are first class citizens and should be there from start, we should use prometheus for that
* Use modules to keep different concerns apart, to the point I can replace them, so low coupling and high cohesion
* Avoid librarie sif possible, pydatantic, dataclasses, pandas and numpy are ok

## Shell Script Standards
This section describes standards for shell scripts

* Be clear on info, warn and error messages, using semaphoro colors whenver possible
* Split in small functions that make things easier to read and understand
* When displaying messages try to use the ame formatting as for python

### Envrioment
* Assume Linux
* Assume ZSH
* Assume PODMAN over DOCKER
* Assume prometheus for metric
* Assume promtail and Loki for log collection

## Source Code management

When making changes avoid making extensive changes at once, go step by step, find the path with last impact and balst radio and perform the change, and after that commit that change and test. If that is OK, then go to the next and so on so forth
