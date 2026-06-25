package hla.rti1516e;

import hla.rti1516e.encoding.EncoderFactory;

public class RtiFactory {
    public RTIambassador getRtiAmbassador() { return new RTIambassador(); }
    public EncoderFactory getEncoderFactory() { return new EncoderFactory(); }
    public String rtiName() { return "HLA 1516e Java shim"; }
    public String rtiVersion() { return "0.6"; }
}
