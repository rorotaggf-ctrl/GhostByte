
def inject_payload(carrier: str, zw_payload: str, mode: str = "paragraph") -> str:
    if not carrier.strip():
        return zw_payload

    if mode == "spaces":
        words = carrier.split(" ")
        if len(words) <= 1:
            return carrier + zw_payload

        # Teile ZW-Payload in gleichgroße Portionen pro Wortzwischenraum
        chunk_size = max(1, len(zw_payload) // (len(words) - 1))
        injected = []
        pos = 0

        for i, word in enumerate(words):
            injected.append(word)
            if i < len(words) - 1:
                chunk = zw_payload[pos:pos + chunk_size]
                injected.append(" " + chunk)
                pos += chunk_size

        if pos < len(zw_payload):
            injected.append(zw_payload[pos:])

        return "".join(injected)

    # Standard: Paragraph injection
    if "\n\n" in carrier:
        parts = carrier.split("\n\n", 1)
        return parts[0] + "\n\n" + zw_payload + parts[1]

    return carrier + "\n\n" + zw_payload