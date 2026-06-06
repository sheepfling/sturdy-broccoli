package hla.rti1516e;
public class RtiFactory {
    public RTIambassador getRtiAmbassador() { return new RTIambassador(); }
    public String rtiName() { return "HLA 1516e Java shim"; }
    public String rtiVersion() { return "0.5"; }
}
