# Product-Agnostic Aggregator Site

This project is a small FastAPI website for publishing searchable listings such as bikes, cameras, rentals, jobs, or any other product family. It includes:

- A public, server-rendered home page at `/`.
- API documentation at `/docs`.
- Basic admin pages at `/admin`.
- A database-backed product-family and attribute setup flow.
- A friendly interactive setup helper for non-technical users.
- A Dockerfile so the same site can be deployed to AWS, Google Cloud, or Azure.

## Who this guide is for

Use this README if you are starting from a completely new computer or a completely new cloud account. The instructions avoid assumptions and show both macOS/Linux **bash** commands and Windows **Command Prompt / PowerShell** commands where they differ.

## What you need before you start

Install these first:

1. **Python 3.11 or newer** from <https://www.python.org/downloads/>.
   - On Windows, tick **Add Python to PATH** during installation.
2. **Git** from <https://git-scm.com/downloads>.
3. **Docker Desktop** from <https://www.docker.com/products/docker-desktop/> if you plan to deploy to a cloud provider.
4. A code editor, for example Visual Studio Code.
5. For cloud deployment: an AWS, Google Cloud, or Azure account with billing enabled.

## Fastest setup for non-technical users

Open a terminal in this project folder and run the interactive helper. It explains each step and waits for you before continuing.

### macOS or Linux bash

```bash
python3 scripts/setup_site_interactive.py
```

If your computer uses `python` instead of `python3`, run:

```bash
python scripts/setup_site_interactive.py
```

### Windows Command Prompt or PowerShell

```cmd
py scripts\setup_site_interactive.py
```

If `py` is not available, run:

```cmd
python scripts\setup_site_interactive.py
```

The helper can:

1. Create the Python virtual environment.
2. Install the required packages.
3. Ask what kind of listing site you want to create.
4. Create the database tables and searchable fields.
5. Start the website locally.
6. Walk you through AWS, Google Cloud, or Azure deployment.

## Manual local setup from scratch

Follow this section if you prefer to type each command yourself.

### 1. Open the project folder

```bash
cd /path/to/aggregator
```

On Windows, the command may look like:

```cmd
cd C:\path\to\aggregator
```

### 2. Create a private Python environment

This keeps the site's Python packages separate from the rest of your computer.

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```cmd
py -m venv .venv
.venv\Scripts\activate
```

### 3. Install packages

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create your first site category

Example for a bike listing site:

```bash
python scripts/setup_aggregator.py --product bikes --attributes brand,model,year,price,cc,mileage,features,owners,km_run --with-frontend
```

Example for a camera listing site:

```bash
python scripts/setup_aggregator.py --product cameras --attributes brand,model,megapixels,sensor_type,price,features --with-frontend
```

The `--product` value is the short name for the type of listing. The `--attributes` value is the comma-separated list of fields visitors can search or filter.

### 5. Start the website

```bash
uvicorn app.main:app --reload
```

Open these pages in your browser:

- Home page: <http://127.0.0.1:8000/>
- API documentation: <http://127.0.0.1:8000/docs>
- Admin UI: <http://127.0.0.1:8000/admin>

Stop the local server by pressing `Ctrl+C` in the terminal.

## Add listings

After setup, send new listings to the API endpoint `POST /api/listings`. The easiest way to explore the form is to open <http://127.0.0.1:8000/docs>, expand `POST /api/listings`, and click **Try it out**.

Example JSON body:

```json
{
  "product_family": "bikes",
  "state": "California",
  "district": "Los Angeles County",
  "city": "Los Angeles",
  "title": "Used commuter bike",
  "description": "Good condition, recently serviced.",
  "price": 350,
  "source_name": "Manual entry",
  "source_url": "https://example.com/listing/123",
  "attributes": {
    "brand": "Trek",
    "model": "FX",
    "year": "2022",
    "features": "disc brakes"
  }
}
```

## Database configuration

By default, the app uses a local SQLite database file named `aggregator.db`. That is perfect for learning, demos, and local development.

For production, set a `DATABASE_URL` environment variable before starting the app. PostgreSQL is recommended for real deployments.

Example PostgreSQL URL format:

```text
postgresql+psycopg://USERNAME:PASSWORD@HOSTNAME:5432/DATABASE_NAME
```

If `DATABASE_URL` is not set, the app automatically falls back to SQLite.

## Docker setup

A `Dockerfile` is included so cloud services can build and run the website the same way.

Build the image locally:

```bash
docker build -t aggregator-site .
```

Run it locally:

```bash
docker run --rm -p 8000:8000 aggregator-site
```

Open <http://127.0.0.1:8000/>.

> Important: if you run the container without a managed database, it uses SQLite inside the container. Data may disappear when the container is replaced. Use `DATABASE_URL` for a real production site.

## Deploy from scratch on AWS

Recommended beginner service: **AWS App Runner**.

### AWS prerequisites

1. Create an AWS account at <https://aws.amazon.com/>.
2. Add billing information.
3. Push this project to GitHub, GitLab, Bitbucket, or AWS CodeCommit.
4. Optional but recommended: create an Amazon RDS PostgreSQL database for persistent production data.

### AWS deployment steps

1. Sign in to the AWS Console.
2. Search for **App Runner**.
3. Choose **Create service**.
4. Choose your source:
   - **Source code repository** if your code is on GitHub or another supported repository provider.
   - **Container registry** if you already built and pushed a Docker image.
5. Connect/select your repository.
6. Tell App Runner to use the `Dockerfile` in this repository.
7. Set the service port to `8000` if App Runner asks for a port.
8. Add environment variables:
   - Optional for demos: no variables needed.
   - Recommended for production: `DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@HOSTNAME:5432/DATABASE_NAME`.
9. Create the service.
10. Wait until App Runner shows a public URL.
11. Open the URL in a browser.
12. Open `https://YOUR-AWS-URL/docs` to confirm the API documentation is live.

### AWS production notes

- Use RDS PostgreSQL if you need data to survive redeployments.
- Store database passwords in AWS Secrets Manager or App Runner environment secrets rather than writing them in code.
- Add a custom domain in App Runner when you are ready to use your own website address.

## Deploy from scratch on Google Cloud Platform (GCP)

Recommended beginner service: **Cloud Run**.

### GCP prerequisites

1. Create a Google Cloud account at <https://cloud.google.com/>.
2. Create or select a project.
3. Enable billing.
4. Push this project to GitHub or another Git repository.
5. Optional but recommended: create a Cloud SQL PostgreSQL database for persistent production data.

### GCP deployment steps

1. Open the Google Cloud Console.
2. Search for **Cloud Run**.
3. Choose **Create service**.
4. Choose one of these source options:
   - **Continuously deploy from source repository** and connect your repository.
   - Or build and push a container image to Artifact Registry, then deploy that image.
5. If deploying from source, let Google Cloud build with the `Dockerfile` in this repository.
6. Set the container port to `8000` if asked.
7. Select **Allow unauthenticated invocations** if this should be a public website.
8. Add environment variables:
   - Optional for demos: no variables needed.
   - Recommended for production: `DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@HOSTNAME:5432/DATABASE_NAME`.
9. Click **Create** or **Deploy**.
10. Wait until Cloud Run shows a public service URL.
11. Open the URL in a browser.
12. Open `https://YOUR-GCP-URL/docs` to confirm the API documentation is live.

### GCP production notes

- Use Cloud SQL PostgreSQL if you need durable data.
- Store database passwords with Secret Manager rather than hard-coding them.
- Add a custom domain in Cloud Run when you are ready to use your own website address.

## Deploy from scratch on Azure

Recommended beginner service: **Azure Container Apps**.

### Azure prerequisites

1. Create an Azure account at <https://azure.microsoft.com/>.
2. Add billing information.
3. Push this project to GitHub or another Git repository.
4. Optional but recommended: create Azure Database for PostgreSQL for persistent production data.

### Azure deployment steps

1. Open the Azure Portal.
2. Create a **Resource Group** for the site.
3. Search for **Container Apps**.
4. Choose **Create Container App**.
5. Connect a container image or configure GitHub Actions to build from this repository's `Dockerfile`.
6. Set ingress to **External** or **Public** so visitors can open the website.
7. Set target port to `8000`.
8. Add environment variables:
   - Optional for demos: no variables needed.
   - Recommended for production: `DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@HOSTNAME:5432/DATABASE_NAME`.
9. Create the Container App.
10. Wait until Azure shows an application URL.
11. Open the URL in a browser.
12. Open `https://YOUR-AZURE-URL/docs` to confirm the API documentation is live.

### Azure production notes

- Use Azure Database for PostgreSQL if you need durable data.
- Store database passwords in Azure Key Vault or Container App secrets.
- Add a custom domain in Container Apps when you are ready to use your own website address.

## Troubleshooting

### `python` is not recognized

Install Python again and ensure **Add Python to PATH** is selected. On Windows, try `py` instead of `python`.

### The site starts but the browser cannot open it

Make sure the terminal running `uvicorn` is still open. The local address is <http://127.0.0.1:8000/>.

### Cloud deploy works but data disappears

You are probably using SQLite inside a temporary container. Create a managed PostgreSQL database and set `DATABASE_URL` in your cloud service.

### Port errors

Only one program can use port `8000` at a time. Stop the old server with `Ctrl+C` or run with a different port:

```bash
uvicorn app.main:app --reload --port 8001
```
