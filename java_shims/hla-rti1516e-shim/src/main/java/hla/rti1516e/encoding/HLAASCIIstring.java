package hla.rti1516e.encoding;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;

public class HLAASCIIstring implements DataElement {
    private final String value;

    public HLAASCIIstring(String value) {
        this.value = value == null ? "" : value;
    }

    public String getValue() {
        return value;
    }

    public byte[] toByteArray() {
        byte[] payload = value.getBytes(StandardCharsets.US_ASCII);
        ByteBuffer buffer = ByteBuffer.allocate(4 + payload.length);
        buffer.putInt(payload.length);
        buffer.put(payload);
        return buffer.array();
    }
}
