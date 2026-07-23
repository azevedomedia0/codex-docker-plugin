# Image signing and verification

Prefer immutable digests:

```bash
cosign sign REGISTRY/IMAGE@sha256:DIGEST
cosign verify REGISTRY/IMAGE@sha256:DIGEST \
  --certificate-identity EXPECTED_IDENTITY \
  --certificate-oidc-issuer EXPECTED_ISSUER
```

For key-based signing, keep private keys in a managed KMS or secret store; never commit them or generate them casually in a repository.

For attestations:

- bind the predicate to the exact digest;
- identify predicate type and schema;
- verify builder identity and source revision;
- retain transparency-log evidence when applicable; and
- enforce verification at deployment separately from creation.

Signing does not prove an image is secure. It proves identity/integrity under the selected trust policy.
