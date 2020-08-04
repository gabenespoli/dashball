# Dashball

### Setup for development (with docker)

This means that you can update the code locally and you will be able to see
live changes in the browser.

1. Build the development image:
```
docker build -t churn-dashboard-us-dev -f Dockerfile.dev .
```

2. Start the container:
```
docker run -d -p 8050:8050 -v $(pwd):/app churn-dashboard-us-dev
```

3. Open http://localhost:8050 in a web browser to view the dashboard.
