pip install -e .
jupyter serverextension enable --py sagemaker_studio_autoshutdown

cd labextension/
jlpm
jlpm build
jupyter labextension install . --debug
nohup supervisorctl -c /etc/supervisor/conf.d/supervisord.conf restart jupyterlabserver
