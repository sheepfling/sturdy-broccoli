package hla.rti1516e;
public class HLAinteger64Interval implements LogicalTimeInterval {
    private final long value;
    public HLAinteger64Interval(long value) { this.value = value; }
    public long getValue() { return value; }
    public String toString() { return "HLAinteger64Interval(" + value + ")"; }
}
