# Security policy

Please report vulnerabilities privately through GitHub's security advisory
interface. Do not include real clipboard contents, credentials, gateway tokens,
or customer data in reports.

Safe Keystroke Paste deliberately treats clipboard text as untrusted input. It
does not log or persist clipboard contents. However, synthetic input is sent to
whichever window owns keyboard focus; users must verify the target before every
transmission.
