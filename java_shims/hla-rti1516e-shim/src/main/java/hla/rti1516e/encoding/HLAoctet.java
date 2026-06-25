package hla.rti1516e.encoding;

public class HLAoctet implements DataElement {
    private final int value;

    public HLAoctet(int value) {
        this.value = value & 0xFF;
    }

    public int getValue() {
        return value;
    }

    public byte[] toByteArray() {
        return new byte[] { (byte) value };
    }
}
