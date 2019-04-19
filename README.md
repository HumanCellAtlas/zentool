# Zentool

This command-line utility provides tools for working with ZenHub,
and synchronizing ZenHub with Google Sheets.

## Installation

```
pip install zentool
```

## Authentication

You will need programattic access to ZenHub, GitHub and Google Sheets.

### ZenHub

While logged in to ZenHub,
click your name in the bottom left hand corner of the screen,
then -> Manage Organizations -> API Tokens -> `Genrate new token`.
Note down the token you created.
In a terminal session, do:
```
export ZENHUB_API_TOKEN="the-zenhub-token-you-just-created"
```

### GitHub

Login to [GitHub](https://github.com/).
Click your face in the top right hand corner of the screen,
then -> Settings -> Developer Settings -> Personal access tokens ->
`Generate New Token`.
Note down the token you created.
In the same terminal session, do:
```
export GITHUB_API_TOKEN="the-github-access-token-you-just-created"
```

### Google Sheets

While logged in to Google,
go to https://developers.google.com/sheets/api/quickstart/python,
click `ENABLE THE GOOGLE SHEETS API`, then in the resulting dialog
click `DOWNLOAD CLIENT CONFIGURATION`
and save the file credentials.json to the working directory of your
terminal.

The first time you run zentool and try to access a spreadsheet, it
may open a browser and ask you for permission.

## Tools

### Spreadsheet Make: Dump Epics for a Repository to a Spreadsheet

* Create a new **blank** Google Sheet
* Copy its ID from the URL.  I will call this SPREADSHEET_ID below.
  The URL will look something like this docs.google.com/spreadsheets/d/**COPY THIS BIT**/edit#gid=0
* Run the `zentool spreadseet make` command:
```
zentool --repo-name GITHUB_REPO_NAME spreadsheet SPREADSHEET_ID make

e.g.
zentool --repo-name HumanCellAtlas/dcp spreadsheet 3N5tJxhLQ6e7v5IBrjH22q9k8LwISXCG make
```
This will copy all open epic IDs and their descriptions to the spreadsheet.

### Spreadsheet Sync: Retrieve Epics Status

Once you have created a spreadsheet using `spreadsheet make` or done
something equivalent by hand, you can get the tool to retrieve the
status of all issues attached to epics.  It will create a column for
each repo that has an issues attached to one of your epics, and fill
in the issue number and color code it in that column.  Yellow = open,
green = closed:
```
zentool --repo-name GITHUB_REPO_NAME spreadsheet SPREADSHEET_ID sync

e.g.
zentool --repo-name HumanCellAtlas/dcp spreadsheet 3N5tJxhLQ6e7v5IBrjH22q9k8LwISXCG sync
```

### Spreadsheet Create-issues: Create Issues as Directed by Sheet

With this command, zentool will search the spreadsheet for the "🛠"
symbol, and where it finds one, it will create an issue in the repository
of that column, reusing the title and description from the epic of this
row, and then attach it to the epic for that row.

```
zentool --repo-name GITHUB_REPO_NAME spreadsheet SPREADSHEET_ID create-issues

e.g.
zentool --repo-name HumanCellAtlas/dcp spreadsheet 3N5tJxhLQ6e7v5IBrjH22q9k8LwISXCG create-issues
```

Note that you must have adequate permissions to create the issue in
the repository, and to attach it to the epic.  In the past we have
discovered this is problematic for repositories not in your organization.

### Comment on Issues Attached to an Epic

You may add a simple comment to all of the issues attached to an epic
by running:

```
zentool --repo-name GITHUB_REPO_NAME comment EPIC_NUM "Your comment"

e.g.
zentool --repo-name HumanCellAtlas/dcp comment 123 "Your comment"
```

### Assign Issues Attached to an Epic to a Release

```
zentool --repo-name GITHUB_REPO_NAME release EPIC_NUM "RELEASE NAME"

e.g.
zentool --repo-name HumanCellAtlas/dcp release 123 "General Availability"
```
