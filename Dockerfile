FROM nvidia/cuda:11.7.1-cudnn8-runtime-ubuntu20.04

# Install python & jupyter
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip
RUN pip3 install jupyter
RUN pip3 install torch
RUN pip3 install transformers
RUN pip3 install accelerate

# Disable security
RUN jupyter notebook --generate-config
RUN echo "c.NotebookApp.token = ''" >> $(jupyter --config-dir)/jupyter_notebook_config.py

# Set default URL
RUN echo "c.NotebookApp.default_url = '/project/'" >> $(jupyter --config-dir)/jupyter_notebook_config.py

# expose & launch
EXPOSE 8888
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--no-browser", "--allow-root"]