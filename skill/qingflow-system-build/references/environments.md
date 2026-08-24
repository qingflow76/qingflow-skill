# Environment Switching

Use this reference before any builder-side write, repair, or verification flow.

## Step 1: Resolve the active environment

Decide explicitly whether the task targets:

- `test`: build validation, mock data, trial package creation, safe iteration
- `prod`: formal business system changes in the live environment

If the user did not specify an environment, default to `prod`.

## Test Environment

Use test for:

- first application of a new `SolutionSpec`
- trying builder apply flows end-to-end with readback verification, or `solution_install` when the user is installing an existing packaged solution
- package initialization and schema evolution experiments
- mock data creation, with at least `5` records per relevant entity unless the user asks for fewer

Builder behavior in test:

- `preflight` or `plan` is still preferred, but fast `apply` is acceptable when the user explicitly wants an end-to-end smoke test
- package creation is acceptable
- verify should read back apps, views, portal, navigation, and sample records

Known current test backend:

- use an explicitly provided non-production backend

## Production Environment

Use production for:

- changes to real business systems
- additive modifications to live packages and apps
- controlled rollout of approved solution specs

Builder behavior in prod:

- always identify the target package or app set before changing anything
- default to `preflight` or `plan` before any `apply`
- additive requirements should modify the existing package with ordinary tools by default
- if creating a new package seems necessary in prod, ask the user to confirm package creation first
- do not seed mock data unless the user explicitly approves it for production
- verify is mandatory after writes

Production guardrails:

- restate the target workspace and target package before any write
- call out whether the action creates, mutates, or deletes builder-side configuration
- if a safer read-only inspection can answer the request, do that first

## Reporting Rule

For builder work, always report:

- active environment
- target workspace
- whether the operation is `plan`, `apply`, `repair`, or `verify`
- whether it touches an existing package or creates a new one
