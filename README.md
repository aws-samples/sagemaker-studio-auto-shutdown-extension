# Sagemaker-Studio-Autoshutdown-Extension

This JupyterLab extension automatically shuts down KernelGateway Apps, Kernels and Image Terminals in SageMaker Studio when they are idle for a stipulated period of time. You will be able to configure an idle time limit of your preference. 

Image below showcases SageMaker Studio architecture. It is critical to understand how pricing works and which components will incur cost. Instance that hosts JupyterServer app and System Terminals is free. Customers will only pay for instances with at least one KernelGateway App that is "In Service" state.

KernelGateway Apps update idle state to JupyterServer and will be deleted after the user set idle time limit is reached. Image Terminals do not report the idle state to JupyterServer. As such, we delete Image Terminals when there are no KernelGateway Apps on the instance and 5 mins of such a state has elapsed.

<img src="Studio_arch.jpg">

## Requirements

* Please ensure your JupyterLab version is >= v1.2.18 and < 2.0. You can check the version by opening a terminal window in SageMaker Studio (File > New -> Terminal) and running the following command: 'jupyter lab --version'

## Installation Instructions

There are **two options** for installing the Studio Autoshutdown Extension. 

## Option 1: JupyterLab Server-Side Extension (Recommended)
This option comes with a server-side extension only. Installation does not require Internet connection as all the dependencies are stored in the install tarball and can be done via VPCOnly mode. Include the following script in JupyterServer [Lifecycle Configuration (LCC)](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-lcc.html) or run from System terminal if you are testing - [Link](https://github.com/aws-samples/sagemaker-studio-lifecycle-config-examples/tree/main/scripts/install-autoshutdown-server-extension).

## Option 2: JupyterLab UI and Server-Side Extension
This option provides UI in JupyterLab for users to set up an idle time limit. Use this option if you have fewer users and can administer manually. This option requires Internet access as the dependencies have to be pulled down. You can automate the installation by including the following script in JupyterServer LCC - [Link](https://github.com/aws-samples/sagemaker-studio-lifecycle-config-examples/blob/main/scripts/install-autoshutdown-extension/on-jupyter-server-start.sh). If you would like to install manually, follow instructions below:

1. Open a System Terminal session in your Sagemaker Studio's Jupyter Server. (You can do this by clicking File > New > Terminal)

2. Download/Clone the current repository by running: 
```bash
git clone https://github.com/aws-samples/sagemaker-studio-auto-shutdown-extension.git
```
3. Change directory to sagemaker-studio-auto-shutdown-extension:
```bash
cd sagemaker-studio-auto-shutdown-extension
```
4. Run the following script. This step will take about 3 minutes.

```bash
./install_tarball.sh
```
5. Refresh your IDE to see the extension on the sidebar as shown in the screen shot below:

<img src="studio.png">



### Monitoring the installation across all users

You can periodically monitor to check if the extension is installed and running across all users, and get notified if it is not. Checkout the folder [extension-checker](extension-checker) for more information. This feature is only supported in IAM mode, and is not supported in SSO mode.


## Idle Time Limit Setting

*Idle time limit (in minutes)* - This parameter is to set an idle time after which the idle kernels and Apps with no active notebook sessions will be terminated. By default the idle time limit is set to 120 mins. Idle state is decided based on JupyterServer’s implementation of execution_state and last_activity metadata of the kernels. Read this for more information - When is a kernel considered idle? (https://github.com/jupyter/notebook/issues/4634)

## Limitations

1. You will need to reinstall this extension and configure the idle time limit, each time you delete your user's JupyterServer "app" and recreate it. Use JupyterServer LCC to auto install the extension upon restart.

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
#4 Ensure you are testing for shutting down KernelGateway Apps, Kernels and Image Terminals. System Terminal will not be shutdown as it does not incur cost.

### Uninstall

```bash
pip uninstall sagemaker_studio_autoshutdown
jupyter labextension uninstall sagemaker-studio-autoshutdown
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.
