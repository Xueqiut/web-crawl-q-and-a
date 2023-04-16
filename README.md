# web-crawl-q-and-a
This is a sample sample project used to learn openai models and APIs. Find the openai's example project [here](https://github.com/openai/openai-cookbook/tree/main/apps/web-crawl-q-and-a)

# Package manager - poetry
Package set up
- Resolve the dependencies: `poetry install`
- Add new dependencies: `poetry add ***`
- Build and distribute package: `poetry build`

# Unit test framework - pytest
Run unit test
- Run all the test cases with auto discovery: `poetry run pytest`
- Run single test case: `poetry run pytest -k test_case_name`

# How does this work
```
- poetry run python3 crawler/crawl.py
- poetry run python3 embeddings/source_embeddings.py
- poetry run python3 q-and-a/question_and_answer.py
```