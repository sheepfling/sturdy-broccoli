package hla.rti1516e.encoding;

import java.nio.ByteBuffer;
import java.util.Arrays;

public class HLAopaqueData implements DataElement {
    private final byte[] value;

    public HLAopaqueData(byte[] value) {
        this.value = value == null ? new byte[0] : Arrays.copyOf(value, value.length);
    }

    public byte[] getValue() {
        return Arrays.copyOf(value, value.length);
    }

    public byte[] toByteArray() {
        ByteBuffer buffer = ByteBuffer.allocate(4 + value.length);
        buffer.putInt(value.length);
        buffer.put(value);
        return buffer.array();
    }
}
