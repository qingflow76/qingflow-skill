# Q-Linker Builder Notes

## What Builder Should Configure

- `remoteLookupConfig`
- alias parsing
- target field binding
- auto trigger
- custom button text

For current AppForm declarations, use `config.qLinkerBinding` from the pinned field Schema. The snake_case `q_linker_binding` name is a compatibility shorthand used by the high-level builder layer.

## Current Supported Scope

- custom mode only
- standard request fields
- alias path parsing
- target field binding to existing ordinary fields

## Recommended Public APIs For Samples

### Httpbin

- URL: `https://httpbin.org/get`
- Good for:
  - query echo
  - request URL echo

Useful paths:
- `$.args.keyword`
- `$.url`

### Open-Meteo Geocoding

- URL: `https://geocoding-api.open-meteo.com/v1/search`
- Good for:
  - place normalization
  - country
  - lat/lng summary

Useful paths:
- `$.results[0].name`
- `$.results[0].country`
- `$.results[0].latitude`
- `$.results[0].longitude`

## Target Field Rules

Required:
- every `outputs[*].target_field` must point to an existing field

Prefer:
- text
- long text
- number
- amount
- date
- datetime
- single select
- multi select
- boolean

Avoid:
- q_linker
- code_block
- relation
- subtable
- attachment
- member
- department
- address

## Safe Verification

- `qingflow builder app get ... fields`
- `qingflow record schema insert`
- `record_insert`

This verifies that the configuration does not break the form page, even before runtime execution is tested.
