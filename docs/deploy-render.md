# Deploy Share Thoughts on Render

This demo uses the existing Dockerfile, Gunicorn, free Render PostgreSQL, WhiteNoise for static assets, and temporary local storage for uploads. No AWS account, bucket, or storage credentials are required. The frontend is served by Django. Messaging polls HTTP endpoints, so Redis, Channels, and a separate frontend service are unnecessary.

## 1. Understand the demo storage

Uploaded images and videos disappear whenever Render restarts, redeploys, or sleeps. Database records remain until the database is deleted or expires, so old posts can show missing images after a restart. Re-upload files when needed. Existing local users, posts, and uploads are not transferred automatically.

`SERVE_MEDIA=True` enables Django's basic media server even with `DEBUG=False`, specifically for this disposable demo. It is unsuitable for production traffic; use persistent object storage and dedicated media serving for a lasting deployment. Local development continues to use the existing `media/` folder.

## 2. Create the Blueprint

1. Commit and push the deployment files to the GitHub branch you want to deploy.
2. In Render choose **New → Blueprint**, connect this repository, and select that branch.
3. Use `render.yaml` at the repository root. Review the proposed resources: `share-thoughts` (free Docker web service) and `share-thoughts-db` (free PostgreSQL), both in Singapore.
4. Confirm both resources use **Free**, then deploy the Blueprint. No environment values need to be entered manually.
5. Wait for migrations and static collection to finish and the web service to become healthy. Open its assigned `https://...onrender.com` URL.

The Blueprint generates `SECRET_KEY`, connects the internal `DATABASE_URL`, enables secure cookies and HTTPS redirects, and sets the Docker command to `sh /app/render-start.sh`. No build command or separate static site is needed. The existing Docker CMD remains the development server for local Compose usage; Render overrides it.

`RENDER_EXTERNAL_HOSTNAME` is automatically added to Django's allowed hosts. Same-origin forms work without manually entering the generated URL. `/healthz/` checks database connectivity. Migrations run at startup because free services do not provide a pre-deploy command; use one web instance with this setup. A migration failure prevents startup and appears in the deploy logs.

## 3. Verify the hosted app

- Open `/healthz/` and expect `{"status": "ok"}`.
- Open `/login/` and `/admin/login/`; confirm images and admin styles load.
- Register two disposable accounts and check login/logout, a post, likes, comments, follows, and messaging.
- Upload an avatar, cover, image, and video. Reload and verify the uploaded files load.
- Redeploy, then confirm the accounts/posts still exist. Uploaded files will be gone as expected.
- Confirm HTTP redirects to HTTPS and forms submit without CSRF errors.

Password reset is disabled when `DEBUG=False`: the original tutorial implementation changes passwords without verifying account ownership. Implement verified email reset before enabling password recovery on a public deployment. This app currently does not send recovery emails.

If you need an admin account and your Render plan includes a shell, run `python manage.py createsuperuser` there. Do not place admin passwords in the Blueprint or commit them. Free services do not include a shell; normal registration is enough to exercise the app.

## Custom domains and settings

Add and verify the domain in Render, then set `ALLOWED_HOSTS` to the hostname (no scheme). For additional trusted form origins, set `CSRF_TRUSTED_ORIGINS` to comma-separated HTTPS origins. Redeploy after changing settings. Keep `TRUST_PROXY_HEADERS=True` only behind a proxy you trust to set `X-Forwarded-Proto`, such as Render.

`SECURE_HSTS_SECONDS` remains zero initially. Once HTTPS and any custom domain work, you may enable it. Keep `DATABASE_URL` empty and `TRUST_PROXY_HEADERS=False` in local development; plain HTTP and SQLite continue to work.

## Free-tier limits and cleanup

Render's free web service sleeps after 15 idle minutes, and waking it can take about a minute. Its filesystem is ephemeral. Never use local SQLite or local uploads for durable Render data. Only one free PostgreSQL database can be active per workspace. If the previous demo database is still present, remove it only if its data is no longer needed before creating this one. The free PostgreSQL database expires 30 days after creation; export anything needed before expiry. Free instance hours are shared across the workspace, including other projects. To avoid usage charges, use a workspace without a payment method. Render suspends services or disables builds when free bandwidth/build allowances run out in such workspaces. If the workspace already has a payment method, check its billing limits before proceeding: free services can still incur bandwidth/build overages.

To remove a test deployment, disconnect its Blueprint first, then delete the web service and database. Disconnecting the Blueprint alone does not delete resources.

## References

- [Render Django deployment](https://render.com/docs/deploy-django)
- [Render Blueprint reference](https://render.com/docs/blueprint-spec)
- [Render free service limits](https://render.com/docs/free)
