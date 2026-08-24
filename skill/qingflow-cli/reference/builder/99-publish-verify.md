# Builder Publish And Readback Verification

Read this before reporting a builder task as finished.

## Scope

Responsible for: `builder publish verify`, readback-before-retry, partial success interpretation, and final user-facing completion wording.

Not responsible for: replacing resource-specific verification. Views, charts, portal, workflow, buttons, and associated resources still need their own apply/readback checks.

## Main chain

```text
apply result -> resource readback -> publish verify when app resources changed -> final status
```

## Readback-before-retry rule

If a write returns any of these, do not immediately replay the same write:

- timeout
- `partial_success`
- `write_executed=true`
- `safe_to_retry=false`
- readback unavailable
- backend readback 40002 after a write
- `VIEW_CUSTOM_BUTTON_READBACK_PENDING` after `custom_buttons_verified=true`

Next action:

```text
package get / app resolve / app get fields|layout|views|charts / portal get / publish verify
```

Then patch only the missing or mismatched resources.

For custom button view binding, verify through `builder app get ... views` before retrying: if the target view already shows a `CUSTOM` button with the expected text/id, treat the write as successful with delayed readback, not as a failed button creation.

## Final status decision table

Use this table before retrying or reporting to the user.

| Evidence | Meaning | Next action | User-facing wording |
| --- | --- | --- | --- |
| `status=success` and resource readback matches | Write and verification succeeded | Publish verify if the resource needs publish | "已成功，已回读验证" |
| `partial_success` plus `write_executed=true`, `safe_to_retry=false`, timeout, or readback unavailable | Write may have landed; verification is incomplete | Read back first, then patch only missing/mismatched parts | "写入已发出，回读未完全确认" |
| Validation/contract error before write, or `write_executed=false` | Write did not execute | Fix payload and retry the same resource only | "失败，原因是入参/契约错误" |
| Backend readback returns 40002/404/timeout after a write | Verification is blocked or delayed; not proof of write failure | Read package/app/portal inventory through the normal get path | "写入结果待确认，不能直接判定失败" |
| A workflow/chart/relation/portal reference required by the user request or by another created resource is missing | Build is incomplete | Create or patch the missing required resource | "部分完成，仍缺少关键资源" |
| Frontend visibility or publish status was not verified | Backend write may be done, but live visibility is unknown | Run publish verify or portal/app readback | "是否前端可见未确认" |

Short rule: **write result answers whether the write was attempted; readback answers what exists; publish/portal verification answers whether the user can see it.**

## Final report requirements

Always state:

- whether the intended write appears successful;
- which path made it successful;
- what is verified as front-end visible or published;
- what remains unverified or incomplete;
- whether further repair is needed.

Do not report "全部完成" when resources required by the user request, dependent charts, relations, portal references, or readback checks are missing. If workflow was not requested and not clearly required, say "workflow not requested/not configured" instead of treating it as a missing resource.
