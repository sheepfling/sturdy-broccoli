package hla.rti1516e.encoding;

public class EncoderFactory {
    public HLAASCIIstring createHLAASCIIstring() {
        return new HLAASCIIstring("");
    }

    public HLAASCIIstring createHLAASCIIstring(String value) {
        return new HLAASCIIstring(value);
    }

    public HLAunicodeString createHLAunicodeString() {
        return new HLAunicodeString("");
    }

    public HLAunicodeString createHLAunicodeString(String value) {
        return new HLAunicodeString(value);
    }

    public HLAoctet createHLAoctet() {
        return new HLAoctet(0);
    }

    public HLAoctet createHLAoctet(int value) {
        return new HLAoctet(value);
    }

    public HLAopaqueData createHLAopaqueData() {
        return new HLAopaqueData(new byte[0]);
    }

    public HLAopaqueData createHLAopaqueData(byte[] value) {
        return new HLAopaqueData(value);
    }

    public HLAfixedRecord createHLAfixedRecord() {
        return new HLAfixedRecord();
    }

    public HLAfixedArray createHLAfixedArray(DataElement... elements) {
        return new HLAfixedArray(elements);
    }

    public HLAvariableArray createHLAvariableArray(DataElement... elements) {
        return new HLAvariableArray(elements);
    }
}
