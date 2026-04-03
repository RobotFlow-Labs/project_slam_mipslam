FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md ./
RUN pip install uv && uv pip install -e ".[dev,serve]" --system
COPY . .
CMD ["python", "-m", "anima_slam_mipslam"]

