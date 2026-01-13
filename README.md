# Travel Agent Site

Simple travel agent landing page with an interest form. Built with Flask and served in Docker. Submissions are stored in a local SQLite database so they can be persisted in a mounted volume on Unraid.

Quick start (build locally):

1. Build the image:

```powershell
docker build -t travel-agent-site .
```

If you're building from a tool that needs an explicit Dockerfile (such as Unraid's Docker build UI),
set the build context to the repo root and the Dockerfile path to `Dockerfile`.

2. Run the container (map a host folder for persistent DB):

```powershell
docker run -d -p 5000:80 -v ${PWD}/data:/app/data -e ADMIN_KEY=your_admin_key -e DB_PATH=/app/data/submissions.db --name travel-agent-site travel-agent-site
```

The form is available at `http://localhost:5000/`.

Admin view (list submissions):

Open `http://localhost:5000/admin?key=your_admin_key` and replace `your_admin_key` with the value set in `ADMIN_KEY`.

Unraid notes:
- Use the Docker build option in Unraid or build locally and push to a registry.
- Map a host folder (for example, `/mnt/user/appdata/travel-agent-site`) to `/app/data` in the container.
- Set `DB_PATH=/app/data/submissions.db` so the SQLite DB is persisted on the host.
- Expose port `80` on the container to a port of your choice on the Unraid host.

Files of interest:
- `app.py` - Flask application
- `templates/` - HTML templates
- `static/style.css` - basic styling
- `Dockerfile` and `docker-compose.yml`

Feel free to ask me to add email notifications, reCAPTCHA, or authentication for the admin view.
