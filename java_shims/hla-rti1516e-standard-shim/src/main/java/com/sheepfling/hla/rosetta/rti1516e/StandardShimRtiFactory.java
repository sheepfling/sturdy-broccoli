package com.sheepfling.hla.rosetta.rti1516e;

import hla.rti1516e.RTIambassador;
import hla.rti1516e.RtiFactory;
import hla.rti1516e.encoding.EncoderFactory;
import hla.rti1516e.exceptions.RTIinternalError;

public final class StandardShimRtiFactory implements RtiFactory {
    public static final String FACTORY_NAME = "HLA-X Java 2010 Standard Shim";
    public static final String FACTORY_VERSION = "0.13.0-rosetta-java-2010";

    public RTIambassador getRtiAmbassador() throws RTIinternalError {
        return new StandardShimRTIambassador();
    }

    public EncoderFactory getEncoderFactory() throws RTIinternalError {
        throw new RTIinternalError("HLA-X Java 2010 Standard Shim does not implement EncoderFactory yet");
    }

    public String rtiName() {
        return FACTORY_NAME;
    }

    public String rtiVersion() {
        return FACTORY_VERSION;
    }
}
