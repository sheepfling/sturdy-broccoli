package hla.rti1516e;
public class HLAinteger64Time implements LogicalTime, Comparable<HLAinteger64Time> {
    private final long value;
    public HLAinteger64Time(long value) { this.value = value; }
    public long getValue() { return value; }
    public int compareTo(HLAinteger64Time other) { return Long.compare(value, other.value); }
    public String toString() { return "HLAinteger64Time(" + value + ")"; }
}
