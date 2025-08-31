# Path collision robots simulation

An app to schedulte the next tasks in car factory

Repo have some large files, so make sure that your `git-lfs` works.


## Instalation

To run application first make sure that you have `Poetry` and `Python3.10`.
Then use below commands:

```shell
$ poetry env use python3.10
$ poetry install
$ poetry shell
(venv) $ uvicorn --host localhost --port 8000 gs_app.main:app
```