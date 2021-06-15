def get_sessions():
    sessions = [
	{
		"id": "b1281026-ee55-42b8-86e0-fdd604307e2c",
		"path": "sm-studio-lifecycle-config-samples/Untitled.ipynb",
		"name": "Untitled.ipynb",
		"type": "notebook",
		"kernel": {
			"id": "8b71da19-872e-4f5b-b17c-77dfdd352880",
			"name": "python3__SAGEMAKER_INTERNAL__arn:aws:sagemaker:us-west-2:236514542706:image/datascience-1.0",
			"last_activity": "2021-06-14T19:34:13.627524Z",
			"execution_state": "idle",
			"connections": 1,
			"instance_type": "ml.t3.medium",
			"app_name": "datascience-1-0-ml-t3-medium-fbbacbd136ea35c00e5ce9203df8"
		},
		"notebook": {
			"path": "sm-studio-lifecycle-config-samples/Untitled.ipynb",
			"name": "Untitled.ipynb"
		}
	}]
    return sessions

def get_terminals():
    terminals = [
	{
		"name": "1"
	},
	{
		"name": "2"
	},
	{
		"name": "3"
	},
	{
		"name": "4"
	},
	{
		"name": "5"
	},
	{
		"name": "arn:aws:sagemaker:us-west-2:236514542706:image/datascience-1.0__1__ml.t3.medium"
	},
	{
		"name": "arn:aws:sagemaker:us-west-2:236514542706:image/datascience-1.0__2__ml.t3.medium"
	}]
    return terminals

def get_apps():
    apps = [
	{
		"app_name": "tensorflow-2-3-cpu-py-ml-t3-medium-bb1b683388c545cc7791768635d8",
		"environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.3-cpu-py37-ubuntu18.04-v1",
		"environment_name": "tensorflow-2.3-cpu-py37-ubuntu18.04-v1",
		"image_name": "tensorflow-2.3-cpu-py37-ubuntu18.04-v1",
		"instance_type": "ml.t3.medium"
	},
	{
		"app_name": "tensorflow-2-1-cpu-py-ml-t3-medium-cd513c89e61979ed5077457d553a",
		"environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-2.1-cpu-py36",
		"environment_name": "tensorflow-2.1-cpu-py36",
		"image_name": "tensorflow-2.1-cpu-py36",
		"instance_type": "ml.t3.medium"
	},
	{
		"app_name": "datascience-1-0-ml-t3-medium-fbbacbd136ea35c00e5ce9203df8",
		"environment_arn": "arn:aws:sagemaker:us-west-2:236514542706:image/datascience-1.0",
		"environment_name": "datascience-1.0",
		"image_name": "datascience-1.0",
		"instance_type": "ml.t3.medium"
    }]
    return apps
