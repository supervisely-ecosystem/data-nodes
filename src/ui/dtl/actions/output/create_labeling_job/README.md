# Create Labeling Job

`Create Labeling Job` layer allows you to create labeling jobs for your team members. You can specify the reviewer, assign labelers and select classes and tags to label in node options. If there are no connected layers between the source data layer and the `Create Labeling Job` layer that alter source data or annotations then the labeling job will be assigned to the project from which the data is taken, otherwise new project will be created.

### Settings

- **Description**
  - **Labeling Job Title** - the name of the labeling job
  - **Short Description** - enter the description of the labeling job
  - **Readme** - enter the instructions for labelers
- **Members**
  - **Reviewer** - select a user to review labeling job results
  - **Labelers** - select a user or multiple users to label data
- **Classes** - select classes to label
- **Tags** - select tags to label
- **Output** - Available if there are connected layers between the source data layer and the `Labeling Job` layer that alter source data or annotations in any way. If there are no such connected layers, the labeling job will be assigned to the project from which the data is taken.
  - **Project Name** - the name of the project that will be created
  - **Dataset Name** - the name of the dataset that will be created

### Example 1. Assign to source project

There are no layers that alter source data or annotations between the source data layer and the `Labeling Job` layer, so the labeling job will be assigned to the project from which the data is taken.

<table>
<tr>
<td style="text-align:center; width:50%"><strong>Source datasets</strong></td>
<td style="text-align:center; width:50%"><strong>Source datasets after Labeling Job layer applied</strong></td>
</tr>
<tr>
<td> <img src="https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/32e6d1a5-2014-4554-818d-d24bd00d11bb" alt="Source project"/> </td>
<td> <img src="https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/d54be815-1412-40e1-82ea-82f517a6030b" alt="Existing project"/> </td>
</tr>
</table>


### Example 2. New project

There are layers that alter source data or annotations between the source data layer and the `Labeling Job` layer, so a new project will be created.

<div align="center" markdown>
<img src="https://github.com/supervisely-ecosystem/data-nodes/assets/48913536/74518c1c-ce04-4570-9df2-8030209719f6" width="35%"></img>
</div>

### JSON views

<details>
  <summary>Assign to source project</summary>
  <pre>
	  {
	  	"action": "create_labeling_job",
	  	"src": [
	  		"$filter_image_by_tag_7__true"
	  	],
	  	"dst": [],
	  	"settings": {
	  		"job_name": "dogs",
	  		"description": null,
	  		"readme": null,
	  		"user_ids": [
	  			7
	  		],
	  		"reviewer_id": 6,
	  		"classes_to_label": [
	  			"dog"
	  		],
	  		"tags_to_label": [],
	  		"create_new_project": false,
	  		"project_name": "",
	  		"dataset_name": null,
	  		"keep_original_ds": true
	  	}
	  },
  </pre>
</details>

<details>
  <summary>New project</summary>
  <pre>
    {
    		"action": "create_labeling_job",
    		"src": [
    			"$anonymize_8"
    		],
    		"dst": "New project",
    		"settings": {
    			"job_name": "cats",
    			"description": null,
    			"readme": null,
    			"user_ids": [
    				7
    			],
    			"reviewer_id": 6,
    			"classes_to_label": [
    				"cat",
    				"dog"
    			],
    			"tags_to_label": [
    				"cat",
    				"dog"
    			],
    			"create_new_project": true,
    			"project_name": "New project",
    			"dataset_name": "New dataset",
    			"keep_original_ds": false
    		}
    }
  </pre>
</details>

