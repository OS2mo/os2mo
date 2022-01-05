Release type: patch

[#47784] Temporarily remove heavy metrics

We have discovered that metrics are being updated on EVERY REQUEST against MO!
Not just on requests against the /metrics endpoint, as we had imagined.

This means that every single request against MO results in 5 requests to other systems.
Among these is a request to DAR, which means that MOs minimum request response-time is the round-trip time to DAR.

This change temporarily disables these 5 metrics, with a plan to reintroduce them later.
