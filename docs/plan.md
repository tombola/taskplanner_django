# Task planner

A simple django/wagtail app that provides business logic integrations with task management services
(initially only supporting ToDoist), in order to create tasks, provide an
overview of created tasks, and respond to webhooks.

## Features

- templates for creation of groups of tasks, including subtasks
- change status of todoist task on receipt of webhook event, based on logic related to labels and
  current status

## Task group templates

A 'task group template' should be represented by a wagtail page type with a streamfield that can be used to
add tasks and subtasks (using nested streamfield blocks). Each streamfield
'task' block should have a field for labels/tags that can be added to the
todoist task.

Uses tokens when creating a task group so that the titles of each task group
instance can be differentiated. The tokens are defined in a comma-separated CharField.

Example:

Wagtail page
    - title: Chilli task template
    - tokens: SKU, VARIETYNAME
    - tasks:
      - sow {SKU} (label:sow)
      - plant {SKU} (label:plant)
      - harvest {SKU} (label:harvest)
      - process {SKU} (label:process)
          - {SKU} checked in
          - {SKU} dried

### Task Creation Form

A django form with field to select task group template and dynamically generated
fields based on the tokens defined for that 'task group template' (page).

On submission of the form the `todoist_api_python` package is used to create
corresponding tasks on ToDoist.

## Webhook endpoint

Not implemented yet
