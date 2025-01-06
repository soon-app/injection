# Integrations

**Integrations make it easy to connect `python-injection` to other frameworks.**

## [FastAPI](https://github.com/fastapi/fastapi)

Exemple:

```python
from fastapi import FastAPI
from injection.integrations.fastapi import Inject

app = FastAPI()

@app.get("/")
async def my_endpoint(service: MyService = Inject(MyService)):
    ...
```
