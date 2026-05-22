# QRoPE Stage 111 Provider SDK Backend Discovery

Stage 111 adds a no-submission provider SDK and optional backend discovery gate for the noisy-hardware robustness lane.

The gate reads Stage 106 results and checks whether the provider SDK dependencies needed for execution are present locally:

- IBM Runtime: `qiskit`, `qiskit_ibm_runtime`
- Amazon Braket: `braket`, `boto3`

By default it does not contact provider APIs. With `--allow-live-discovery`, it may use configured local credentials to perform non-secret provider/backend discovery, still without submitting hardware jobs.

The current purpose is to distinguish three failure modes before Stage 107 execution:

- Stage 106 policy/configuration blockers;
- missing optional provider SDKs;
- live provider/backend availability failures.

Current expected decision before full configuration and SDK installation:

`PROVIDER_SDK_BACKEND_DISCOVERY_BLOCKED`

This gate does not submit circuits, fill calibration counts, fill matched packet counts, or support a noisy-hardware robustness claim.
