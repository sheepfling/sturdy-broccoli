package hla.rti1516e.encoding;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;

public class HLAunicodeString implements DataElement {
    private final String value;

    public HLAunicodeString(String value) {
        this.value = value == null ? "" : value;
    }

    public String getValue() {
        return value;
    }

    public byte[] toByteArray() {
        byte[] payload = value.getBytes(StandardCharsets.UTF_16BE);
        ByteBuffer buffer = ByteBuffer.allocate(4 + payload.length);
        buffer.putInt(payload.length / 2);
        buffer.put(payload);
        return buffer.array();
    }
}
