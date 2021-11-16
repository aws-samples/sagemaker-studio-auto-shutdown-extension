pip install sagemaker_studio_autoshutdown-0.1.1.tar.gz 
jlpm config set cache-folder /tmp/yarncache
jupyter lab build --debug --minimize=False
echo "#######################################################"
echo "The installation was successful. This terminal window will close in 10 seconds. Refresh your IDE to see the extension on the sidebar."
sleep 10
nohup supervisorctl -c /etc/supervisor/conf.d/supervisord.conf restart jupyterlabserver
