package hla.rti1516e;
import java.io.Serializable;
public abstract class HandleBase implements Serializable {
    private final int value;
    protected HandleBase(int value) { this.value = value; }
    public int intValue() { return value; }
    public int hashCode() { return getClass().hashCode() * 31 + value; }
    public boolean equals(Object other) { return other != null && other.getClass() == getClass() && ((HandleBase) other).value == value; }
    public String toString() { return getClass().getSimpleName() + "(" + value + ")"; }
}
