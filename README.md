# Dashball

### Setup for development (with docker)

This means that you can update the code locally and you will be able to see
live changes in the browser.

1. Build the development image:
```
docker build -t dashball .
```

2. Start the container:
```
docker run -d -p 8051:8051 -v $(pwd):/app --name dashball dashball
```

3. Open http://localhost:8051 in a web browser to view the dashboard.
