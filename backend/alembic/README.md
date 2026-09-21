# VEYRA v4.0 database migrations

Production deployments should use Alembic rather than relying on `create_all`.

```bash
cd backend
alembic upgrade head
```

The application still uses `create_all` for local/demo bootstrap compatibility. For production, run migrations before starting the API and disable automatic schema creation after the migration path has been adopted by the deployment platform.
