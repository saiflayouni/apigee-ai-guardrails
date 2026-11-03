# Recorded demonstrations

One English slide deck for Mexico and Ahlen online, and Cairo in person with Arabic/English narration. Target 30 minutes including questions, maximum 35 minutes. No live coding.

Record three clips from the real deployed application:

1. Normal inventory question: prompt, actual answer, HTTP status.
2. Direct injection: prompt, gateway rejection, relevant Apigee Debug policy before target invocation.
3. Synthetic supplier note: legitimate user request, fixture tool, callback decision, final answer. HTTP 200 can coexist with a blocked tool result.

Use new sessions and synthetic data. Do not record Authorization headers, cookies or secrets. Announce recorded clips as recorded. Save local copies for venue/network failures.

## What has and has not been demonstrated

Normal answers, a gateway prompt block and callback rejection of the synthetic note were observed. Revalidate before recording. Dedicated output-leakage and scanner-outage tests remain pending. Backend anonymous access must also be rechecked before claiming gateway bypass is closed.

The UI only knows the final response and optional `security_events`. The current `app.py` does not emit those events. `Not observed` means no detailed evidence was returned, not that a component is off. Do not animate invented successful checks.

A callback log alone does not establish complete request correlation. Capture timestamps and add server-side correlation before claiming an end-to-end trace.
