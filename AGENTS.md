### Preface
slang is a python translations generator utility that generates typesafe interface 
for translations.

### Development
- we use `uv` as a package manager
- we use `task` for common commands (remember that task commands run by default just for the current project in the 
monorepo unless it explicitly says otherwise {usually will be named x_all})
- we use `pytest` for testing
- we write unit tests for every feature we add (make sure it fails first)

### Code style
- We write type safe Python (using annotations)

## Definition of Done

- A task is not done unless `task test` + `task lint` passed
