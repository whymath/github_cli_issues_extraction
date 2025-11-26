# GitHub CLI Issues Extraction

This is a repository with some simple steps to download and extract data from a GitHub repository using the GitHub CLI. The reference documentation for the CLI is available here - https://cli.github.com/manual/gh_issue_list.


### STEP 1:
Authorize your local folder:

`gh auth login`


### STEP 2:
Run the following commands to download issues data:

`gh api -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28" --paginate "/repos/UKGovernmentBEIS/inspect_evals/issues?state=all&per_page=100" > issues9.json`

Alternatively, run the following command to download PRs data:

`gh api -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28" --paginate "/repos/UKGovernmentBEIS/inspect_evals/pulls?state=all&per_page=100" > prs9.json`


Note that the above commands were executed on a Windows PowerShell / Command Prompt, and might need some modifications for Unix-based systems.


### STEP 3:
Update the `json_file_name` variable at the bottom of `json_to_csv_converter.py`.

Run `json_to_csv_converter.py` file
