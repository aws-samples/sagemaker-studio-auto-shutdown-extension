# Sagemaker-Studio-Autoshutdown-Extension

This JupyterLab extension automatically shuts down Kernels and Apps in Sagemaker Studio when they are idle for a stipulated period of time. You will be able to configure an idle time limit using the user interface this extension provides. Installation instructions are listed below.


This extension is composed of a Python package named `sagemaker_studio_autoshutdown`
for the server extension and a NPM package named `sagemaker-studio-autoshutdown`
for the frontend extension.

## Requirements

* Please ensure your JupyterLab version is >= v1.2.18 and < 2.0. You can check the version by opening a terminal window in SageMaker Studio (File > New -> Terminal) and running the following command: 'jupyter lab --version'

## Installation Steps

1. Open a Terminal session in your Sagemaker Studio's Jupyter Server. (You can do this by clicking File > New > Terminal)

2. Download/Clone the current repository by running 'git clone https://github.com/aws-samples/sagemaker-studio-auto-shutdown-extension.git'

3. Change directory to sagemaker-studio-auto-shutdown-extension

4. Run the following script

```bash
./install_tarball.sh
```
5. Refresh your IDE to see the extension on the sidebar as shown in the screen shot below:

<img src="Extension Screen Shot.png">


## Idle Time Limit Setting

*Idle time limit (in minutes)* - This parameter is to set an idle time after which the idle kernels and Apps with no active notebook sessions will be terminated. By default the idle time limit is set to 120 mins. Idle state is decided based on JupyterServer’s implementation of execution_state and last_activity metadata of the kernels. Read this for more information - When is a kernel considered idle? (https://github.com/jupyter/notebook/issues/4634)

## Limitations

1. This extension does not take open terminals into consideration. For example, if your kernels are idle for the time you configured but the terminals are not then the extension will shut down the terminals and the kernels.
2. You will have to reinstall this extension and configure the idle time limit, if you delete the JupyterServer on the AWS Console and recreate it.

## Troubleshooting

#1 Delete JupyterServer and recreate it. You can do this by selecting the User and going into User Details screen in SageMaker Studio console. It is a two step process: 1/ delete JupyterServer app. 2/ Click on "Open Studio", which will recreate JupterServer with the latest version.

#2 If you are seeing the frontend extension but it is not working, check
that the server extension is enabled:

```bash
jupyter serverextension list
```

#3 If the server extension is installed and enabled but you are not seeing
the frontend, check the frontend is installed:

```bash
jupyter labextension list
```

If it is not installed, try:

```bash
bash install_server_extension.sh
bash install_frontend_extension.sh
```

### Uninstall

```bash
pip uninstall sagemaker_studio_autoshutdown
jupyter labextension uninstall sagemaker-studio-autoshutdown
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.
