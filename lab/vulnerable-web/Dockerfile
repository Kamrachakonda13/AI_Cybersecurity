# Lab target image: Flask app as unprivileged `nobody`, no attack tooling inside.
# Help: hardened by compose (`cap_drop: ALL`, read-only, cpu/mem caps). Red team
# attacks this container FROM outside; nobody shells into it.
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 4101
# Unprivileged, no curl/nmap tooling inside target — red team attacks FROM outside container
USER nobody
CMD ["python", "app.py"]
