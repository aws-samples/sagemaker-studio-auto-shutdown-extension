pip install -e .
jupyter serverextension enable --py sagemaker_studio_autoshutdown
nohup supervisorctl -c /etc/supervisor/conf.d/supervisord.conf restart jupyterlabserver

