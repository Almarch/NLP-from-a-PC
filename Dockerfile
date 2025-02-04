
FROM jupyter/base-notebook:latest

# Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir build
RUN pip install --no-cache-dir -r requirements.txt

# disable security (this is intended for local use)
RUN echo "c.NotebookApp.token = ''" >> /etc/jupyter/jupyter_notebook_config.py

# access project (shared volume)
WORKDIR /project
RUN echo "c.NotebookApp.default_url = '/project/'" >> /etc/jupyter/jupyter_notebook_config.py

# expose & launch
EXPOSE 8888
CMD ["start-notebook.sh"]